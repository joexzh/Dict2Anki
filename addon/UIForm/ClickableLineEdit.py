import typing as T

from aqt import QLineEdit, QMouseEvent, pyqtSignal


class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def mousePressEvent(self, a0: T.Optional[QMouseEvent]) -> None:
        self.clicked.emit(self)
        return super().mousePressEvent(a0)
