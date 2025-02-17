try:
    from aqt import mw, QAction
    from .addon.entryPoint import EntryPoint
    from .addon.constants import ADDON_FULL_NAME

    def showWindow():
        ep = EntryPoint()
        ep.windows.exec()

    action = QAction(ADDON_FULL_NAME, mw)
    action.triggered.connect(showWindow)
    mw.form.menuTools.addAction(action)

except ImportError:
    import os
    from PyQt6.QtWidgets import QApplication
    from addon.addonWindow import Windows
    import sys

    if os.environ.get("DEVDICT2ANKI"):
        app = QApplication(sys.argv)
        window = Windows()
        window.show()
        sys.exit(app.exec())
