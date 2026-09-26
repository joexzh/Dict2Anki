import typing as T

from aqt import QLineEdit, QMouseEvent, pyqtSignal


class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self._on_text_change)

    def mousePressEvent(self, a0: T.Optional[QMouseEvent]) -> None:
        self.clicked.emit(self)
        return super().mousePressEvent(a0)

    def _on_text_change(self, text: str):
        self.setToolTip(text)
