from __future__ import annotations

import typing as T

import aqt
import aqt.utils
from aqt import QComboBox, QDialog, QIcon, QLineEdit, Qt

from . import _typing as _T
from . import adv_conf, conf_model, dictionary, queryApi
from . import constants as C
from .adv_conf_dialog import AdvConfDialog

if T.TYPE_CHECKING:
    from .addonWindow import Windows


def set_api_combobox_tooltip(combobox: QComboBox, api_name: str):
    api = queryApi.apis.get(api_name)
    tooltip_text = api.desc if api else ''
    combobox.setToolTip(tooltip_text)


class ConfCtl:
    @staticmethod
    def read() -> _T.ConfigMap:
        if config := aqt.mw.addonManager.getConfig(__name__):
            return config  # type: ignore
        else:
            raise FileNotFoundError('missing config file')

    @staticmethod
    def write(conf: conf_model.Conf):
        if conf.is_dirty():
            aqt.mw.addonManager.writeConfig(__name__, conf.get_saving_map())  # type: ignore

    @staticmethod
    def init_ui(w: Windows, conf: conf_model.Conf):
        """Should be called only once!"""

        ConfCtl.init_adv_conf_ui(w, conf)

        w.deckComboBox.setCurrentText(conf.deck)
        w.dictionaryComboBox.setCurrentText(conf.selected_dict)
        w.currentDictionaryLabel.setText(f'当前选择词典: {w.dictionaryComboBox.currentText()}')
        w.apiComboBox.setCurrentText(conf.selected_api)
        set_api_combobox_tooltip(w.apiComboBox, conf.selected_api)
        w.cookieLineEdit.setText(conf.current_cookies)
        w.definitionCheckBox.setChecked(conf.definition)
        w.imageCheckBox.setChecked(conf.image)
        w.sentenceCheckBox.setChecked(conf.sentence)
        w.phraseCheckBox.setChecked(conf.phrase)
        w.AmEPhoneticCheckBox.setChecked(conf.ame_phonetic)
        w.BrEPhoneticCheckBox.setChecked(conf.bre_phonetic)
        w.BrEPronRadioButton.setChecked(conf.bre_pron)
        w.AmEPronRadioButton.setChecked(conf.ame_pron)
        w.noPronRadioButton.setChecked(conf.no_pron)
        w.congestSpinBox.setValue(conf.congest)
        w.uaLineEdit.setText(conf.user_agent)
        undoicon = QIcon.fromTheme(QIcon.ThemeIcon.EditUndo)
        uaAction = w.uaLineEdit.addAction(undoicon, aqt.QLineEdit.ActionPosition.TrailingPosition)
        uaAction.setToolTip('回到默认')  # type: ignore
        uaAction.triggered.connect(lambda: w.uaLineEdit.setText(C.USER_AGENT))  # type: ignore

        ConfCtl.register_events(w, conf)

    @staticmethod
    def init_adv_conf_ui(w: Windows, conf: conf_model.Conf):
        if conf.advanced_enabled and conf.advanced_enable_user_modules:
            queryApi.load_usr_mod()
            dictionary.load_usr_mod()

        w.dictionaryComboBox.addItems((k for k in dictionary.dictionaries))
        i = 0
        for k, v in queryApi.apis.items():
            w.apiComboBox.addItem(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout), k)
            w.apiComboBox.setItemData(i, v.desc, Qt.ItemDataRole.ToolTipRole)
            i += 1

        if (dictionary.dictionaries.get(dict_ := conf.selected_dict)) is None:
            aqt.utils.show_info(f'无法加载模块[{dict_}]，回滚到默认值[{dictionary.default_dict.name}]', parent=w)
            conf.selected_dict = dictionary.default_dict.name

        if conf.advanced_enabled is False:
            if (queryApi.apis.get(api := conf.selected_api)) is None:
                aqt.utils.show_info(f'无法加载模块[{api}]，回滚到默认值[{queryApi.default_api.name}]', parent=w)
                conf.selected_api = queryApi.default_api.name
        else:
            # warn for any invalid API in user config
            _ast_dict, errmsg = adv_conf.ensure_ast_dict_errmsg_for_ui(conf.get_ast_dict())
            if errmsg:
                aqt.utils.show_warning(errmsg)

        w.advEnableCB.setChecked(conf.advanced_enabled)
        w.advEnableUserModCB.setChecked(conf.advanced_enable_user_modules)
        w.advDefinitionLineEdit.setText(conf.advanced_definition)
        w.advPhraseLineEdit.setText(conf.advanced_phrase)
        w.advSentenceLineEdit.setText(conf.advanced_sentence)
        w.advImageLineEdit.setText(conf.advanced_image)
        w.advEnPhoneticLineEdit.setText(conf.advanced_BrEPhonetic)
        w.advUsPhoneticLineEdit.setText(conf.advanced_AmEPhonetic)
        w.advEnPronLineEdit.setText(conf.advanced_BrEPron)
        w.advUsPronLineEdit.setText(conf.advanced_AmEPron)

        ConfCtl.adv_conf_ui_set_enabled(w, conf.advanced_enabled)

    @staticmethod
    def old_conf_group_set_enabled(w: Windows, enabled: bool):
        w.oldConfigGroupBox.setEnabled(enabled)

    @staticmethod
    def adv_conf_widgets_set_enabled(w: Windows, enabled: bool):
        w.advEnableUserModCB.setEnabled(enabled)

        w.advDefinitionLabel.setEnabled(enabled)
        w.advDefinitionLineEdit.setEnabled(enabled)

        w.advPhraseLabel.setEnabled(enabled)
        w.advPhraseLineEdit.setEnabled(enabled)

        w.advSentenceLabel.setEnabled(enabled)
        w.advSentenceLineEdit.setEnabled(enabled)

        w.advImageLabel.setEnabled(enabled)
        w.advImageLineEdit.setEnabled(enabled)

        w.advEnPhoneticLabel.setEnabled(enabled)
        w.advEnPhoneticLineEdit.setEnabled(enabled)

        w.advUsPhoneticLabel.setEnabled(enabled)
        w.advUsPhoneticLineEdit.setEnabled(enabled)

        w.advEnPronLabel.setEnabled(enabled)
        w.advEnPronLineEdit.setEnabled(enabled)

        w.advUsPronLabel.setEnabled(enabled)
        w.advUsPronLineEdit.setEnabled(enabled)

    @staticmethod
    def adv_conf_ui_set_enabled(w: Windows, enabled: bool):
        if enabled:
            ConfCtl.old_conf_group_set_enabled(w, False)
            ConfCtl.adv_conf_widgets_set_enabled(w, True)
        else:
            ConfCtl.adv_conf_widgets_set_enabled(w, False)
            ConfCtl.old_conf_group_set_enabled(w, True)

    @staticmethod
    def register_adv_conf_events(w: Windows, conf: conf_model.Conf):

        def _on_adv_enabled_cb_change(state):
            checked = state == Qt.CheckState.Checked.value
            conf.advanced_enabled = checked
            ConfCtl.adv_conf_ui_set_enabled(w, checked)

        def _on_adv_enable_user_mod_cb_change(state):
            conf.advanced_enable_user_modules = state == Qt.CheckState.Checked.value
            aqt.utils.tooltip('重启 Anki 后生效', parent=w)

        def _on_adv_line_edit_click(line_edit: QLineEdit):
            text = line_edit.text()
            dialog = AdvConfDialog(text, w)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                line_edit.setText(dialog.get_text())

        def _on_adv_definition_line_edit_change(val: str):
            conf.advanced_definition = val

        def _on_adv_phrase_line_edit_change(val: str):
            conf.advanced_phrase = val

        def _on_adv_sentence_line_edit_change(val: str):
            conf.advanced_sentence = val

        def _on_adv_image_line_edit_change(val: str):
            conf.advanced_image = val

        def _on_adv_en_phonetic_line_edit_change(val: str):
            conf.advanced_BrEPhonetic = val

        def _on_adv_us_phonetic_line_edit_change(val: str):
            conf.advanced_AmEPhonetic = val

        def _on_adv_en_pron_line_edit_change(val: str):
            conf.advanced_BrEPron = val

        def _on_adv_us_pron_line_edit_change(val: str):
            conf.advanced_AmEPron = val

        w.advEnableCB.stateChanged.connect(_on_adv_enabled_cb_change)
        w.advEnableUserModCB.stateChanged.connect(_on_adv_enable_user_mod_cb_change)

        w.advDefinitionLineEdit.clicked.connect(_on_adv_line_edit_click)
        w.advDefinitionLineEdit.textChanged.connect(_on_adv_definition_line_edit_change)

        w.advPhraseLineEdit.clicked.connect(_on_adv_line_edit_click)
        w.advPhraseLineEdit.textChanged.connect(_on_adv_phrase_line_edit_change)

        w.advSentenceLineEdit.clicked.connect(_on_adv_line_edit_click)
        w.advSentenceLineEdit.textChanged.connect(_on_adv_sentence_line_edit_change)

        w.advImageLineEdit.clicked.connect(_on_adv_line_edit_click)
        w.advImageLineEdit.textChanged.connect(_on_adv_image_line_edit_change)

        w.advEnPhoneticLineEdit.clicked.connect(_on_adv_line_edit_click)
        w.advEnPhoneticLineEdit.textChanged.connect(_on_adv_en_phonetic_line_edit_change)

        w.advUsPhoneticLineEdit.clicked.connect(_on_adv_line_edit_click)
        w.advUsPhoneticLineEdit.textChanged.connect(_on_adv_us_phonetic_line_edit_change)

        w.advEnPronLineEdit.clicked.connect(_on_adv_line_edit_click)
        w.advEnPronLineEdit.textChanged.connect(_on_adv_en_pron_line_edit_change)

        w.advUsPronLineEdit.clicked.connect(_on_adv_line_edit_click)
        w.advUsPronLineEdit.textChanged.connect(_on_adv_us_pron_line_edit_change)

    @staticmethod
    def register_events(w: Windows, conf: conf_model.Conf):
        def _on_deck_combobox_change(text):
            conf.deck = text

        def _on_dict_combobox_change(text):
            conf.selected_dict = text
            w.currentDictionaryLabel.setText(f'当前选择词典: {w.dictionaryComboBox.currentText()}')
            w.cookieLineEdit.blockSignals(True)
            w.cookieLineEdit.setText(conf.current_cookies)
            w.cookieLineEdit.blockSignals(False)

        def _on_api_combobox_change(text):
            conf.selected_api = text
            set_api_combobox_tooltip(w.apiComboBox, text)

        def _on_cookie_line_edit_change(text):
            conf.current_cookies = text

        def _on_definition_cb_change(state: int):
            conf.definition = state == Qt.CheckState.Checked.value

        def _on_sentence_cb_change(state):
            conf.sentence = state == Qt.CheckState.Checked.value

        def _on_phrase_cb_change(state):
            conf.phrase = state == Qt.CheckState.Checked.value

        def _on_image_cb_change(state):
            conf.image = state == Qt.CheckState.Checked.value

        def _on_ame_phonetic_cb_change(state):
            conf.ame_phonetic = state == Qt.CheckState.Checked.value

        def _on_bre_phonetic_cb_change(state):
            conf.bre_phonetic = state == Qt.CheckState.Checked.value

        def _on_ame_pron_radio_toggled():
            if w.AmEPronRadioButton.isChecked():
                conf.ame_pron = True

        def _on_bre_pron_radio_toggled():
            if w.BrEPronRadioButton.isChecked():
                conf.bre_pron = True

        def _on_no_pron_radio_toggled():
            if w.noPronRadioButton.isChecked():
                conf.no_pron = True

        def _on_congest_spinbox_change(value: int):
            conf.congest = value

        def _on_ua_line_edit_changed(text):
            conf.user_agent = text

        # register events

        w.deckComboBox.currentTextChanged.connect(_on_deck_combobox_change)
        w.dictionaryComboBox.currentTextChanged.connect(_on_dict_combobox_change)
        w.apiComboBox.currentTextChanged.connect(_on_api_combobox_change)
        w.cookieLineEdit.textChanged.connect(_on_cookie_line_edit_change)
        w.definitionCheckBox.stateChanged.connect(_on_definition_cb_change)
        w.sentenceCheckBox.stateChanged.connect(_on_sentence_cb_change)
        w.phraseCheckBox.stateChanged.connect(_on_phrase_cb_change)
        w.imageCheckBox.stateChanged.connect(_on_image_cb_change)
        w.AmEPhoneticCheckBox.stateChanged.connect(_on_ame_phonetic_cb_change)
        w.BrEPhoneticCheckBox.stateChanged.connect(_on_bre_phonetic_cb_change)
        w.AmEPronRadioButton.toggled.connect(_on_ame_pron_radio_toggled)
        w.BrEPronRadioButton.toggled.connect(_on_bre_pron_radio_toggled)
        w.noPronRadioButton.toggled.connect(_on_no_pron_radio_toggled)
        w.congestSpinBox.valueChanged.connect(_on_congest_spinbox_change)
        w.uaLineEdit.textChanged.connect(_on_ua_line_edit_changed)

        def update_cookies_line_edit(val: str):
            w.cookieLineEdit.blockSignals(True)
            w.cookieLineEdit.setText(val)
            w.cookieLineEdit.blockSignals(False)

        # register model events. For now only `current_cookies` is actively modified by code (not by user)
        conf.listen('current_cookies', update_cookies_line_edit)

        ConfCtl.register_adv_conf_events(w, conf)
