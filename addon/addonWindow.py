import json
import logging
import os
import sys
from copy import deepcopy
from tempfile import gettempdir
from typing import Iterable, Optional

import aqt
import aqt.utils
from aqt import (QDialog, QIcon, QListWidgetItem, QPlainTextEdit, QPushButton,
                 Qt, QVBoxLayout, pyqtSlot)

from . import conf_model, misc, noteManager
from ._typing import AbstractDictionary, AbstractQueryAPI, QueryWordData
from .constants import *
from .dictionary import dictionaries
from .logger import Handler
from .loginDialog import LoginDialog
from .queryApi import apis
from .UIForm import icons_rc, mainUI, wordGroup
from .workers import (AudioDownloadWorker, LoginStateCheckWorker, QueryWorker,
                      RemoteWordFetchingWorker, VersionCheckWorker,
                      WorkerManager)

logger = logging.getLogger('dict2Anki')


def fatal_error(exc_type, exc_value, exc_traceback):
    logger.exception(exc_value, exc_info=(exc_type, exc_value, exc_traceback))


# 未知异常日志
# sys.excepthook = fatal_error


class Windows(QDialog, mainUI.Ui_Dialog):
    isRunning = False

    def __init__(self, parent=None):
        super(Windows, self).__init__(parent)
        self.localWords = []
        self.remoteWords = []

        self.workerman = WorkerManager()
        self.conf = conf_model.Conf(ConfCtl.read())

        self.init_ui()
        self.setupLogger()
        self.checkUpdate()
        # self.__dev() # 以备调试时使用

    def __dev(self):
        def on_dev():
            logger.debug('whatever')

        self.devBtn = QPushButton('Magic Button', self.mainTab)
        self.devBtn.clicked.connect(on_dev)
        self.gridLayout_4.addWidget(self.devBtn, 4, 3, 1, 1)

    def init_ui(self):
        self.setupUi(self)
        self.setWindowTitle(ADDON_FULL_NAME)
        self.usernameLineEdit.hide()
        self.usernameLabel.hide()
        self.passwordLabel.hide()
        self.passwordLineEdit.hide()
        self.dummyBtn.hide()
        self.dictionaryComboBox.addItems([d.name for d in dictionaries])
        self.apiComboBox.addItems([d.name for d in apis])
        self.deckComboBox.addItems(noteManager.getDeckNames())
        self.needDeleteWordsView = NeedDeleteWordsView(self.needDeleteCheckBox, self.needDeleteWordListWidget)
        ConfCtl.init_ui(self, self.conf)

    def closeEvent(self, event):
        ConfCtl.write(self.conf)
        # 插件关闭时退出所有线程
        self.workerman.destroy()

        event.accept()

    def setupLogger(self):
        """初始化 Logger """

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

        def onDestroyed():
            QtHandler.newRecord.disconnect(logTextBox.appendPlainText)
            logger.removeHandler(QtHandler)

        # 日志Widget销毁时移除 Handlers
        logTextBox.destroyed.connect(onDestroyed)

    def get_current_dict(self) -> type[AbstractDictionary]:
        return dictionaries[self.conf.selected_dict]

    def get_current_api(self) -> type[AbstractQueryAPI]:
        return apis[self.conf.selected_api]

    def resetProgressBar(self, total: int):
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(total)

    def checkUpdate(self):
        @pyqtSlot(str, str)
        def on_haveNewVersion(version, changeLog):
            if aqt.utils.askUser(f'有新版本:{version}是否更新？\n\n{changeLog.strip()}'):
                aqt.utils.openLink(RELEASE_URL)
        worker = VersionCheckWorker()
        worker.haveNewVersion.connect(on_haveNewVersion)
        self.workerman.start(worker)

    @pyqtSlot()
    def on_pullRemoteWordsBtn_clicked(self):
        """获取单词按钮点击事件"""
        if not self.conf.deck:
            aqt.utils.showInfo('\n请选择或输入要同步的牌组')
            return

        self.mainTab.setEnabled(False)
        self.resetProgressBar(0)

        logger.info(self.conf.print())

        # 登陆线程
        worker = LoginStateCheckWorker(self.get_current_dict().checkCookie,
                                       json.loads(self.conf.current_cookies or '{}'))
        worker.logSuccess.connect(self.onLogSuccess)
        worker.logFailed.connect(self.onLoginFailed)
        self.workerman.start(worker)

    @pyqtSlot()
    def onLoginFailed(self):
        aqt.utils.showCritical('第一次登录或cookie失效!请重新登录')
        self.resetProgressBar(1)
        self.mainTab.setEnabled(True)
        self.conf.current_cookies = ""
        currentDict = self.get_current_dict()
        self.loginDialog = LoginDialog(
            loginUrl=currentDict.loginUrl,
            loginCheckCallbackFn=currentDict.loginCheckCallbackFn,
            parent=self
        )
        self.loginDialog.loginSucceed.connect(self.onLogSuccess)
        self.loginDialog.show()

    @pyqtSlot(str)
    def onLogSuccess(self, cookie):
        self.conf.current_cookies = cookie
        currentDict = self.get_current_dict()
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
        if grps := self.conf.current_selected_groups:
            for groupName in grps:
                items = group.wordGroupListWidget.findItems(groupName, Qt.MatchFlag.MatchExactly)
                for item in items:
                    item.setCheckState(Qt.CheckState.Checked)

        def onAccepted():
            """选择单词本弹窗确定事件"""
            # 清空 listWidget
            self.newWordListWidget.clear()
            self.needDeleteWordsView.clear()
            self.mainTab.setEnabled(False)

            groupNames: list[str] = [group.wordGroupListWidget.item(index).text() for index in range(group.wordGroupListWidget.count()) if # type: ignore
                              group.wordGroupListWidget.item(index).checkState() == Qt.CheckState.Checked] # type: ignore
            # 保存分组记录
            self.conf.current_selected_groups = groupNames
            self.resetProgressBar(1)
            logger.info(f'选中单词本{groupNames}')
            self.getRemoteWordList(groupNames)

        def onRejected():
            """选择单词本弹窗取消事件"""
            self.resetProgressBar(1)
            self.mainTab.setEnabled(True)

        group.buttonBox.accepted.connect(onAccepted)
        container.rejected.connect(onRejected)
        container.exec()

    def getRemoteWordList(self, groupNames: list[str]):
        """根据选中到分组获取分组下到全部单词，并保存到self.remoteWords"""
        groupMap = dict(self.get_current_dict().groups)

        # 启动单词获取线程
        worker = RemoteWordFetchingWorker(self.get_current_dict(),
                                          [(groupName, groupMap[groupName],) for groupName in groupNames])
        worker.tick.connect(lambda: self.progressBar.setValue(self.progressBar.value() + 1))
        worker.setProgress.connect(self.progressBar.setMaximum)
        worker.doneThisGroup.connect(self.on_getRemoteWords_groupDone)
        worker.done.connect(self.on_allPullWork_done)
        self.workerman.start(worker)

        # 同时获取本地单词
        self.localWords = noteManager.getWordsByDeck(self.conf.deck)

    @pyqtSlot(list)
    def on_getRemoteWords_groupDone(self, words: list[str]):
        """一个分组（单词本）获取完毕事件"""
        self.remoteWords.extend(words)

    @pyqtSlot(object)
    def on_allPullWork_done(self, worker):
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
        self.newWordListWidget.clear()
        self.needDeleteWordsView.clear()

        self.needDeleteWordsView.add_items(needToDeleteWords)

        for word in newWords:
            item = QListWidgetItem(word)
            item.setIcon(waitIcon)
            self.newWordListWidget.addItem(item)
        self.newWordListWidget.clearSelection()

        self.needDeleteWordsView.check_if_not_empty()

        self.dictionaryComboBox.setEnabled(True)
        self.apiComboBox.setEnabled(True)
        self.deckComboBox.setEnabled(True)
        self.pullRemoteWordsBtn.setEnabled(True)
        self.queryBtn.setEnabled(self.newWordListWidget.count() > 0)
        self.syncBtn.setEnabled(self.newWordListWidget.count() == 0 and not self.needDeleteWordsView.empty())
        if self.needDeleteWordsView.empty() and self.newWordListWidget.count() == 0:
            logger.info('无需同步')
            aqt.utils.tooltip('无需同步')
        else:
            aqt.utils.tooltip("查询完成")
        self.mainTab.setEnabled(True)

    @pyqtSlot()
    def on_queryBtn_clicked(self):
        logger.info('点击查询按钮')
        logger.info(self.conf.print())
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
        worker = QueryWorker(row_words, self.get_current_api(), self.conf.congest)
        worker.rowSuccess.connect(self.on_queryRowSuccess)
        worker.rowFail.connect(self.on_queryRowFail)
        worker.tick.connect(lambda: self.progressBar.setValue(self.progressBar.value() + 1))
        worker.doneWithResult.connect(self.on_queryDone)
        self.workerman.start(worker)

    @pyqtSlot(int, str, dict)
    def on_queryRowSuccess(self, row, word, result):
        """该行单词查询完毕"""
        doneIcon = QIcon(':/icons/done.png')
        wordItem = self.newWordListWidget.item(row)
        wordItem.setIcon(doneIcon) # type: ignore
        wordItem.setData(Qt.ItemDataRole.UserRole, result) # type: ignore

    @pyqtSlot(int, str)
    def on_queryRowFail(self, row, word):
        failedIcon = QIcon(':/icons/failed.png')
        failedWordItem = self.newWordListWidget.item(row)
        failedWordItem.setIcon(failedIcon) # type: ignore

    @pyqtSlot(list)
    def on_queryDone(self, results):
        failed_words = []
        for row, word, queryResult in results:
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
                if not aqt.utils.askUser(
                    '存在未查询或失败的单词，确定要加入单词本吗？\n 你可以选择失败的单词点击 "查询按钮" 来重试。'):
                    return
                break

        model = noteManager.getOrCreateModel()
        noteManager.getOrCreateModelCardTemplate(model)
        deck = noteManager.getOrCreateDeck(self.conf.deck, model)

        logger.info('同步点击')
        audiosDownloadTasks = []

        # 判断是否需要下载发音
        if self.conf.no_pron:
            logger.info('不下载发音')
            whichPron = None
        else:
            whichPron = F_AMEPRON if self.conf.ame_pron else F_BREPRON
            logger.info(f'下载发音{whichPron}')

        added = 0
        for i in range(self.newWordListWidget.count()):
            wordItem = self.newWordListWidget.item(i)
            wordItemData: Optional[QueryWordData] = wordItem.data(Qt.ItemDataRole.UserRole) # type: ignore
            if wordItemData:
                noteManager.addNoteToDeck(deck, model, self.conf, wordItemData)
                added += 1
                # 添加发音任务
                if whichPron and wordItemData.get(whichPron):
                    # 我们不希望文件名被 mw.col.media.add_file 改变，因此直接下载到媒体库文件夹。
                    # 后续不需要再调用 mw.col.media.add_file
                    fpath = noteManager.media_path(misc.audio_fname(whichPron, wordItemData[F_TERM]))
                    audiosDownloadTasks.append((fpath, wordItemData[whichPron],))

        logger.info(f'发音下载任务:{audiosDownloadTasks}')

        if audiosDownloadTasks:
            self.syncBtn.setEnabled(False)
            self.resetProgressBar(len(audiosDownloadTasks))

            worker = AudioDownloadWorker(audiosDownloadTasks)
            worker.tick.connect(lambda f,u,s: self.progressBar.setValue(self.progressBar.value() + 1))
            worker.done.connect(lambda _: aqt.utils.tooltip(f'发音下载完成'))
            self.workerman.start(worker)

        self.newWordListWidget.clear()

        needDeleteItems = self.needDeleteWordsView.checked_items()
        needToDeleteWords = self.needDeleteWordsView.item_texts(needDeleteItems)

        deleted = 0

        if needToDeleteWords and aqt.utils.askUser(
            f'确定要删除这些单词吗:{needToDeleteWords[:3]}...({len(needToDeleteWords)}个)', title=ADDON_FULL_NAME, parent=self):
            noteIds = noteManager.getNoteIds(needToDeleteWords, self.conf.deck)
            noteManager.removeNotes(noteIds)
            deleted = len(needToDeleteWords)
            self.needDeleteWordsView.remove_items(needDeleteItems)
            logger.info('删除完成')

        aqt.mw.reset()

        logger.info('完成')

        if not audiosDownloadTasks:
            aqt.utils.tooltip(f'添加{added}个笔记\n删除{deleted}个笔记')

    def simpleLogin(self):
        aqt.utils.showCritical("第一次登录或cookie失效！请重新登录")
        currentDict = self.get_current_dict()
        self.resetProgressBar(0)
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
        self.conf.current_cookies = cookie
        logger.info(self.conf.print())
        # set cookie to cookiejar and check
        if self.get_current_dict().checkCookie(json.loads(cookie)):
            aqt.utils.tooltip("登录成功")
        else:
            aqt.utils.tooltip("登录失败")
        self.resetProgressBar(1)


class NeedDeleteWordsView:
    def __init__(self, title_checkbox: aqt.QCheckBox, list_widget: aqt.QListWidget):
        self._checkbox = title_checkbox
        self._list_widget = list_widget
        self._delIcon = QIcon(":/icons/delete.png")
        self._listen_checkbox_change()

    def _listen_checkbox_change(self):
        def on_cb_change(state):
            check_state = Qt.CheckState(state)
            for item in self._items_iter():
                item.setCheckState(check_state)

        self._checkbox.stateChanged.connect(on_cb_change)

    def check_if_not_empty(self):
        if not self.empty():
            self._checkbox.blockSignals(True)
            self._checkbox.setChecked(True)
            self._checkbox.blockSignals(False)

    def _items_iter(self) -> Iterable[aqt.QListWidgetItem]:
        return (self._list_widget.item(i) for i in range(self._list_widget.count()))  # type: ignore

    def items(self) -> list[aqt.QListWidgetItem]:
        return list(self._items_iter())

    def checked_items(self) -> list[aqt.QListWidgetItem]:
        return list(
            filter(
                lambda item: item.checkState() == Qt.CheckState.Checked,
                self._items_iter(),
            )
        )

    def item_texts(self, items: Iterable[aqt.QListWidgetItem]) -> list[str]:
        return [item.text() for item in items]

    def add_items(self, texts: Iterable[str]):
        for text in texts:
            self.add_item(text)

    def add_item(self, text: str):
        item = QListWidgetItem(text)
        item.setCheckState(Qt.CheckState.Checked)
        item.setIcon(self._delIcon)
        self._list_widget.addItem(item)

    def remove_items(self, items: Iterable[aqt.QListWidgetItem]):
        for item in items:
            self._list_widget.takeItem(self._list_widget.row(item))

    def empty(self):
        return self._list_widget.count() == 0

    def clear(self):
        self._list_widget.clear()


class ConfCtl:

    @staticmethod
    def read():
        if config := aqt.mw.addonManager.getConfig(__name__):
            return config
        else:
            raise FileNotFoundError('missing config file')

    @staticmethod
    def write(conf: conf_model.Conf):
        aqt.mw.addonManager.writeConfig(__name__, conf.get_map())  # type: ignore

    @staticmethod
    def init_ui(w: Windows, conf: conf_model.Conf):
        """Should be called only once!"""

        # init UI
        w.deckComboBox.setCurrentText(conf.deck)
        w.dictionaryComboBox.setCurrentIndex(conf.selected_dict)
        w.currentDictionaryLabel.setText(f'当前选择词典: {w.dictionaryComboBox.currentText()}')
        w.apiComboBox.setCurrentIndex(conf.selected_api)
        w.usernameLineEdit.setText(conf.current_username)
        w.passwordLineEdit.setText(conf.current_password)
        w.cookieLineEdit.setText(conf.current_cookies)
        w.definitionCheckBox.setChecked(conf.definition)
        w.imageCheckBox.setChecked(conf.image)
        w.sentenceCheckBox.setChecked(conf.sentence)
        w.phraseCheckBox.setChecked(conf.phrase)
        w.AmEPhoneticCheckBox.setChecked(conf.ame_phonetic)
        w.BrEPhoneticCheckBox.setChecked(conf.bre_phonetic)
        w.BrEPronRadioButton.setChecked(conf.bre_pron)
        w.AmEPronRadioButton.setChecked(conf.ame_pron)
        w.noPronRadioButton.setChecked(conf.no_pron)
        w.congestSpinBox.setValue(conf.congest)

        def _on_deck_combobox_change(text):
            conf.deck = text

        def _on_dict_combobox_change(index):
            conf.selected_dict = index
            w.currentDictionaryLabel.setText(f'当前选择词典: {w.dictionaryComboBox.currentText()}')
            w.cookieLineEdit.blockSignals(True)
            w.cookieLineEdit.setText(conf.current_cookies)
            w.cookieLineEdit.blockSignals(False)

        def _on_api_combobox_change(index):
            conf.selected_api = index

        def _on_cookie_line_edit_change(text):
            conf.current_cookies = text

        def _on_definition_cb_change(state: int):
            conf.definition = state == Qt.CheckState.Checked.value

        def _on_sentence_cb_change(state):
            conf.sentence = state == Qt.CheckState.Checked.value

        def _on_phrase_cb_change(state):
            conf.phrase = state == Qt.CheckState.Checked.value

        def _on_image_cb_change(state):
            conf.image = state == Qt.CheckState.Checked.value

        def _on_ame_phonetic_cb_change(state):
            conf.ame_phonetic = state == Qt.CheckState.Checked.value

        def _on_bre_phonetic_cb_change(state):
            conf.bre_phonetic = state == Qt.CheckState.Checked.value

        def _on_ame_pron_radio_toggled():
            if w.AmEPronRadioButton.isChecked():
                conf.ame_pron = True

        def _on_bre_pron_radio_toggled():
            if w.BrEPronRadioButton.isChecked():
                conf.bre_pron = True

        def _on_no_pron_radio_toggled():
            if w.noPronRadioButton.isChecked():
                conf.no_pron = True

        def _on_congest_spinbox_change(value: int):
            conf.congest = value

        # register events
        w.deckComboBox.currentTextChanged.connect(_on_deck_combobox_change)
        w.dictionaryComboBox.currentIndexChanged.connect(_on_dict_combobox_change)
        w.apiComboBox.currentIndexChanged.connect(_on_api_combobox_change)
        w.cookieLineEdit.textChanged.connect(_on_cookie_line_edit_change)
        w.definitionCheckBox.stateChanged.connect(_on_definition_cb_change)
        w.sentenceCheckBox.stateChanged.connect(_on_sentence_cb_change)
        w.phraseCheckBox.stateChanged.connect(_on_phrase_cb_change)
        w.imageCheckBox.stateChanged.connect(_on_image_cb_change)
        w.AmEPhoneticCheckBox.stateChanged.connect(_on_ame_phonetic_cb_change)
        w.BrEPhoneticCheckBox.stateChanged.connect(_on_bre_phonetic_cb_change)
        w.AmEPronRadioButton.toggled.connect(_on_ame_pron_radio_toggled)
        w.BrEPronRadioButton.toggled.connect(_on_bre_pron_radio_toggled)
        w.noPronRadioButton.toggled.connect(_on_no_pron_radio_toggled)
        w.congestSpinBox.valueChanged.connect(_on_congest_spinbox_change)

        def update_cookies_line_edit(val: str):
            w.cookieLineEdit.blockSignals(True)
            w.cookieLineEdit.setText(val)
            w.cookieLineEdit.blockSignals(False)

        # register model events. For now only `current_cookies` is actively modified by code (not by user)
        conf.listen("current_cookies", update_cookies_line_edit)
