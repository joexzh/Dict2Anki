import typing as T

from aqt import QDialog, QIcon, QLabel, QObject, QPushButton, Qt, QVBoxLayout, QWidget

from . import queryApi
from ._typing import AbstractQueryAPI
from .UIForm import adv_conf_dialog


def make_api_btn(api: type[AbstractQueryAPI], parent: T.Optional[QWidget]) -> QPushButton:
    icon = QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout)
    btn = QPushButton(icon=icon, text=f'api:"{api.name}"', parent=parent)
    btn.setStyleSheet("""
        QPushButton {
            text-align: left;
            padding-left: 0px;
            padding-right: 0px;
        }
    """)
    btn.setToolTip(api.desc)
    return btn


class AdvConfDialog(QDialog, adv_conf_dialog.Ui_Dialog):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('构造高级设置')
        self.lineEdit.setText(text)
        self.descBtn.clicked.connect(self._on_desc_btn_click)

        for _k, v in queryApi.apis.items():
            # follow the UI_Dialog code, set widgetContents as parent
            btn = make_api_btn(v, self.apiScrollAreaWidgetContents)
            btn.clicked.connect(lambda checked, btn=btn: self._on_api_flag_btn_click(btn))
            self.apiScrollLayout.addWidget(btn)

        for btn in self.flagScrollAreaWidgetContents.findChildren(QPushButton):
            btn.clicked.connect(lambda checked, btn=btn: self._on_api_flag_btn_click(btn))

    def _on_api_flag_btn_click(self, btn: QPushButton):
        old_text = self.lineEdit.text()
        if old_text:
            new_text = f'{self.lineEdit.text()} | {btn.text()}'
        else:
            new_text = btn.text()
        self.lineEdit.setText(new_text)

    def _on_desc_btn_click(self):
        dialog = QDialog(self)
        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        dialog.setLayout(layout)
        label = QLabel(dialog)
        label.setMinimumWidth(400)
        label.setWordWrap(True)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        label.setTextFormat(Qt.TextFormat.MarkdownText)
        label.setOpenExternalLinks(True)
        text = """支持每个字段查询不同的 API。

api 或 flag（标记笔记）以操作符 `|`（OR）分隔，从左到右执行，成功则停止，失败则继续，直到成功为止。注意，flag 视作失败，一般用于重要字段并且应放在最后。在一条笔记中（一个单词），多个字段触发的 flag 会被最后一次执行的 flag 覆盖。

空值代表清空字段。

例： `api:"funny Vocabulary.com API" | api:"有道 API" | flag:1`"""
        label.setText(text)
        layout.addWidget(label)
        dialog.exec()

    def get_text(self):
        return self.lineEdit.text()
