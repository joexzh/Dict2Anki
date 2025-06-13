try:
    import aqt
    assert aqt.mw is not None
    from .addon.entryPoint import EntryPoint
    from .addon.constants import ADDON_FULL_NAME

    def showWindow():
        ep = EntryPoint()
        ep.windows.exec()

    action = aqt.QAction(ADDON_FULL_NAME, aqt.mw)
    action.triggered.connect(showWindow)
    aqt.mw.form.menuTools.addAction(action)

except AssertionError:
    print("apt.mw is None")
