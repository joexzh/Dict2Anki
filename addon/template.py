from __future__ import annotations

import logging
import typing as T
from abc import ABC, abstractmethod

import aqt.utils
from anki.errors import CardTypeError
from aqt import QAbstractButton, QEvent, QObject, QRadioButton, Qt, QWidget

from . import _typing as _T
from . import noteManager
from .preview import PreviewDialog
from .UIForm.template import Ui_tplForm

logger = logging.getLogger('dict2Anki.template')


def add_modified_hint(text: str) -> str:
    if not text.endswith('*'):
        text = text + '*'
    return text


def remove_modified_hint(text: str) -> str:
    if text.endswith('*'):
        text = text[0:-1]
    return text


def create_disk_models(db_model: DbModel, id_after: int = 0) -> list[DiskModel]:
    tpls_folder = noteManager.templates_folder()
    models = []
    for tpl_d in tpls_folder.iterdir():
        if not tpl_d.is_dir():
            continue
        try:
            name = tpl_d.name
            # ensure model.load_template() no error
            front, back, css = noteManager.template_from_folder(tpls_folder, name)
            id_after += 1
            model = DiskModel(id_after, name, db_model)
            model._front = front
            model._back = back
            model._css = css
            model._cached = True
            models.append(model)
        except FileNotFoundError as e:
            logger.warning(str(e))

    return models


class Template(QWidget, Ui_tplForm):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._previewer: T.Union[None, PreviewDialog] = None
        self.setupUi(self)
        self.plainEditText.installEventFilter(self)

        self._db_model = DbModel(0)

        self.tplButtonGroup.setId(self.dbTplButton, self._db_model.id())
        self._tpl_id_model_map: dict[int, Model] = {
            self._db_model.id(): self._db_model,
        }

        self.partButtonGroup.setId(self.frontButton, 0)
        self.partButtonGroup.setId(self.backButton, 1)
        self.partButtonGroup.setId(self.cssButton, 2)
        self._part_id_name_map: dict[int, str] = {0: 'front', 1: 'back', 2: 'css'}

        index = self.tplSetLayout.indexOf(self.dbTplButton)
        for model in create_disk_models(self._db_model):
            self._tpl_id_model_map[model.id()] = model
            # create radio button for disk template model
            index += 1
            btn = QRadioButton(model.name(), self)
            self.tplSetLayout.insertWidget(index, btn)
            self.tplButtonGroup.addButton(btn, model.id())

        self._listen_ui_events()
        self._listen_model_events()
        self._on_tpl_id_change(0)

    def eventFilter(self, a0: T.Optional[QObject], a1: T.Optional[QEvent]) -> bool:
        """Listen to plainEditText focus out event for text change. It's a
        replacement to textChanged for better performance.
        """
        if (
            a0 == self.plainEditText
            and a1
            and a1.type() == QEvent.Type.FocusOut
            and self.selected_model() == self._db_model
        ):
            self._on_edit_text_focus_out()
        return super().eventFilter(a0, a1)

    def _listen_ui_events(self):
        self.tplButtonGroup.idPressed.connect(self._on_tplbtn_id_press)  # before click, id not yet changed
        self.tplButtonGroup.idClicked.connect(self._on_tpl_id_change)
        self.partButtonGroup.idPressed.connect(self._on_partbtn_id_press)  # before click, id not yet changed
        self.partButtonGroup.idClicked.connect(self._on_part_id_change)
        self.saveButton.clicked.connect(self.save)
        self.previewButton.clicked.connect(self.preview)

    def _listen_model_events(self):
        def front_modified(model):
            self._update_ui_when_part_modified('front', model)

        def back_modified(model):
            self._update_ui_when_part_modified('back', model)

        def css_modified(model):
            self._update_ui_when_part_modified('css', model)

        self._db_model.listen('front_modified', front_modified)
        self._db_model.listen('back_modified', back_modified)
        self._db_model.listen('css_modified', css_modified)

    def _on_edit_text_focus_out(self):
        self._update_model_part()
        self._update_previewer()

    def _update_model_part(self):
        part = self.selected_part()
        self.selected_model().set_part(part, self.plainEditText.toPlainText())

    def _update_ui_when_part_modified(self, part: str, model: Model):
        if model == self.selected_model():
            self._update_ui_part_modified_hint(part, model.get_part_modified(part))
        # update tpl button regardless of selection
        self._update_ui_tpl_modified_hint(model)

    def _on_tplbtn_id_press(self, _id: int):
        self._update_model_part()

    def _on_tpl_id_change(self, id: int):
        "after tpl button change selection"
        model: Model = self._tpl_id_model_map[id]
        part_id = self.partButtonGroup.checkedId()

        self.plainEditText.setReadOnly(model.readonly())
        self._set_ui_edit_text(part_id, model)
        self._update_ui_modified_hint(model)
        self._update_previewer()

    def _on_partbtn_id_press(self, _id: int):
        self._update_model_part()

    def _on_part_id_change(self, id: int):
        "after part button change selection"
        model = self.selected_model()
        self._set_ui_edit_text(id, model)

    def _set_ui_edit_text(self, part_id: int, model: Model):
        part = self._part_id_name_map[part_id]
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
        return self._tpl_id_model_map[self.tplButtonGroup.checkedId()]

    def selected_part(self) -> str:
        return self._part_id_name_map[self.partButtonGroup.checkedId()]

    def save(self):
        self._update_model_part()
        try:
            self.selected_model().save()
            aqt.utils.tooltip('保存成功', parent=self)
        except CardTypeError as e:
            logger.exception('Fail to save card!')
            aqt.utils.show_critical(str(e), parent=self, textFormat=Qt.TextFormat.AutoText)

    def preview(self):
        if self._previewer is None:
            model = self.selected_model()
            note = noteManager.create_sample_note(model.get_front(), model.get_back(), model.get_css())
            self._previewer = PreviewDialog(note, self)
            self._previewer.finished.connect(self._on_previewer_close)
            self._previewer.show()
        self._previewer.raise_()

    def _on_previewer_close(self, _r: int):
        self._previewer = None

    def _update_previewer(self):
        if self._previewer is None:
            return
        model = self.selected_model()
        self._previewer.update_content(model.get_front(), model.get_back(), model.get_css())


class Model(ABC, _T.ListenableModel):
    """
    Emits {part}_modified event with parameter `self`.
    {part} can be either "front", "back" or "css".
    """

    @abstractmethod
    def __init__(self, id: int):
        super().__init__()
        self._id = id
        self._front = ''
        self._back = ''
        self._css = ''
        self._front_modified = False
        self._back_modified = False
        self._css_modified = False
        self._cached = False

    def id(self) -> int:
        "Unique id across all models"
        return self._id

    @abstractmethod
    def readonly(self) -> bool:
        pass

    @abstractmethod
    def load_template(self):
        pass

    @abstractmethod
    def save(self):
        pass

    def reset(self, front: str, back: str, css: str):
        self._front = front
        self._back = back
        self._css = css
        self._cached = True
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
        if not self._cached:
            self.load_template()
        return getattr(self, f'_{part}')

    def get_front(self) -> str:
        return self.get_part('front')

    def get_back(self) -> str:
        return self.get_part('back')

    def get_css(self) -> str:
        return self.get_part('css')

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

    def set_front(self, val: str):
        self.set_part('front', val)

    def set_back(self, val: str):
        self.set_part('back', val)

    def set_css(self, val: str):
        self.set_part('css', val)

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


class DbModel(Model):
    "model for template from database"

    def __init__(self, id: int):
        super().__init__(id)

    def readonly(self) -> bool:
        return False

    def load_template(self):
        front, back, css = noteManager.template_from_db()
        self._front = front
        self._back = back
        self._css = css
        self._cached = True

    def save(self):
        noteManager.update_db_model_template(self.get_front(), self.get_back(), self.get_css())
        self.set_part_modified('front', False)
        self.set_part_modified('back', False)
        self.set_part_modified('css', False)


class DiskModel(Model):
    "model for template from disk"

    def __init__(self, id: int, name: str, db_model: Model):
        super().__init__(id)
        self._name = name
        self._db_model = db_model

    def name(self) -> str:
        return self._name

    def readonly(self) -> bool:
        return True

    def load_template(self):
        front, back, css = noteManager.template_from_folder(noteManager.templates_folder(), self._name)
        self._front = front
        self._back = back
        self._css = css
        self._cached = True

    def save(self):
        noteManager.update_db_model_template(self.get_front(), self.get_back(), self.get_css())
        self._db_model.reset(self.get_front(), self.get_back(), self.get_css())
