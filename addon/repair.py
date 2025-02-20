import json
import logging
import os
from typing import Any, Optional

import aqt
import aqt.operations
import aqt.operations.note
import aqt.utils

from . import dictionary, noteManager, queryApi, workers
from ._typing import QueryWordData
from .addonWindow import Windows
from .constants import *

_logger = logging.getLogger("dict2Anki.repair")


_fieldConfigRemoveOnlyMap = {
    noteManager.writeNoteDefinition: lambda config: not config[F_DEFINITION],
    noteManager.writeNoteSentence: lambda config: not config[F_SENTENCE],
    noteManager.writeNotePhrase: lambda config: not config[F_PHRASE],
    noteManager.writeNoteImage: lambda config: not config[F_IMAGE],
    noteManager.writeNoteBrEPhonetic: lambda config: not config[F_BREPHONETIC],
    noteManager.writeNoteAmEPhonetic: lambda config: not config[F_AMEPHONETIC],
    noteManager.writeNotePron: lambda config: config[F_NOPRON],
}


class Repair:

    def __init__(self, windows: Windows):
        self._w = windows
        self._queryCntGrp = _CntGrp()
        self._audioCntGrp = _CntGrp()
        self._noteCnt = 0
        self._notes = []
        self._fieldFns = []
        self._whichPron = None
        self._api_name = ""
        self._w.repairBtn.clicked.connect(self._on_repairBtnClick)

    def _formatStrFromCurrentConfig(self) -> str:
        configMap = self._w.config.map

        def pronStr():
            if configMap[F_NOPRON]:
                return "无"
            elif configMap[F_BREPRON]:
                return "英"
            else:
                return "美"

        return rf"""默认设置:
        Deck：{configMap['deck']}
        查词API：{self._w.config.get_current_api().name}
        释义：{configMap[F_DEFINITION]}
        例句：{configMap[F_SENTENCE]}
        短语：{configMap[F_PHRASE]}
        图片：{configMap[F_IMAGE]}
        英式音标：{configMap[F_BREPHONETIC]}
        美式音标：{configMap[F_AMEPHONETIC]}
        发音：{pronStr()}"""

    def _writeLogAndLabel(self, msg: str, label: aqt.QLabel):
        _logger.info(msg)
        label.setText(msg)

    def _UISetEnabled(self, b):
        self._w.repairBtn.setEnabled(b)
        self._w.repairCBGroupBox.setEnabled(b)
        self._w.resetProgressBar(1)

    def _getWriteFieldFnsFromUI(self):
        self._fieldFns = []

        if self._w.repairDefCB.isChecked():
            self._fieldFns.append(noteManager.writeNoteDefinition)

        if self._w.repairSentenceCB.isChecked():
            self._fieldFns.append(noteManager.writeNoteSentence)

        if self._w.repairPhraseCB.isChecked():
            self._fieldFns.append(noteManager.writeNotePhrase)

        if self._w.repairImgCB.isChecked():
            self._fieldFns.append(noteManager.writeNoteImage)

        if self._w.repairBrEPhoneticCB.isChecked():
            self._fieldFns.append(noteManager.writeNoteBrEPhonetic)

        if self._w.repairAmEPhoneticCB.isChecked():
            self._fieldFns.append(noteManager.writeNoteAmEPhonetic)

        if self._w.repairPronCB.isChecked():
            self._fieldFns.append(noteManager.writeNotePron)

    def _on_repairBtnClick(self):
        self._getWriteFieldFnsFromUI()
        if not self._fieldFns:
            aqt.utils.showInfo("请勾选要修复的字段")
            return

        self._w.config.print()
        if not aqt.utils.askUser(
            f"{self._formatStrFromCurrentConfig()}\n\n可能要花费较长时间，是否继续?"
        ):
            return

        if not self._checkLoginState():
            self._writeLogAndLabel("请在登录后重试", self._w.repairProgressNoteLabel)
            return

        self._repair()

    def _checkLoginState(self) -> bool:
        self._writeLogAndLabel(
            "正在检查登录信息 . . .", self._w.repairProgressNoteLabel
        )
        currentApi = self._w.config.get_current_api()
        currentDict = self._w.config.get_current_dict()

        if currentApi == queryApi.eudict.API:
            if currentDict != dictionary.eudict.Eudict:
                aqt.utils.showCritical(
                    f"当前选择的是[{queryApi.eudict.API.name}]，请前往[同步]页面选择[{dictionary.eudict.Eudict.name}]以获取登录信息"
                )
                return False
            else:
                if currentDict.checkCookie(
                    json.loads(
                        str(self._w.config.get_current_credential()["cookie"]) or "{}"
                    )
                ):
                    return True
                else:
                    self._w.simpleLogin()
                    return False

        else:
            return True

    def _repair(self):
        self._UISetEnabled(False)
        self._w.repairProgressQueryLabel.clear()
        self._w.repairProgressAudioLabel.clear()
        self._noteCnt = 0
        self._queryCntGrp.reset()
        self._audioCntGrp.reset()
        self._api_name = self._w.config.get_current_api().name

        self._notes = noteManager.getNotesByDeckName(
            self._w.config.map["deck"], noteManager.noteFilterByModelName
        )
        if len(self._notes) == 0:
            self._writeLogAndLabel(
                f"没有要更新的笔记 . . . ", self._w.repairProgressNoteLabel
            )
            return self._complete(None, None)

        if self._removeOnly():
            self._updateNotes(self._notes)
            return self._complete(
                "仅清空字段，跳过查询API和发音下载 . . . ",
                self._w.repairProgressAudioLabel,
            )

        self._queryWords(self._notes)

        self._whichPron: Optional[str] = None
        if not self._w.config.map[F_NOPRON]:
            self._whichPron = F_AMEPRON if self._w.config.map[F_AMEPRON] else F_BREPRON

        self._updateNoteProgress(0, len(self._notes))
        self._updateAudioProgress(
            self._audioCntGrp.success_cnt, self._audioCntGrp.fail_cnt
        )

    def _updateNoteProgress(self, cnt, total):
        self._w.repairProgressNoteLabel.setText(f"正在更新笔记：{cnt} / {total} . . . ")

    def _updateQueryProgress(self, success_cnt, fail_cnt, total):
        self._w.repairProgressQueryLabel.setText(
            f"正在调用{self._api_name}：{success_cnt + fail_cnt} / {total}，成功：{success_cnt}，失败：{fail_cnt} . . . "
        )

    def _updateAudioProgress(self, success_cnt, fail_cnt):
        self._w.repairProgressAudioLabel.setText(
            f"正在下载发音，成功：{success_cnt}，失败：{fail_cnt} . . . "
        )

    def _removeOnly(self):
        ret = True
        for fn in self._fieldFns:
            ret = ret & _fieldConfigRemoveOnlyMap[fn](self._w.config.map)
        return ret

    def _queryWords(self, notes):
        row_words: list[Any] = [None] * len(notes)
        for i, note in enumerate(notes):
            row_words[i] = (i, note[F_TERM])

        self._w.resetProgressBar(len(row_words))
        self._queryCntGrp.total = len(row_words)
        self._updateQueryProgress(
            self._queryCntGrp.success_cnt,
            self._queryCntGrp.fail_cnt,
            self._queryCntGrp.total,
        )

        worker = workers.QueryWorker(
            row_words, self._w.config.get_current_api(), self._w.config.map[F_CONGEST]
        )
        worker.rowSuccess.connect(self._on_queryRowSuccess)
        worker.rowFail.connect(self._on_queryRowFail)
        worker.tick.connect(self._queryRowTick)
        worker.doneWithResult.connect(self._on_queryDone)
        self._w.workerman.start(worker)

    def _on_queryRowSuccess(self, row, word, queryResult):
        self._queryCntGrp.incSuccessCnt()
        self._updateQueryProgress(
            self._queryCntGrp.success_cnt,
            self._queryCntGrp.fail_cnt,
            self._queryCntGrp.total,
        )

        self._updateOneNote(self._notes[row], queryResult)
        assert aqt.mw.col
        aqt.mw.col.update_note(self._notes[row])
        self._noteCnt += 1
        self._updateNoteProgress(self._noteCnt, len(self._notes))

        self._downloadAudio(self._notes[row], queryResult)

    def _on_queryRowFail(self, row, word):
        self._queryCntGrp.incFailCnt()
        self._updateQueryProgress(
            self._queryCntGrp.success_cnt,
            self._queryCntGrp.fail_cnt,
            self._queryCntGrp.total,
        )

        self._noteCnt += 1
        self._updateNoteProgress(self._noteCnt, len(self._notes))

    def _queryRowTick(self):
        self._w.progressBar.setValue(self._w.progressBar.value() + 1)

    def _on_queryDone(self, _):
        self._complete(None, None)

    def _updateOneNote(self, note, queryResult):
        noteManager.writeNoteFields(
            note, queryResult, self._w.config.map, self._fieldFns
        )

    def _updateNotes(self, notes):
        for i, note in enumerate(notes):
            self._updateOneNote(note, None)

        # update notes to collection
        noteManager.updateNotes(notes)
        self._updateNoteProgress(len(notes), len(notes))

    def _downloadAudio(self, note, queryResult: QueryWordData):
        if not self._whichPron:
            return

        if (
            queryResult
            and (url := queryResult[self._whichPron])
            and not (
                os.path.isfile(
                    filePath := noteManager.media_path(
                        f"{self._whichPron}_{note[F_TERM]}.mp3"
                    )
                )
            )
        ):
            worker = AudioDownloadSingleWorker(filePath, url)
            worker.tick.connect(self._on_audioDownloadTick)
            self._w.workerman.start(worker)

    def _on_audioDownloadTick(self, fileName, url, success):
        if success:
            self._audioCntGrp.incSuccessCnt()
        else:
            self._audioCntGrp.incFailCnt()
        self._updateAudioProgress(
            self._audioCntGrp.success_cnt, self._audioCntGrp.fail_cnt
        )

    def _complete(self, msg, label):
        if msg:
            self._writeLogAndLabel(msg, label)
        self._w.repairProgressNoteLabel.setText(
            self._w.repairProgressNoteLabel.text() + "修复完成"
        )
        self._UISetEnabled(True)
        self._clear()
        aqt.mw.reset()

        aqt.utils.tooltip("修复完成")

    def _clear(self):
        self._notes.clear()
        self._fieldFns.clear()
        self._api_name = ""
        self._whichPron = None


class _CntGrp:
    def __init__(self):
        self.reset()

    def reset(self):
        self.total = 0
        self.success_cnt = 0
        self.fail_cnt = 0

    def incSuccessCnt(self):
        self.success_cnt += 1

    def incFailCnt(self):
        self.fail_cnt += 1


class AudioDownloadSingleWorker(workers.NetworkWorker):
    tick = aqt.pyqtSignal(str, str, bool)
    _logger = logging.getLogger("dict2Anki.workers.AudioDownloadSingleWorker")

    def __init__(self, fileName, url):
        super().__init__()
        self._fileName = fileName
        self._url = url

    def run(self):
        try:
            workers.downloadSingleAudio(
                self._fileName, self._url, self.session, self._logger, self.tick
            )
        finally:
            self.done.emit(self)
