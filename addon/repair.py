import json
import logging
import os
from typing import Any, Callable, Optional

import aqt
import aqt.utils

from . import conf_model, dictionary, misc, noteManager, queryApi, workers
from ._typing import ListenableModel, QueryWordData
from .addonWindow import Windows
from .constants import *

_logger = logging.getLogger("dict2Anki.repair")


_write_fn_valid_map: dict[
    noteManager.writeNoteFnType, Callable[[conf_model.Conf], bool]
] = {
    noteManager.writeNoteDefinition: lambda conf: not conf.definition,
    noteManager.writeNoteSentence: lambda conf: not conf.sentence,
    noteManager.writeNotePhrase: lambda conf: not conf.phrase,
    noteManager.writeNoteImage: lambda conf: not conf.image,
    noteManager.writeNoteBrEPhonetic: lambda conf: not conf.bre_phonetic,
    noteManager.writeNoteAmEPhonetic: lambda conf: not conf.ame_phonetic,
    noteManager.writeNotePron: lambda conf: conf.no_pron,
}
"""Provides lambdas to check whether a write function is needed."""


class CntGrp(ListenableModel):
    def __init__(self):
        super().__init__()
        self._total = 0
        self._success_cnt = 0
        self._fail_cnt = 0

    @property
    def total(self):
        return self._total

    @property
    def success_cnt(self):
        return self._success_cnt

    @property
    def fail_cnt(self):
        return self._fail_cnt

    def reset(self, total: int = 0, success_cnt: int = 0, fail_cnt: int = 0):
        """triggers `reset` event, `self` as event argument"""
        self._total = total
        self._success_cnt = success_cnt
        self._fail_cnt = fail_cnt
        self._notify("reset", self)

    def incSuccessCnt(self):
        """triggers `incSuccessCnt` event, `self` as event argument"""
        self._success_cnt += 1
        self._notify("incSuccessCnt", self)

    def incFailCnt(self):
        """triggers `incFailCnt` event, `self` as event argument"""
        self._fail_cnt += 1
        self._notify("incFailCnt", self)


class RepairModel:
    def __init__(self):
        self.queryGrp = CntGrp()
        self.audioGrp = CntGrp()
        self.noteGrp = CntGrp()


class Repair:

    def __init__(self, windows: Windows, model: RepairModel):
        self._w = windows
        self._model = model
        self._register_model_events(self._model)
        self._notes = []
        self._write_fns = []
        self._whichPron = None
        self._api_name = ""
        self._w.repairBtn.clicked.connect(self._on_repairBtnClick)

    def _register_model_events(self, model: RepairModel):
        def update_label_note(grp: CntGrp):
            self._w.repairProgressNoteLabel.setText(
                f"更新本地笔记：{grp.success_cnt} / {grp.total} . . . "
            )

        model.noteGrp.listen("reset", update_label_note)
        model.noteGrp.listen("incSuccessCnt", update_label_note)

        def update_label_query(grp: CntGrp):
            self._w.repairProgressQueryLabel.setText(
                f"调用{self._api_name}：{grp.success_cnt + grp.fail_cnt} / {grp.total}，成功：{grp.success_cnt}，失败：{grp.fail_cnt} . . . "
            )

        model.queryGrp.listen("reset", update_label_query)
        model.queryGrp.listen("incSuccessCnt", update_label_query)
        model.queryGrp.listen("incFailCnt", update_label_query)

        def update_label_audio(grp: CntGrp):
            self._w.repairProgressAudioLabel.setText(
                f"下载发音，成功：{grp.success_cnt}，失败：{grp.fail_cnt} . . . "
            )

        model.audioGrp.listen("reset", update_label_audio)
        model.audioGrp.listen("incSuccessCnt", update_label_audio)
        model.audioGrp.listen("incFailCnt", update_label_audio)

    def _warning(self) -> str:
        conf = self._w.conf

        def pronStr():
            if conf.no_pron:
                return "无"
            elif conf.bre_pron:
                return "英"
            else:
                return "美"

        return rf"""默认设置:
        Deck：{conf.deck}
        查词API：{self._w.get_current_api().name}
        释义：{conf.definition}
        例句：{conf.sentence}
        短语：{conf.phrase}
        图片：{conf.image}
        英式音标：{conf.bre_phonetic}
        美式音标：{conf.ame_phonetic}
        发音：{pronStr()}"""

    def _writeLogAndLabel(self, msg: str, label: aqt.QLabel):
        _logger.info(msg)
        label.setText(msg)

    def _UISetEnabled(self, b):
        self._w.repairBtn.setEnabled(b)
        self._w.repairCBGroupBox.setEnabled(b)
        self._w.resetProgressBar(1)

    def _get_write_fns(self):
        fns = []

        if self._w.repairDefCB.isChecked():
            fns.append(noteManager.writeNoteDefinition)

        if self._w.repairSentenceCB.isChecked():
            fns.append(noteManager.writeNoteSentence)

        if self._w.repairPhraseCB.isChecked():
            fns.append(noteManager.writeNotePhrase)

        if self._w.repairImgCB.isChecked():
            fns.append(noteManager.writeNoteImage)

        if self._w.repairBrEPhoneticCB.isChecked():
            fns.append(noteManager.writeNoteBrEPhonetic)

        if self._w.repairAmEPhoneticCB.isChecked():
            fns.append(noteManager.writeNoteAmEPhonetic)

        if self._w.repairPronCB.isChecked():
            fns.append(noteManager.writeNotePron)

        return fns

    def _on_repairBtnClick(self):
        self._write_fns = self._get_write_fns()
        if not self._write_fns:
            aqt.utils.showInfo("请勾选要修复的字段")
            return

        _logger.info(self._w.conf.print())
        if not aqt.utils.askUser(f"{self._warning()}\n\n可能要花费较长时间，是否继续?"):
            return

        if not self._checkLoginState():
            self._writeLogAndLabel("请在登录后重试", self._w.repairProgressNoteLabel)
            return

        self._repair()

    def _checkLoginState(self) -> bool:
        self._writeLogAndLabel(
            "正在检查登录信息 . . .", self._w.repairProgressNoteLabel
        )
        currentApi = self._w.get_current_api()
        currentDict = self._w.get_current_dict()

        if currentApi == queryApi.eudict.API:
            if currentDict != dictionary.eudict.Eudict:
                aqt.utils.showCritical(
                    f"当前选择的是[{queryApi.eudict.API.name}]，请前往[同步]页面选择[{dictionary.eudict.Eudict.name}]以获取登录信息"
                )
                return False
            else:
                if currentDict.checkCookie(
                    json.loads(str(self._w.conf.current_cookies) or "{}")
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
        self._api_name = self._w.get_current_api().name

        self._notes = noteManager.getNotesByDeckName(
            self._w.conf.deck, noteManager.noteFilterByModelName
        )
        if len(self._notes) == 0:
            self._writeLogAndLabel(
                f"没有要更新的笔记 . . . ", self._w.repairProgressNoteLabel
            )
            return self._complete(None, None)

        self._model.noteGrp.reset(len(self._notes))
        if self._removeOnly():
            self._updateNotes(self._notes)
            return self._complete(
                "仅清空字段，跳过查询API和发音下载 . . . ",
                self._w.repairProgressAudioLabel,
            )

        self._queryWords(self._notes)

        self._whichPron: Optional[str] = None
        if not self._w.conf.no_pron:
            self._whichPron = F_AMEPRON if self._w.conf.ame_pron else F_BREPRON

    def _removeOnly(self):
        ret = True
        for fn in self._write_fns:
            ret = ret & _write_fn_valid_map[fn](self._w.conf)
        return ret

    def _queryWords(self, notes):
        row_words: list[Any] = [None] * len(notes)
        for i, note in enumerate(notes):
            row_words[i] = (i, note[F_TERM])

        self._w.resetProgressBar(len(row_words))
        self._model.queryGrp.reset(len(row_words))
        self._model.audioGrp.reset(0)

        worker = workers.QueryWorker(
            row_words, self._w.get_current_api(), self._w.conf.congest
        )
        worker.rowSuccess.connect(self._on_queryRowSuccess)
        worker.rowFail.connect(self._on_queryRowFail)
        worker.tick.connect(self._queryRowTick)
        worker.doneWithResult.connect(self._on_queryDone)
        self._w.workerman.start(worker)

    def _on_queryRowSuccess(self, row, word, queryResult):
        self._model.queryGrp.incSuccessCnt()

        self._updateOneNote(self._notes[row], queryResult)
        assert aqt.mw.col
        aqt.mw.col.update_note(self._notes[row])
        self._model.noteGrp.incSuccessCnt()

        self._downloadAudio(self._notes[row], queryResult)

    def _on_queryRowFail(self, row, word):
        self._model.queryGrp.incFailCnt()

    def _queryRowTick(self):
        self._w.progressBar.setValue(self._w.progressBar.value() + 1)

    def _on_queryDone(self, _):
        self._complete(None, None)

    def _updateOneNote(self, note, queryResult):
        noteManager.writeNoteFields(note, queryResult, self._w.conf, self._write_fns)

    def _updateNotes(self, notes):
        """remove only"""

        for i, note in enumerate(notes):
            self._updateOneNote(note, None)

        # update notes to collection
        noteManager.updateNotes(notes)
        self._model.noteGrp.reset(self._model.noteGrp.total, len(notes))

    def _downloadAudio(self, note, queryResult: QueryWordData):
        if not self._whichPron:
            return

        if (
            queryResult
            and (url := queryResult[self._whichPron])
            and not (
                os.path.isfile(
                    filePath := noteManager.media_path(
                        misc.audio_fname(self._whichPron, note[F_TERM])
                    )
                )
            )
        ):
            worker = AudioDownloadSingleWorker(filePath, url)
            worker.tick.connect(self._on_audioDownloadTick)
            self._w.workerman.start(worker)

    def _on_audioDownloadTick(self, fileName, url, success):
        if success:
            self._model.audioGrp.incSuccessCnt()
        else:
            self._model.audioGrp.incFailCnt()

    def _complete(self, msg, label):
        if msg:
            self._writeLogAndLabel(msg, label)
        self._UISetEnabled(True)
        self._clear()
        aqt.mw.reset()

        aqt.utils.tooltip("修复完成")

    def _clear(self):
        self._notes.clear()
        self._write_fns.clear()


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


def make_repair(win):
    return Repair(win, RepairModel())
