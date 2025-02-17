import json
import logging
import os
import sys
from copy import deepcopy
from tempfile import gettempdir
from typing import Optional

from aqt import (QDialog, QIcon, QListWidgetItem, QPlainTextEdit, QPushButton,
                 Qt, QThread, QVBoxLayout, pyqtSlot)

from ._typing import (AbstractDictionary, AbstractQueryAPI, Config, Mask,
                      QueryWordData)
from .constants import *
from .dictionary import dictionaries
from .logger import Handler
from .loginDialog import LoginDialog
from .queryApi import apis
from .UIForm import icons_rc, mainUI, wordGroup
from .workers import (AudioDownloadWorker, LoginStateCheckWorker, QueryWorker,
                      RemoteWordFetchingWorker, VersionCheckWorker)

try:
    from aqt import mw
    from aqt.utils import askUser, openLink, showCritical, showInfo, tooltip

    from . import noteManager
except ImportError:
    from test.dummy_aqt import (askUser, mw, openLink, showCritical, showInfo,
                                tooltip)

    from ..test import dummy_noteManager as noteManager

logger = logging.getLogger('dict2Anki')


def fatal_error(exc_type, exc_value, exc_traceback):
    logger.exception(exc_value, exc_info=(exc_type, exc_value, exc_traceback))


# 未知异常日志
sys.excepthook = fatal_error


class Windows(QDialog, mainUI.Ui_Dialog):
    isRunning = False

    def __init__(self, parent=None):
        super(Windows, self).__init__(parent)
        self.currentConfig: Config
        self.localWords = []
        self.remoteWords = []
        self.selectedGroups: list[list[str]] = []

        self.workerThread = QThread(self)
        self.workerThread.start()
        self.updateCheckThead = QThread(self)
        self.updateCheckThead.start()
        self.audioDownloadThread = QThread(self)

        self.updateCheckWork = None
        self.loginWorker = None
        self.queryWorker = None
        self.pullWorker = None
        self.audioDownloadWorker = None

        self.setupUi(self)
        self.setWindowTitle(ADDON_FULL_NAME)
        self.setupLogger()
        self.initCore()
        self.checkUpdate()
        # self.__dev() # 以备调试时使用

    def __dev(self):
        def on_dev():
            logger.debug('whatever')

        self.devBtn = QPushButton('Magic Button', self.mainTab)
        self.devBtn.clicked.connect(on_dev)
        self.gridLayout_4.addWidget(self.devBtn, 4, 3, 1, 1)

    def closeEvent(self, event):
        self.setCurrentConfigAndSave()
        # 插件关闭时退出所有线程
        if self.workerThread.isRunning():
            self.workerThread.requestInterruption()
            self.workerThread.quit()
            self.workerThread.wait()

        if self.updateCheckThead.isRunning():
            self.updateCheckThead.quit()
            self.updateCheckThead.wait()

        if self.audioDownloadThread.isRunning():
            self.audioDownloadThread.requestInterruption()
            self.workerThread.quit()
            self.workerThread.wait()

        event.accept()

    def setupLogger(self):
        """初始化 Logger """

        def onDestroyed():
            logger.removeHandler(QtHandler)

        # 防止 debug 信息写入stdout/stderr 导致 Anki 崩溃
        logFile = os.path.join(gettempdir(), 'dict2anki.log')
        logging.basicConfig(handlers=[logging.FileHandler(logFile, 'w', 'utf-8')], level=logging.DEBUG, format='[%(asctime)s][%(levelname)8s] -- %(message)s - (%(name)s)')

        logTextBox = QPlainTextEdit(self)
        logTextBox.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout = QVBoxLayout()
        layout.addWidget(logTextBox)
        self.logTab.setLayout(layout)
        QtHandler = Handler(self)
        logger.addHandler(QtHandler)
        QtHandler.newRecord.connect(logTextBox.appendPlainText)

        # 日志Widget销毁时移除 Handlers
        logTextBox.destroyed.connect(onDestroyed)

    def setupGUIByConfig(self):
        config = mw.addonManager.getConfig(__name__)
        if not config:
            raise FileNotFoundError()
        self.deckComboBox.setCurrentText(config['deck'])
        self.dictionaryComboBox.setCurrentIndex(config['selectedDict'])
        self.apiComboBox.setCurrentIndex(config['selectedApi'])
        self.usernameLineEdit.setText(config['credential'][config['selectedDict']]['username'])
        self.passwordLineEdit.setText(config['credential'][config['selectedDict']]['password'])
        self.cookieLineEdit.setText(config['credential'][config['selectedDict']]['cookie'])
        self.definitionCheckBox.setChecked(config[F_DEFINITION])
        self.imageCheckBox.setChecked(config[F_IMAGE])
        self.sentenceCheckBox.setChecked(config[F_SENTENCE])
        self.phraseCheckBox.setChecked(config[F_PHRASE])
        self.AmEPhoneticCheckBox.setChecked(config[F_AMEPHONETIC])
        self.BrEPhoneticCheckBox.setChecked(config[F_BREPHONETIC])
        self.BrEPronRadioButton.setChecked(config[F_BREPRON])
        self.AmEPronRadioButton.setChecked(config[F_AMEPRON])
        self.noPronRadioButton.setChecked(config[F_NOPRON])
        self.selectedGroups = config['selectedGroup']

    def initCore(self):
        self.usernameLineEdit.hide()
        self.usernameLabel.hide()
        self.passwordLabel.hide()
        self.passwordLineEdit.hide()
        self.dictionaryComboBox.addItems([d.name for d in dictionaries])
        self.apiComboBox.addItems([d.name for d in apis])
        self.deckComboBox.addItems(noteManager.getDeckNames())
        self.setupGUIByConfig()

    def setCurrentConfigFromUI(self) -> None:
        self.currentConfig = Config(
            selectedDict=self.dictionaryComboBox.currentIndex(),
            selectedApi=self.apiComboBox.currentIndex(),
            selectedGroup=self.selectedGroups,
            deck=self.deckComboBox.currentText(),
            username=self.usernameLineEdit.text(),
            password=Mask(self.passwordLineEdit.text()),
            cookie=Mask(self.cookieLineEdit.text()),
            definition=self.definitionCheckBox.isChecked(),
            sentence=self.sentenceCheckBox.isChecked(),
            image=self.imageCheckBox.isChecked(),
            phrase=self.phraseCheckBox.isChecked(),
            AmEPhonetic=self.AmEPhoneticCheckBox.isChecked(),
            BrEPhonetic=self.BrEPhoneticCheckBox.isChecked(),
            BrEPron=self.BrEPronRadioButton.isChecked(),
            AmEPron=self.AmEPronRadioButton.isChecked(),
            noPron=self.noPronRadioButton.isChecked(),
        )
        logger.info(f'当前设置:{self.currentConfig}')

    def setCurrentConfigAndSave(self) -> None:
        self.setCurrentConfigFromUI()
        logger.info(f'保存当前设置:{self.currentConfig}')
        self._saveConfig(self.currentConfig)

    def resetProgressBar(self, total: int, text=''):
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(total)
        if text:
            self.progressBar.setFormat(f"{text}...%p%")
        else:
            self.progressBar.resetFormat()

    @staticmethod
    def _saveConfig(config):
        _config = deepcopy(config)
        _config['credential'] = [dict(username='', password='', cookie='')] * len(dictionaries)
        _config['credential'][_config['selectedDict']] = dict(
            username=_config.pop('username'),
            password=str(_config.pop('password')),
            cookie=str(_config.pop('cookie'))
        )
        maskedConfig = deepcopy(_config)
        maskedCredential = [
            dict(
                username=c['username'],
                password=Mask(c['password']),
                cookie=Mask(c['cookie'])) for c in maskedConfig['credential']
        ]
        maskedConfig['credential'] = maskedCredential
        logger.info(f'保存配置项:{maskedConfig}')
        mw.addonManager.writeConfig(__name__, _config)

    def checkUpdate(self):
        @pyqtSlot(str, str)
        def on_haveNewVersion(version, changeLog):
            if askUser(f'有新版本:{version}是否更新？\n\n{changeLog.strip()}'):
                openLink(RELEASE_URL)

        self.updateCheckWork = VersionCheckWorker()
        self.updateCheckWork.moveToThread(self.updateCheckThead)
        self.updateCheckWork.haveNewVersion.connect(on_haveNewVersion)
        self.updateCheckWork.finished.connect(self.updateCheckThead.quit)
        self.updateCheckWork.start.connect(self.updateCheckWork.run)
        self.updateCheckWork.start.emit()

    def getQueryApiByCurrentConfig(self) -> type[AbstractQueryAPI]:
        return apis[self.currentConfig['selectedApi']]
    
    def getDictByCurrentConfig(self) -> type[AbstractDictionary]:
        return dictionaries[self.currentConfig['selectedDict']]

    @pyqtSlot(int)
    def on_dictionaryComboBox_currentIndexChanged(self, index):
        """词典候选框改变事件"""
        self.currentDictionaryLabel.setText(f'当前选择词典: {self.dictionaryComboBox.currentText()}')
        config = mw.addonManager.getConfig(__name__)
        if config is None:
            raise FileNotFoundError()
        self.cookieLineEdit.setText(config['credential'][index]['cookie'])

    @pyqtSlot()
    def on_pullRemoteWordsBtn_clicked(self):
        """获取单词按钮点击事件"""
        if not self.deckComboBox.currentText():
            showInfo('\n请选择或输入要同步的牌组')
            return

        self.mainTab.setEnabled(False)
        self.resetProgressBar(0)

        self.setCurrentConfigFromUI()

        # 登陆线程
        self.loginWorker = LoginStateCheckWorker(self.getDictByCurrentConfig().checkCookie, json.loads(self.cookieLineEdit.text() or '{}'))
        self.loginWorker.moveToThread(self.workerThread)
        self.loginWorker.start.connect(self.loginWorker.run)
        self.loginWorker.logSuccess.connect(self.onLogSuccess)
        self.loginWorker.logFailed.connect(self.onLoginFailed)
        self.loginWorker.start.emit()


    @pyqtSlot()
    def onLoginFailed(self):
        showCritical('第一次登录或cookie失效!请重新登录')
        self.resetProgressBar(1)
        self.mainTab.setEnabled(True)
        self.cookieLineEdit.clear()
        currentDict = self.getDictByCurrentConfig()
        self.loginDialog = LoginDialog(
            loginUrl=currentDict.loginUrl,
            loginCheckCallbackFn=currentDict.loginCheckCallbackFn,
            parent=self
        )
        self.loginDialog.loginSucceed.connect(self.onLogSuccess)
        self.loginDialog.show()

    @pyqtSlot(str)
    def onLogSuccess(self, cookie):
        self.cookieLineEdit.setText(cookie)
        self.setCurrentConfigFromUI()
        currentDict = self.getDictByCurrentConfig()
        currentDict.checkCookie(json.loads(cookie))
        currentDict.getGroups()

        container = QDialog(self)
        group = wordGroup.Ui_Dialog()
        group.setupUi(container)

        for groupName in [str(group_name) for group_name, _ in currentDict.groups]:
            item = QListWidgetItem()
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            item.setText(groupName)
            item.setCheckState(Qt.CheckState.Unchecked)
            group.wordGroupListWidget.addItem(item)

        # 恢复上次选择的单词本分组
        if self.selectedGroups:
            for groupName in self.selectedGroups[self.currentConfig['selectedDict']]:
                items = group.wordGroupListWidget.findItems(groupName, Qt.MatchFlag.MatchExactly)
                for item in items:
                    item.setCheckState(Qt.CheckState.Checked)
        else:
            self.selectedGroups = [list()] * len(dictionaries)

        def onAccepted():
            """选择单词本弹窗确定事件"""
            # 清空 listWidget
            self.newWordListWidget.clear()
            self.needDeleteWordListWidget.clear()
            self.mainTab.setEnabled(False)

            groupNames: list[str] = [group.wordGroupListWidget.item(index).text() for index in range(group.wordGroupListWidget.count()) if # type: ignore
                              group.wordGroupListWidget.item(index).checkState() == Qt.CheckState.Checked] # type: ignore
            # 保存分组记录
            self.selectedGroups[self.currentConfig['selectedDict']] = groupNames
            self.resetProgressBar(1)
            logger.info(f'选中单词本{groupNames}')
            self.getRemoteWordList(groupNames)

        def onRejected():
            """选择单词本弹窗取消事件"""
            self.resetProgressBar(1)
            self.mainTab.setEnabled(True)

        group.buttonBox.accepted.connect(onAccepted)
        group.buttonBox.rejected.connect(onRejected)
        container.exec()

    def getRemoteWordList(self, groupNames: list[str]):
        """根据选中到分组获取分组下到全部单词，并保存到self.remoteWords"""
        groupMap = dict(self.getDictByCurrentConfig().groups)
        
        # 启动单词获取线程
        self.pullWorker = RemoteWordFetchingWorker(self.getDictByCurrentConfig(), [(groupName, groupMap[groupName],) for groupName in groupNames])
        self.pullWorker.moveToThread(self.workerThread)
        self.pullWorker.start.connect(self.pullWorker.run)
        self.pullWorker.tick.connect(lambda: self.progressBar.setValue(self.progressBar.value() + 1))
        self.pullWorker.setProgress.connect(self.progressBar.setMaximum)
        self.pullWorker.doneThisGroup.connect(self.on_getRemoteWords_groupDone)
        self.pullWorker.done.connect(self.on_allPullWork_done)
        self.pullWorker.start.emit()

        # 同时获取本地单词
        self.localWords = noteManager.getWordsByDeck(self.deckComboBox.currentText())

    @pyqtSlot(list)
    def on_getRemoteWords_groupDone(self, words: list[str]):
        """一个分组（单词本）获取完毕事件"""
        self.remoteWords.extend(words)

    @pyqtSlot()
    def on_allPullWork_done(self):
        """全部分组获取完毕事件"""
        localWordSet = set(self.localWords)
        remoteWordSet = set(self.remoteWords)
        self.localWords.clear()
        self.remoteWords.clear()

        newWords = remoteWordSet - localWordSet  # 新单词
        needToDeleteWords = localWordSet - remoteWordSet  # 需要删除的单词
        logger.info(f'本地: {localWordSet}')
        logger.info(f'远程: {remoteWordSet}')
        logger.info(f'待查: {newWords}')
        logger.info(f'待删: {needToDeleteWords}')
        waitIcon = QIcon(':/icons/wait.png')
        delIcon = QIcon(':/icons/delete.png')
        self.newWordListWidget.clear()
        self.needDeleteWordListWidget.clear()

        for word in needToDeleteWords:
            item = QListWidgetItem(word)
            item.setCheckState(Qt.CheckState.Checked)
            item.setIcon(delIcon)
            self.needDeleteWordListWidget.addItem(item)

        for word in newWords:
            item = QListWidgetItem(word)
            item.setIcon(waitIcon)
            self.newWordListWidget.addItem(item)
        self.newWordListWidget.clearSelection()

        self.dictionaryComboBox.setEnabled(True)
        self.apiComboBox.setEnabled(True)
        self.deckComboBox.setEnabled(True)
        self.pullRemoteWordsBtn.setEnabled(True)
        self.queryBtn.setEnabled(self.newWordListWidget.count() > 0)
        self.syncBtn.setEnabled(self.newWordListWidget.count() == 0 and self.needDeleteWordListWidget.count() > 0)
        if self.needDeleteWordListWidget.count() == self.newWordListWidget.count() == 0:
            logger.info('无需同步')
            tooltip('无需同步')
        self.mainTab.setEnabled(True)

    @pyqtSlot()
    def on_queryBtn_clicked(self):
        logger.info('点击查询按钮')
        self.setCurrentConfigFromUI()
        self.queryBtn.setEnabled(False)
        self.pullRemoteWordsBtn.setEnabled(False)
        self.syncBtn.setEnabled(False)

        wordItems = self.newWordListWidget.selectedItems()
        if not wordItems: # 如果没有选中单词，则查询所有单词
            wordItems = [self.newWordListWidget.item(row) for row in range(self.newWordListWidget.count())]

        row_words = []
        for wordItem in wordItems:
            row = self.newWordListWidget.row(wordItem)
            row_words.append((row, wordItem.text())) # type: ignore

        logger.info(f'待查询单词{row_words}')
        # 查询线程
        self.resetProgressBar(len(row_words))
        self.queryWorker = QueryWorker(row_words, self.getQueryApiByCurrentConfig())
        self.queryWorker.moveToThread(self.workerThread)
        self.queryWorker.rowSuccess.connect(self.on_queryRowSuccess)
        self.queryWorker.rowFail.connect(self.on_queryRowFail)
        self.queryWorker.tick.connect(lambda: self.progressBar.setValue(self.progressBar.value() + 1))
        self.queryWorker.done.connect(self.on_queryDone)
        self.queryWorker.start.connect(self.queryWorker.run)
        self.queryWorker.start.emit()

    @pyqtSlot(tuple, dict)
    def on_queryRowSuccess(self, row_word, result):
        """该行单词查询完毕"""
        row, word = row_word
        doneIcon = QIcon(':/icons/done.png')
        wordItem = self.newWordListWidget.item(row)
        wordItem.setIcon(doneIcon) # type: ignore
        wordItem.setData(Qt.ItemDataRole.UserRole, result) # type: ignore

    @pyqtSlot(tuple)
    def on_queryRowFail(self, row_word):
        row, word = row_word
        failedIcon = QIcon(':/icons/failed.png')
        failedWordItem = self.newWordListWidget.item(row)
        failedWordItem.setIcon(failedIcon) # type: ignore

    @pyqtSlot(list)
    def on_queryDone(self, results):
        failed_words = []
        for (row, word), queryResult in results:
            if not queryResult:
                failed_words.append(word)
            if failed_words:
                logger.warning(f'查询失败:{failed_words}')

        self.pullRemoteWordsBtn.setEnabled(True)
        self.queryBtn.setEnabled(True)
        self.syncBtn.setEnabled(True)

    @pyqtSlot()
    def on_syncBtn_clicked(self):

        for i in range(self.newWordListWidget.count()):
            if not self.newWordListWidget.item(i).data(Qt.ItemDataRole.UserRole): # type: ignore
                if not askUser('存在未查询或失败的单词，确定要加入单词本吗？\n 你可以选择失败的单词点击 "查询按钮" 来重试。'):
                    return
                break

        self.setCurrentConfigFromUI()
        model = noteManager.getOrCreateModel()
        noteManager.getOrCreateModelCardTemplate(model)
        deck = noteManager.getOrCreateDeck(self.deckComboBox.currentText(), model)

        logger.info('同步点击')
        audiosDownloadTasks = []

        # 判断是否需要下载发音
        if self.currentConfig[F_NOPRON]:
            logger.info('不下载发音')
            whichPron = None
        else:
            whichPron = F_AMEPRON if self.AmEPronRadioButton.isChecked() else F_BREPRON
            logger.info(f'下载发音{whichPron}')

        added = 0
        for i in range(self.newWordListWidget.count()):
            wordItem = self.newWordListWidget.item(i)
            wordItemData: Optional[QueryWordData] = wordItem.data(Qt.ItemDataRole.UserRole) # type: ignore
            if wordItemData:
                noteManager.addNoteToDeck(deck, model, self.currentConfig, wordItemData)
                added += 1
                # 添加发音任务
                if whichPron and wordItemData.get(whichPron):
                    # 我们不希望文件名被 mw.col.media.add_file 改变，因此直接下载到媒体库文件夹。
                    # 后续不需要再调用 mw.col.media.add_file
                    fpath = noteManager.media_path(f"{whichPron}_{wordItemData[F_TERM]}.mp3")
                    audiosDownloadTasks.append((fpath, wordItemData[whichPron],))

        logger.info(f'发音下载任务:{audiosDownloadTasks}')

        if audiosDownloadTasks:
            self.syncBtn.setEnabled(False)
            self.resetProgressBar(len(audiosDownloadTasks))
            if self.audioDownloadThread is not None:
                self.audioDownloadThread.requestInterruption()
                self.audioDownloadThread.quit()
                self.audioDownloadThread.wait()

            self.audioDownloadThread = QThread(self)
            self.audioDownloadThread.start()
            self.audioDownloadWorker = AudioDownloadWorker(audiosDownloadTasks)
            self.audioDownloadWorker.moveToThread(self.audioDownloadThread)
            self.audioDownloadWorker.tick.connect(lambda t,s: self.progressBar.setValue(self.progressBar.value() + 1))
            self.audioDownloadWorker.start.connect(self.audioDownloadWorker.run)
            self.audioDownloadWorker.done.connect(lambda _: tooltip(f'发音下载完成'))
            self.audioDownloadWorker.done.connect(lambda _: self.audioDownloadThread.quit())
            self.audioDownloadWorker.start.emit()

        self.newWordListWidget.clear()

        needToDeleteWordItems = []
        for i in range(self.needDeleteWordListWidget.count()):
            item = self.needDeleteWordListWidget.item(i)
            if item and item.checkState() == Qt.CheckState.Checked:
                needToDeleteWordItems.append(item)

        needToDeleteWords = [i.text() for i in needToDeleteWordItems]

        deleted = 0

        if needToDeleteWords and askUser(f'确定要删除这些单词吗:{needToDeleteWords[:3]}...({len(needToDeleteWords)}个)', title=ADDON_FULL_NAME, parent=self):
            noteIds = noteManager.getNoteIds(needToDeleteWords, self.currentConfig['deck'])
            noteManager.removeNotes(noteIds)
            deleted += 1
            for item in needToDeleteWordItems:
                self.needDeleteWordListWidget.takeItem(self.needDeleteWordListWidget.row(item))
            logger.info('删除完成')

        mw.reset()

        logger.info('完成')

        if not audiosDownloadTasks:
            tooltip(f'添加{added}个笔记\n删除{deleted}个笔记')

    def simpleLogin(self):
        showCritical("第一次登录或cookie失效！请重新登录")
        currentDict = dictionaries[self.currentConfig['selectedDict']]
        self.resetProgressBar(0)
        self.cookieLineEdit.clear()
        self.loginDialog = LoginDialog(
            loginUrl=currentDict.loginUrl,
            loginCheckCallbackFn=currentDict.loginCheckCallbackFn,
            parent=self,
        )
        self.loginDialog.loginSucceed.connect(
            self._on_simpleLoginSuccess
        )
        self.loginDialog.show()

    def _on_simpleLoginSuccess(self, cookie):
        self.cookieLineEdit.setText(cookie)
        self.setCurrentConfigFromUI()
        # set cookie to cookiejar and check
        if dictionaries[self.currentConfig['selectedDict']].checkCookie(json.loads(cookie)):
            tooltip("登录成功")
        else:
            tooltip("登录失败")
        self.resetProgressBar(1)

