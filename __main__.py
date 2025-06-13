if __name__ == "__main__":
    import sys

    import pytest
    from PyQt6.QtWidgets import QApplication

    from .addon.addonWindow import Windows
    from .test import mock_helper

    mp = pytest.MonkeyPatch()
    mock_helper.mock_aqt_mw(mp)
    mock_helper.mock_aqt_utils(mp)

    app = QApplication(sys.argv)
    window = Windows()
    window.show()
    sys.exit(app.exec())