import json
import logging
import os
import re
from typing import Any, Optional

import aqt
import aqt.operations
import aqt.operations.note
import aqt.utils

from . import dictionary, noteManager, queryApi
from .addonWindow import Windows
from .constants import *
from .workers import AudioDownloadWorker, QueryWorker

_logger = logging.getLogger("dict2Anki.noteFixer")


_fieldConfigRemoveOnlyMap = {
    noteManager.writeNoteDefinition: lambda config: not config[F_DEFINITION],
    noteManager.writeNoteSentence: lambda config: not config[F_SENTENCE],
    noteManager.writeNotePhrase: lambda config: not config[F_PHRASE],
    noteManager.writeNoteImage: lambda config: not config[F_IMAGE],
    noteManager.writeNoteBrEPhonetic: lambda config: not config[F_BREPHONETIC],
    noteManager.writeNoteAmEPhonetic: lambda config: not config[F_AMEPHONETIC],
    noteManager.writeNotePron: lambda config: config[F_NOPRON],
}


def _getAudioFileNameFromField(word: str, fieldVal: str) -> str:
    if (
        fieldVal
        and (
            m := re.search(
                rf"^\[sound:({F_AMEPRON}_{word}\.mp3|{F_BREPRON}_{word}\.mp3)\]$",
                fieldVal,
            )
        )
        and len(grp := m.groups()) == 1
    ):
        _logger.debug(
            f"__getAudioFileNameFromField matched, word='{word}', fieldVal='{fieldVal}'"
        )
        return grp[0]
    _logger.debug(
        f"__getAudioFileNameFromField didn't matched, word='{word}', fieldVal='{fieldVal}'"
    )
    return ""


class _CntGrp:
    def __init__(self):
        self.reset()

    def reset(self):
        self._successCnt = 0
        self._failCnt = 0

    def getSuccessCnt(self):
        return self._successCnt

    def incSuccessCnt(self):
        self._successCnt += 1

    def getFailCnt(self):
        return self._failCnt

    def incFailCnt(self):
        self._failCnt += 1


class NoteFixer:

    def __init__(self, windows: Windows):
        self._w = windows
        self._queryCntGrp = _CntGrp()
        self._audioCntGrp = _CntGrp()
        self._notes = []
        self._queryResults = []
        self._fieldFns = []
        self._queryWorker = None
        self._audioWorker = None
        self._w.noteFixBtn.clicked.connect(self._on_noteFixBtnClick)

    def _formatStrFromCurrentConfig(self) -> str:
        config = self._w.currentConfig

        def pronStr():
            if config[F_NOPRON]:
                return "无"
            elif config[F_BREPRON]:
                return "英"
            else:
                return "美"

        return rf"""默认设置:
        Deck：{config['deck']}
        查词API：{self._w.getQueryApiByCurrentConfig().name}
        释义：{config[F_DEFINITION]}
        例句：{config[F_SENTENCE]}
        短语：{config[F_PHRASE]}
        图片：{config[F_IMAGE]}
        英式音标：{config[F_BREPHONETIC]}
        美式音标：{config[F_AMEPHONETIC]}
        发音：{pronStr()}"""

    def _writeLogAndLabel(self, msg: str, label: aqt.QLabel):
        _logger.info(msg)
        label.setText(msg)

    def _UISetEnabled(self, b):
        self._w.noteFixBtn.setEnabled(b)
        self._w.noteFixCBGroupBox.setEnabled(b)
        self._w.resetProgressBar(1)

    def _getWriteFieldFnsFromUI(self):
        self._fieldFns = []

        if self._w.noteFixDefCB.isChecked():
            self._fieldFns.append(noteManager.writeNoteDefinition)

        if self._w.noteFixSentenceCB.isChecked():
            self._fieldFns.append(noteManager.writeNoteSentence)

        if self._w.noteFixPhraseCB.isChecked():
            self._fieldFns.append(noteManager.writeNotePhrase)

        if self._w.noteFixImgCB.isChecked():
            self._fieldFns.append(noteManager.writeNoteImage)

        if self._w.noteFixBrEPhoneticCB.isChecked():
            self._fieldFns.append(noteManager.writeNoteBrEPhonetic)

        if self._w.noteFixAmEPhoneticCB.isChecked():
            self._fieldFns.append(noteManager.writeNoteAmEPhonetic)

        if self._w.noteFixPronCB.isChecked():
            self._fieldFns.append(noteManager.writeNotePron)

    # @aqt.pyqtSlot()
    # decorating a pyqtSlot here will cause anki crash without any stacktrace information,
    # will be very appreciated if anyone can explains this
    def _on_noteFixBtnClick(self):
        self._getWriteFieldFnsFromUI()
        if not self._fieldFns:
            aqt.utils.showInfo("请勾选要修复的字段")
            return

        self._w.setCurrentConfigFromUI()
        if not aqt.utils.askUser(
            f"{self._formatStrFromCurrentConfig()}\n\n可能要花费较长时间，是否继续?"
        ):
            return

        if not self._checkLoginState():
            self._writeLogAndLabel("请在登录后重试", self._w.noteFixProgressNoteLabel)
            return

        self._fix()

    def _checkLoginState(self) -> bool:
        self._writeLogAndLabel("正在检查登录信息...", self._w.noteFixProgressNoteLabel)
        currentApi = self._w.getQueryApiByCurrentConfig()
        currentDict = self._w.getDictByCurrentConfig()

        if currentApi == queryApi.eudict.API:
            if currentDict != dictionary.eudict.Eudict:
                aqt.utils.showCritical(
                    f"当前选择的是[{queryApi.eudict.API.name}]，请前往[同步]页面选择[{dictionary.eudict.Eudict.name}]以获取登录信息"
                )
                return False
            else:
                if currentDict.checkCookie(
                    json.loads(str(self._w.currentConfig["cookie"]) or "{}")
                ):
                    return True
                else:
                    self._w.simpleLogin()
                    return False

        else:
            return True

    def _fix(self):
        self._UISetEnabled(False)
        self._w.noteFixProgressQueryLabel.clear()
        self._w.noteFixProgressAudioLabel.clear()
        self._writeLogAndLabel("开始修复...", self._w.noteFixProgressNoteLabel)
        self._queryCntGrp.reset()
        self._audioCntGrp.reset()

        self._notes = noteManager.getNotesByDeckName(
            self._w.currentConfig["deck"], noteManager.noteFilterByModelName
        )
        self._queryResults: list[Any] = [None] * len(self._notes)
        self._writeLogAndLabel(
            f"找到{len(self._notes)}条笔记...", self._w.noteFixProgressNoteLabel
        )

        if self._removeOnly():
            self._updateNotes()
            self._endTask(
                "仅清空字段，跳过查询API和发音下载", self._w.noteFixProgressAudioLabel
            )
            return

        self._queryWords(self._notes)

    def _removeOnly(self):
        ret = True
        for fn in self._fieldFns:
            ret = ret & _fieldConfigRemoveOnlyMap[fn](self._w.currentConfig)
        return ret

    def _queryWords(self, notes):
        row_words: list[Any] = [None] * len(notes)
        for i, note in enumerate(notes):
            row_words[i] = (i, note[F_TERM])

        if not row_words:
            self._endTask(
                f"单词查询[完成]，无任务",
                self._w.noteFixProgressQueryLabel,
            )
            return

        self._w.resetProgressBar(len(row_words), self._w.getDictByCurrentConfig().name)
        self._writeLogAndLabel(
            f"开始调用{self._w.getDictByCurrentConfig().name}，单词数量：{len(notes)}...",
            self._w.noteFixProgressQueryLabel,
        )

        self._queryWorker = QueryWorker(row_words, self._w.getQueryApiByCurrentConfig())
        self._queryWorker.rowSuccess.connect(self._on_queryRowSuccess)
        self._queryWorker.rowFail.connect(self._on_queryRowFail)
        self._queryWorker.tick.connect(self._queryRowTick)
        self._queryWorker.done.connect(self._on_queryDone)
        aqt.operations.QueryOp(
            parent=self._w,
            op=lambda col: self._queryWorker.run(),  # type: ignore
            success=lambda _: None,
        ).failure(self._on_queryFail).without_collection().run_in_background()

    def _on_queryRowSuccess(self, row_word, queryResult):
        row, word = row_word
        self._queryResults[row] = queryResult
        self._queryCntGrp.incSuccessCnt()

    def _on_queryRowFail(self, row_word):
        row, word = row_word
        self._queryResults[row] = None
        self._queryCntGrp.incFailCnt()

    def _queryRowTick(self):
        self._w.progressBar.setValue(self._w.progressBar.value() + 1)

    def _on_queryFail(self, e):
        self._endTask(f"单词查询[失败]，异常：{e}", self._w.noteFixProgressQueryLabel)

    def _on_queryDone(self, _):
        self._writeLogAndLabel(
            f"单词查询[完成]，成功{self._queryCntGrp.getSuccessCnt()}，失败{self._queryCntGrp.getFailCnt()}",
            self._w.noteFixProgressQueryLabel,
        )

        self._updateNotes()
        self._downloadAudios()

    def _updateNotes(self):
        for i, note in enumerate(self._notes):
            noteManager.writeNoteFields(
                note,
                self._queryResults[i],
                self._w.currentConfig,
                self._fieldFns,
            )

        self._writeLogAndLabel(
            f"开始写入笔记更新，数量：{len(self._notes)}...",
            self._w.noteFixProgressNoteLabel,
        )

        # update notes to collection
        noteManager.updateNotes(self._notes)
        aqt.mw.reset()
        self._writeLogAndLabel(
            f"笔记更新[完成]，数量：{len(self._notes)}",
            self._w.noteFixProgressNoteLabel,
        )

    def _downloadAudios(self):
        audios = []
        whichPron: Optional[str] = None
        if not self._w.currentConfig[F_NOPRON]:
            whichPron = F_AMEPRON if self._w.currentConfig[F_AMEPRON] else F_BREPRON

        if whichPron:
            for i, note in enumerate(self._notes):
                if (
                    not (
                        fileName := _getAudioFileNameFromField(
                            note[F_TERM], note[whichPron]
                        )
                    )
                    or not (
                        os.path.isfile(fullName := noteManager.media_path(fileName))
                    )
                    and (queryRet := self._queryResults[i])
                    and (url := queryRet[whichPron])
                ):
                    audios.append(
                        (
                            fullName,
                            url,
                        )
                    )
        if not audios:
            self._endTask("发音下载[完成]，无任务", self._w.noteFixProgressAudioLabel)
            return

        self._w.resetProgressBar(len(audios), "发音下载")
        self._writeLogAndLabel(
            f"开始发音下载，数量：{len(audios)}...",
            self._w.noteFixProgressAudioLabel,
        )

        self._audioWorker = AudioDownloadWorker(audios)
        self._audioWorker.tick.connect(self._on_audioDownloadTick)
        self._audioWorker.done.connect(self._on_audioDownloadDone)
        aqt.operations.QueryOp(
            parent=self._w,
            op=lambda col: self._audioWorker.run(),  # type: ignore
            success=lambda _: None,
        ).failure(self._on_audioFail).without_collection().run_in_background()

    def _on_audioDownloadTick(self, audio, success):
        self._w.progressBar.setValue(self._w.progressBar.value() + 1)
        if success:
            self._audioCntGrp.incSuccessCnt()
        else:
            self._audioCntGrp.incFailCnt()

    def _on_audioDownloadDone(self, _):
        msg = f"发音下载[完成]，成功{self._audioCntGrp.getSuccessCnt()}，失败{self._audioCntGrp.getFailCnt()}"
        self._endTask(msg, self._w.noteFixProgressAudioLabel)

    def _on_audioFail(self, e):
        self._endTask(f"发音下载[失败]，异常：{e}", self._w.noteFixProgressAudioLabel)

    def _endTask(self, msg, label):
        if msg:
            self._writeLogAndLabel(msg, label)
        self._w.noteFixProgressAudioLabel.setText(
            self._w.noteFixProgressAudioLabel.text() + " . . . 笔记修复完成"
        )
        self._UISetEnabled(True)
        self._clear()

        aqt.utils.tooltip("笔记修复完成")
        aqt.mw.reset()

    def _clear(self):
        self._notes.clear()
        self._queryResults.clear()
        self._fieldFns.clear()
        self._queryWorker = None
        self._audioWorker = None
