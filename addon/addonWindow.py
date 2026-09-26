from __future__ import annotations

import json
import logging
import os
import shutil
from tempfile import gettempdir
from typing import Iterable, Iterator, Optional

import aqt
import aqt.utils
from aqt import (
    QCloseEvent,
    QDialog,
    QIcon,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    Qt,
    QVBoxLayout,
    pyqtSlot,
)

from . import adv_conf, conf_model, misc, noteManager
from . import constants as C
from ._typing import AbstractDictionary, AbstractQueryAPI, QueryWordData
from .conf_controller import ConfCtl
from .dictionary import dictionaries
from .logger import Handler
from .loginDialog import LoginDialog
from .queryApi import apis
from .repair import Repair
from .UIForm import (
    icons_rc,  # noqa: F401
    mainUI,
    wordGroup,
)
from .workers import ApiASTWorker, LoginStateCheckWorker, RemoteWordFetchingWorker, VersionCheckWorker, WorkerManager

logger = logging.getLogger('dict2Anki')


def fatal_error(exc_type, exc_value, exc_traceback):
    logger.exception(exc_value, exc_info=(exc_type, exc_value, exc_traceback))


# 未知异常日志
# sys.excepthook = fatal_error


class Windows(QDialog, mainUI.Ui_Dialog):
    isRunning = False

    def __init__(self, parent=None):
        super(Windows, self).__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.localWords = []
        self.remoteWords = []

        self.workerman = WorkerManager()
        self.conf = conf_model.Conf.getinstance(ConfCtl.read())

        self.init_ui()
        self.setupLogger()
        self.repair = Repair(self)
        # self.checkUpdate() # disable temporarily
        # self.__dev() # 以备调试时使用

    def __dev(self):
        def on_dev():
            logger.debug('whatever')

        self.devBtn = QPushButton('Magic Button', self.mainTab)
        self.devBtn.clicked.connect(on_dev)
        self.gridLayout_4.addWidget(self.devBtn, 4, 3, 1, 1)

    def init_ui(self):
        self.setupUi(self)
        self.setWindowTitle(C.ADDON_FULL_NAME)
        self.deckComboBox.addItems(noteManager.getDeckNames())
        self.needDeleteWordsView = NeedDeleteWordsView(self.needDeleteCheckBox, self.needDeleteWordListWidget)
        ConfCtl.init_ui(self, self.conf)

    def closeEvent(self, a0: Optional[QCloseEvent]):
        ConfCtl.write(self.conf)
        conf_model.Conf.delinstance()
        # removeHandler in logTextBox.destroyed event is too late which may
        # cause logging in new Windows emit to old logTextBox which is
        # destroyed. So removeHandler here, earlier.
        logger.removeHandler(self.QtHandler)
        # 插件关闭时退出所有线程
        self.workerman.destroy()
        shutil.rmtree(misc.tmp_audio_dir(), ignore_errors=True)

        # need super to emit finished event
        super().closeEvent(a0)

    def setupLogger(self):
        """初始化 Logger"""

        # 防止 debug 信息写入stdout/stderr 导致 Anki 崩溃
        logFile = os.path.join(gettempdir(), 'dict2anki.log')
        logging.basicConfig(
            handlers=[logging.FileHandler(logFile, 'w', 'utf-8')],
            level=logging.DEBUG,
            format='[%(asctime)s][%(levelname)8s] -- %(message)s - (%(name)s)',
        )

        logTextBox = QPlainTextEdit(self)
        logTextBox.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout = QVBoxLayout()
        layout.addWidget(logTextBox)
        self.logTab.setLayout(layout)
        self.QtHandler = Handler(self)
        logger.addHandler(self.QtHandler)
        self.QtHandler.newRecord.connect(logTextBox.appendPlainText)

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
                aqt.utils.openLink(C.RELEASE_URL)

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
        worker = LoginStateCheckWorker(
            self.get_current_dict().checkCookie, json.loads(self.conf.current_cookies or '{}')
        )
        worker.logSuccess.connect(self.onLogSuccess)
        worker.logFailed.connect(self.onLoginFailed)
        self.workerman.start(worker)

    @pyqtSlot()
    def onLoginFailed(self):
        aqt.utils.showCritical('第一次登录或cookie失效!请重新登录')
        self.resetProgressBar(1)
        self.mainTab.setEnabled(True)
        self.conf.current_cookies = ''
        currentDict = self.get_current_dict()
        self.loginDialog = LoginDialog(
            loginUrl=currentDict.loginUrl, loginCheckCallbackFn=currentDict.loginCheckCallbackFn, parent=self
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
        container.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
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

            groupNames: list[str] = [
                group.wordGroupListWidget.item(index).text()  # type: ignore
                for index in range(group.wordGroupListWidget.count())
                if group.wordGroupListWidget.item(index).checkState() == Qt.CheckState.Checked  # type: ignore
            ]
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
        worker = RemoteWordFetchingWorker(
            self.get_current_dict(),
            [
                (
                    groupName,
                    groupMap[groupName],
                )
                for groupName in groupNames
            ],
        )
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
    def on_allPullWork_done(self, _worker):
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

        self.needDeleteWordsView.check_head_cb_if_not_empty()

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
            aqt.utils.tooltip('查询完成')
        self.mainTab.setEnabled(True)

    @pyqtSlot()
    def on_queryBtn_clicked(self):
        logger.info('点击查询按钮')
        logger.info(self.conf.print())

        ast_dict, errmsg = adv_conf.ensure_ast_dict_errmsg_for_ui(self.conf.get_ast_dict())
        if errmsg:
            aqt.utils.show_critical(errmsg)
            return

        self.queryBtn.setEnabled(False)
        self.pullRemoteWordsBtn.setEnabled(False)
        self.syncBtn.setEnabled(False)

        wordItems = self.newWordListWidget.selectedItems()
        if not wordItems:  # 如果没有选中单词，则查询所有单词
            wordItems = [self.newWordListWidget.item(row) for row in range(self.newWordListWidget.count())]

        row_words = []
        for wordItem in wordItems:
            row = self.newWordListWidget.row(wordItem)
            row_words.append((row, wordItem.text()))  # type: ignore

        logger.info(f'待查询单词{row_words}')
        self.resetProgressBar(len(row_words))

        worker = ApiASTWorker(row_words, ast_dict, self.conf.congest, parent=self)
        worker.rowSuccess.connect(self.on_queryRowSuccess)
        worker.rowFail.connect(self.on_queryRowFail)
        worker.done.connect(self.on_queryDone)
        self.workerman.start(worker)

    @pyqtSlot(int, str, dict)
    def on_queryRowSuccess(self, row, _word, query_cache):
        """该行单词查询完毕"""
        doneIcon = QIcon(':/icons/done.png')
        wordItem = self.newWordListWidget.item(row)
        wordItem.setIcon(doneIcon)  # type: ignore
        wordItem.setData(Qt.ItemDataRole.UserRole, query_cache)  # type: ignore

    @pyqtSlot(int, str, dict)
    def on_queryRowFail(self, row, _word, query_cache):
        failedIcon = QIcon(':/icons/failed.png')
        failedWordItem = self.newWordListWidget.item(row)
        failedWordItem.setIcon(failedIcon)  # type: ignore
        failedWordItem.setData(Qt.ItemDataRole.UserRole, query_cache)  # type: ignore

    def on_queryDone(self, _worker):
        self.pullRemoteWordsBtn.setEnabled(True)
        self.queryBtn.setEnabled(True)
        self.syncBtn.setEnabled(True)

    @pyqtSlot()
    def on_syncBtn_clicked(self):
        assert aqt.mw.col is not None

        ast_dict, errmsg = adv_conf.ensure_ast_dict_errmsg_for_ui(self.conf.get_ast_dict())
        if errmsg:
            aqt.utils.show_critical(errmsg)
            return

        for i in range(self.newWordListWidget.count()):
            if not self.newWordListWidget.item(i).data(Qt.ItemDataRole.UserRole):  # type: ignore
                if not aqt.utils.askUser(
                    '存在未查询或失败的单词，确定要加入单词本吗？\n 你可以选择失败的单词点击 "查询按钮" 来重试。',
                    parent=self,
                ):
                    return
                break

        self.syncBtn.setEnabled(False)
        logger.info('同步点击')

        # add notes to database

        model = noteManager.getOrCreateModel()
        noteManager.getOrCreateModelCardTemplate(model)
        deck = noteManager.getOrCreateDeck(self.conf.deck, model)

        added = 0
        notes = []
        for i in range(self.newWordListWidget.count()):
            wordItem = self.newWordListWidget.item(i)
            query_cache: Optional[dict[str, Optional[QueryWordData]]] = wordItem.data(Qt.ItemDataRole.UserRole)  # type: ignore

            # create note only for words that have any API data
            if not query_cache or not any(api_data for api_data in query_cache.values()):
                continue

            word = wordItem.text()  # type: ignore

            # 1. new and add note to database (in order to update flag note
            # must be in database)
            # 2. eval ASTs
            # 3. update note to database

            note = noteManager.new_note(word, model)
            notes.append(note)
            aqt.mw.col.add_note(note, deck['id'])  # type: ignore

            adv_conf.eval_asts_set_note(word, note, query_cache, ast_dict)

            # move audio file
            ast_dict[C.F_AMEPRON].eval(adv_conf.MoveAudioFConfVisitor(word, C.F_AMEPRON))
            ast_dict[C.F_BREPRON].eval(adv_conf.MoveAudioFConfVisitor(word, C.F_BREPRON))

            added += 1

        noteManager.updateNotes(notes)
        self.newWordListWidget.clear()

        # delete checkbox selected items

        needDeleteItems = self.needDeleteWordsView.checked_items()
        needToDeleteWords = self.needDeleteWordsView.item_texts(needDeleteItems)

        deleted = 0

        if needToDeleteWords and aqt.utils.askUser(
            f'确定要删除这些单词吗:{needToDeleteWords[:3]}...({len(needToDeleteWords)}个)',
            title=C.ADDON_FULL_NAME,
            parent=self,
        ):
            noteIds = noteManager.getNoteIds(needToDeleteWords, self.conf.deck)
            noteManager.removeNotes(noteIds)
            deleted = len(needToDeleteWords)
            self.needDeleteWordsView.remove_items(needDeleteItems)
            logger.info('删除完成')

        aqt.mw.reset()

        logger.info('完成')
        self.syncBtn.setEnabled(True)
        aqt.utils.tooltip(f'添加{added}个笔记\n删除{deleted}个笔记')

    def simpleLogin(self):
        aqt.utils.showCritical('第一次登录或cookie失效！请重新登录')
        currentDict = self.get_current_dict()
        self.resetProgressBar(0)
        self.loginDialog = LoginDialog(
            loginUrl=currentDict.loginUrl,
            loginCheckCallbackFn=currentDict.loginCheckCallbackFn,
            parent=self,
        )
        self.loginDialog.loginSucceed.connect(self._on_simpleLoginSuccess)
        self.loginDialog.show()

    def _on_simpleLoginSuccess(self, cookie):
        self.conf.current_cookies = cookie
        logger.info(self.conf.print())
        # set cookie to cookiejar and check
        if self.get_current_dict().checkCookie(json.loads(cookie)):
            aqt.utils.tooltip('登录成功')
        else:
            aqt.utils.tooltip('登录失败')
        self.resetProgressBar(1)


class NeedDeleteWordsView:
    def __init__(self, head_cb: aqt.QCheckBox, list_widget: aqt.QListWidget):
        self._head_cb = head_cb
        self._list_widget = list_widget
        self._delIcon = QIcon(':/icons/delete.png')
        self._listen_head_cb_change()

    def _listen_head_cb_change(self):

        def on_cb_change(state):
            check_state = Qt.CheckState(state)
            for item in self._items_iter():
                item.setCheckState(check_state)

        self._head_cb.stateChanged.connect(on_cb_change)

    def check_head_cb_if_not_empty(self):
        if not self.empty():
            self._head_cb.blockSignals(True)
            self._head_cb.setChecked(True)
            self._head_cb.blockSignals(False)

    def _items_iter(self) -> Iterator[aqt.QListWidgetItem]:
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
