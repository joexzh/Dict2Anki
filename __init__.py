try:
    from aqt import mw, QAction
    assert mw is not None
    from .addon.entryPoint import EntryPoint
    from .addon.constants import ADDON_FULL_NAME

    def showWindow():
        ep = EntryPoint()
        ep.windows.exec()

    action = QAction(ADDON_FULL_NAME, mw)
    action.triggered.connect(showWindow)
    mw.form.menuTools.addAction(action)

except (ImportError, AssertionError):
    import os

    if os.environ.get("DEVDICT2ANKI") or __name__ == "__main__":
        from PyQt6.QtWidgets import QApplication
        from .addon.addonWindow import Windows
        import sys

        app = QApplication(sys.argv)
        window = Windows()
        window.show()
        sys.exit(app.exec())
