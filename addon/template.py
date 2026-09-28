from __future__ import annotations

from abc import ABC, abstractmethod

import aqt.utils
from aqt import QAbstractButton, QWidget

from . import _typing as _T
from . import noteManager
from .UIForm.template import Ui_tplForm


def add_modified_hint(text: str) -> str:
    if not text.endswith('*'):
        text = text + '*'
    return text


def remove_modified_hint(text: str) -> str:
    if text.endswith('*'):
        text = text[0:-1]
    return text


def save(front: str, back: str, css: str):
    # TODO
    pass


class Template(QWidget, Ui_tplForm):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.user_model = UserModel()
        self.default_model = DefaultModel(self.user_model)

        self.tplButtonGroup.setId(self.userTplButton, self.user_model.id())
        self.tplButtonGroup.setId(self.defaultTplButton, self.default_model.id())

        self.partButtonGroup.setId(self.frontButton, 0)
        self.partButtonGroup.setId(self.backButton, 1)
        self.partButtonGroup.setId(self.cssButton, 2)

        self.tpl_id_model_map: dict[int, Model] = {
            self.user_model.id(): self.user_model,
            self.default_model.id(): self.default_model,
        }
        self.part_id_name_map: dict[int, str] = {0: 'front', 1: 'back', 2: 'css'}

        self._listen_events()
        self._on_tpl_id_change(0)

    def _listen_events(self):
        self._listen_ui_events()
        self._listen_model_events()

    def _listen_ui_events(self):
        self.tplButtonGroup.idClicked.connect(self._on_tpl_id_change)
        self.partButtonGroup.idClicked.connect(self._on_part_id_change)
        self.saveButton.clicked.connect(self.save)
        self.previewButton.clicked.connect(self.preview)
        self.plainEditText.textChanged.connect(self._on_edit_text_change)

    def _listen_model_events(self):
        def front_modified(model):
            self._update_ui_when_part_modified('front', model)

        def back_modified(model):
            self._update_ui_when_part_modified('back', model)

        def css_modified(model):
            self._update_ui_when_part_modified('css', model)

        self.user_model.listen('front_modified', front_modified)
        self.user_model.listen('back_modified', back_modified)
        self.user_model.listen('css_modified', css_modified)

    def _on_edit_text_change(self):
        part = self.part_id_name_map[self.partButtonGroup.checkedId()]
        self.selected_model().set_part(part, self.plainEditText.toPlainText())

    def _update_ui_when_part_modified(self, part: str, model: Model):
        if model == self.selected_model():
            self._update_ui_part_modified_hint(part, model.get_part_modified(part))
        # update tpl button regardless of selection
        self._update_ui_tpl_modified_hint(model)

    def _on_tpl_id_change(self, id: int):
        "after tpl button change selection"
        model: Model = self.tpl_id_model_map[id]
        part_id = self.partButtonGroup.checkedId()

        self.plainEditText.setReadOnly(model.readonly())
        self._update_ui_edit_text(part_id, model)
        self._update_ui_modified_hint(model)

    def _on_part_id_change(self, id: int):
        "after part button change selection"
        model = self.selected_model()
        self._update_ui_edit_text(id, model)

    def _update_ui_edit_text(self, part_id: int, model: Model):
        part = self.part_id_name_map[part_id]
        self.plainEditText.blockSignals(True)
        self.plainEditText.setPlainText(model.get_part(part))
        self.plainEditText.blockSignals(False)

    def _update_ui_modified_hint(self, model: Model):
        "update tpl and part buttons"
        for part in ['front', 'back', 'css']:
            self._update_ui_part_modified_hint(part, model.get_part_modified(part))

        self._update_ui_tpl_modified_hint(model)

    def _update_ui_tpl_modified_hint(self, model: Model):
        "update tpl button"
        btn = self.tplButtonGroup.button(model.id())
        if not btn:
            return
        self._update_ui_btn_modified_hint(btn, model.any_modified())

    def _update_ui_part_modified_hint(self, part: str, is_modified: bool):
        "update part button"
        part_btn = getattr(self, f'{part}Button')
        self._update_ui_btn_modified_hint(part_btn, is_modified)

    def _update_ui_btn_modified_hint(self, btn: QAbstractButton, is_modified: bool):
        if is_modified:
            btn.setText(add_modified_hint(btn.text()))
        else:
            btn.setText(remove_modified_hint(btn.text()))

    def selected_model(self) -> Model:
        return self.tpl_id_model_map[self.tplButtonGroup.checkedId()]

    def save(self):
        self.selected_model().save()
        aqt.utils.tooltip('保存成功', parent=self)

    def preview(self):
        # TODO
        pass


class Model(ABC, _T.ListenableModel):
    """
    Emits {part}_modified event with parameter `self`.
    {part} can be either "front", "back" or "css".
    """

    @abstractmethod
    def __init__(self):
        super().__init__()
        self._front = ''
        self._back = ''
        self._css = ''
        self._front_modified = False
        self._back_modified = False
        self._css_modified = False
        self._front_cached = False
        self._back_cached = False
        self._css_cached = False

    @abstractmethod
    def id(self) -> int:
        "Unique id across all models"
        pass

    @abstractmethod
    def readonly(self) -> bool:
        pass

    @abstractmethod
    def load_front(self) -> str:
        pass

    @abstractmethod
    def load_back(self) -> str:
        pass

    @abstractmethod
    def load_css(self) -> str:
        pass

    @abstractmethod
    def save(self):
        pass

    def reset(self, front: str, back: str, css: str):
        self._front = front
        self._back = back
        self._css = css
        self._front_cached = True
        self._back_cached = True
        self._css_cached = True
        self.set_part_modified('front', False)
        self.set_part_modified('back', False)
        self.set_part_modified('css', False)

    def reset_default(self):
        pass

    def get_part(self, part: str) -> str:
        """get front/back/css

        Args:
            part: front, back or css
        """
        cached = getattr(self, f'_{part}_cached')
        if not cached:
            load_fn = getattr(self, f'load_{part}')
            load_fn()
            setattr(self, f'_{part}_cached', True)
        return getattr(self, f'_{part}')

    def set_part(self, part: str, val: str):
        """Set front/back/css

        Args:
            part: front, back or css
        """
        attr_name = f'_{part}'
        if getattr(self, attr_name) == val:
            return
        setattr(self, attr_name, val)
        self.set_part_modified(part, True)

    def get_part_modified(self, part: str) -> bool:
        """Get {front,back,css}_modified

        Args:
            part: front, back or css"""
        return getattr(self, f'_{part}_modified')

    def set_part_modified(self, part: str, val: bool):
        """Set {front,back,css}_modified.
        Emits {part}_modified event with parameter `self`.

        Args:
            part: front, back or css"""

        attr_name = f'_{part}_modified'
        if getattr(self, attr_name) == val:
            return
        setattr(self, attr_name, val)
        self._notify(f'{part}_modified', self)

    def any_modified(self) -> bool:
        return self._front_modified or self._back_modified or self._css_modified


class UserModel(Model):
    def __init__(self):
        super().__init__()

    def id(self) -> int:
        return 0

    def readonly(self) -> bool:
        return False

    def load_front(self) -> str:
        # TODO
        self._front = 'user model front'
        return self._front

    def load_back(self) -> str:
        # TODO
        self._back = 'user model back'
        return self._back

    def load_css(self) -> str:
        # TODO
        self._css = 'user model css'
        return self._css

    def save(self):
        save(self.get_part('front'), self.get_part('back'), self.get_part('css'))
        self.set_part_modified('front', False)
        self.set_part_modified('back', False)
        self.set_part_modified('css', False)


class DefaultModel(Model):
    def __init__(self, user_model: Model):
        super().__init__()
        self.user_model = user_model

    def id(self) -> int:
        return 1

    def readonly(self) -> bool:
        return True

    def load_front(self) -> str:
        # TODO
        self._front = 'default model front'
        return self._front

    def load_back(self) -> str:
        # TODO
        self._back = 'default model back'
        return self._back

    def load_css(self) -> str:
        # TODO
        self._css = 'default model css'
        return self._css

    def save(self):
        save(self.get_part('front'), self.get_part('back'), self.get_part('css'))
        self.user_model.reset(self.get_part('front'), self.get_part('back'), self.get_part('css'))
