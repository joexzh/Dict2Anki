try:
    import aqt

    assert aqt.mw is not None

    from .addon import addonWindow
    from .addon.constants import ADDON_FULL_NAME

    if (addon_name := aqt.addons.AddonManager.addon_from_module(__name__)) != '107281012':
        # '107281012' is addon code on ankiweb.net
        ADDON_FULL_NAME = addon_name

    w: addonWindow.Windows = None

    def showWindow():

        def on_finish(_result):
            global w
            w = None

        global w

        if w:
            w.raise_()
            w.activateWindow()
            return

        w = addonWindow.Windows(aqt.mw)
        w.finished.connect(on_finish)
        # change from exec() to show() to prevent blocking anki main window
        w.show()

    def on_profile_will_close():
        global w
        if w:
            w.close()

    # Hook before closing anki main window or changing profile. If user directly
    # close anki main window when addon window is still open, should close addon
    # window first as some function rely on closeEvent to finish/abort.
    aqt.gui_hooks.profile_will_close.append(on_profile_will_close)

    action = aqt.QAction(ADDON_FULL_NAME, aqt.mw)
    action.triggered.connect(showWindow)
    aqt.mw.form.menuTools.addAction(action)

except AssertionError:
    print('apt.mw is None')
