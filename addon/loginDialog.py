import json
import sys
import logging
from PyQt6.QtCore import QUrl, pyqtSignal, Qt
from .UIForm import loginDialog
from PyQt6.QtWidgets import QDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from .constants import USER_AGENT

logger = logging.getLogger('dict2Anki')


class LoginDialog(QDialog, loginDialog.Ui_LoginDialog):
    loginSucceed = pyqtSignal(str)

    def __init__(self, loginUrl, loginCheckCallbackFn, parent=None):
        super().__init__(parent)
        self.url = QUrl(loginUrl)
        self.loginCheckCallbackFn = loginCheckCallbackFn
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.page = LoginWebEngineView(self)
        self.pageContainer.addWidget(self.page)
        self.page.load(self.url)
        self.makeConnection()

    def makeConnection(self):
        self.reloadBtn.clicked.connect(self._reload)
        self.page.loadFinished.connect(self.checkLoginState)

    def _reload(self):
        logger.debug('Reload page')
        self.page.cookieStore.deleteAllCookies() # type: ignore
        self.page.load(QUrl(self.address.text()))

    def checkLoginState(self):
        def contentLoaded(content):
            logger.debug(f'Cookie:{self.page.cookie}')
            logger.debug(f'Content{content}')
            if self.loginCheckCallbackFn(cookie=self.page.cookie, content=content):
                logger.info(f'Login Success!')
                self.onLoginSucceed()
            logger.info(f'Login Fail!')

        self.page.page().toHtml(contentLoaded) # type: ignore

    def onLoginSucceed(self):
        logger.info('Destruct login dialog')
        self.close()
        logger.debug('emit cookie')
        self.loginSucceed.emit(json.dumps(self.page.cookie))


class LoginWebEngineView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 绑定cookie被添加的信号槽
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setHttpUserAgent( # type: ignore
            USER_AGENT
        )
        self.cookieStore = self.profile.cookieStore() # type: ignore
        self.cookieStore.cookieAdded.connect(self.onCookieAdd) # type: ignore
        self._cookies = {}
        self.show()

    def onCookieAdd(self, cookie):
        name = cookie.name().data().decode('utf-8')
        value = cookie.value().data().decode('utf-8')
        self._cookies[name] = value

    @property
    def cookie(self) -> dict:
        return self._cookies
