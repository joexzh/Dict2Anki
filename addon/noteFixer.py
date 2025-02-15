import os
from typing import Optional
import aqt
import aqt.utils
import aqt.operations.note
import aqt.operations
import re
import logging
from .addonWindow import Windows
from . import noteManager
from .__typing import QueryWordData
from .constants import *
from .workers import QueryWorker, AudioDownloadWorker


def __getAudioFileNameFromField(word: str, fieldVal: str):
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
        return grp[0]
    return ""


def __getWriteFieldFnsFromUI() -> list[noteManager.writeNoteFnType]:
    # TODO
    return []


class __CntGrp:
    def __init__(self):
        self.reset()

    def reset(self):
        self.__successCnt = 0
        self.__failCnt = 0

    def getSuccessCnt(self):
        return self.__successCnt

    def incSuccessCnt(self):
        self.__successCnt += 1

    def getFailCnt(self):
        return self.__failCnt

    def incFailCnt(self):
        self.__failCnt += 1


class NoteFixer:
    logger = logging.getLogger("dict2Anki.noteFixer")

    def __init__(self, windows: Windows):
        self.__windows = windows
        self.__notes: list
        self.__queryResults: list[QueryWordData]
        self.__queryCntGrp = __CntGrp()
        self.__audioCntGrp = __CntGrp()

        self.__windows.noteFixBtn.clicked.connect(self.__on_noteFixBtnClick)

    def __formatStrFromCurrentConfig(self) -> str:
        config = self.__windows.currentConfig

        def pronStr():
            if config[F_NOPRON]:
                return "无"
            elif config[F_BREPRON]:
                return "英"
            else:
                return "美"

        return rf"""默认设置:
        Deck: {config['deck']}
        查词API: {self.__windows.getQueryApiByCurrentConfig().name}
        释义{config[F_DEFINITION]}
        例句{config[F_SENTENCE]}
        短语{config[F_PHRASE]}
        图片{config[F_IMAGE]}
        英式音标{config[F_BREPHONETIC]}
        美式音标{config[F_AMEPHONETIC]}
        发音{pronStr()}"""

    def __writeLogAndLabel(self, msg: str, label: aqt.QLabel):
        self.logger.info(msg)
        label.setText(msg)

    def __UISetEnabled(self, b):
        self.__windows.noteFixBtn.setEnabled(b)
        self.__windows.noteFixCBGroupBox.setEnabled(b)

    @aqt.pyqtSlot()
    def __on_noteFixBtnClick(self):
        writeFieldFns = __getWriteFieldFnsFromUI()
        if not writeFieldFns:
            aqt.utils.showInfo("请勾选要修复的字段")

        if not aqt.utils.askUser(
            f"{self.__formatStrFromCurrentConfig()}\n\n可能要花费较长时间，是否继续?"
        ):
            return

        self.__UISetEnabled(False)
        self.__windows.noteFixProgressQueryLabel.setText("")
        self.__windows.noteFixProgressAudioLabel.setText("")
        self.__writeLogAndLabel("开始修复...", self.__windows.noteFixProgressNoteLabel)

        self.__windows.setCurrentConfigFromUI()

        self.__notes = noteManager.getNotesByDeckName(
            self.__windows.currentConfig["deck"], noteManager.noteFilterByModelName
        )

        wordList = [] * len(self.__notes)
        for i, note in enumerate(self.__notes):
            wordList[i] = {F_TERM: note[F_TERM], "row": i}

        self.__queryResults = [] * len(self.__notes)
        self.__queryCntGrp.reset()

        self.__windows.resetProgressBar(len(wordList))

        # spawn another thread to query words
        queryWorker = QueryWorker(wordList, self.__windows.getQueryApiByCurrentConfig())
        queryWorker.oneRowDone.connect(self.__on_queryOneRowDone)
        aqt.operations.QueryOp(
            parent=self.__windows,
            op=lambda col: queryWorker.run(),
            success=self.__on_querySuccess,
        ).failure(
            lambda e: self.__on_queryFail(len(self.__notes), e)
        ).without_collection().run_in_background()

        self.__writeLogAndLabel(
            f"找到{len(self.__notes)}条笔记...", self.__windows.noteFixProgressNoteLabel
        )
        self.__writeLogAndLabel(
            f"开始调用查询 API，单词数量：{len(self.__notes)}...",
            self.__windows.noteFixProgressQueryLabel,
        )

    def __on_queryOneRowDone(self, word, row, queryResult):
        self.__windows.progressBar.setValue(self.__windows.progressBar.value() + 1)
        if queryResult:  # success
            self.__queryCntGrp.incSuccessCnt()
        else:  # fail
            self.__queryCntGrp.incFailCnt()
        self.__queryResults[row] = queryResult

    def __on_queryFail(self, total: int, e: Exception):
        self.__writeLogAndLabel(
            f"单词查询[意外结束]，共{total}，成功{self.__queryCntGrp.getSuccessCnt}，失败{self.__queryCntGrp.getSuccessCnt}, 异常：{e}",
            self.__windows.noteFixProgressQueryLabel,
        )

        self.__UISetEnabled(True)

    def __on_querySuccess(
        self, _  # "_" is for passing type check as a QueryOp success callback
    ):
        self.__writeLogAndLabel(
            f"单词查询[完成]，成功{self.__queryCntGrp.getSuccessCnt}，失败{self.__queryCntGrp.getSuccessCnt}",
            self.__windows.noteFixProgressQueryLabel,
        )

        audios = []
        pronField: Optional[str] = None
        if not self.__windows.currentConfig[F_NOPRON]:
            pronField = (
                F_AMEPRON if self.__windows.currentConfig[F_AMEPRON] else F_BREPRON
            )

        for i, note in enumerate(self.__notes):
            # write changes to notes
            noteManager.writeNoteFields(
                note,
                self.__queryResults[i],
                self.__windows.currentConfig,
                __getWriteFieldFnsFromUI(),
            )

            if pronField:
                # prepare audios
                if (
                    not (
                        fileName := __getAudioFileNameFromField(
                            note[F_TERM], note[pronField]
                        )
                    )
                    or not (
                        fullName := os.path.isfile(noteManager.media_path(fileName))
                    )
                    and (queryRet := self.__queryResults[i])
                    and queryRet[pronField]
                ):
                    audios.append(
                        (
                            fullName,
                            queryRet[pronField],  # url
                        )
                    )

            self.__windows.resetProgressBar(len(audios))

            # spawn another thread to download audio
            audioWorker = AudioDownloadWorker(audios)
            audioWorker.tick.connect(self.__on_audioDownloadTick)
            aqt.operations.QueryOp(
                parent=self.__windows,
                op=lambda col: audioWorker.run(),
                success=self.__on_audioDownloadSuccess,
            ).failure(
                lambda e: self.__on_audioDownloadFail(len(audios), e)
            ).without_collection().run_in_background()

            # update note to collection
            aqt.operations.note.update_notes(
                parent=self.__windows, notes=self.__notes
            ).success(
                lambda _: self.__on_noteUpdateSuccess(_, len(self.__notes))
            ).failure(
                self.__on_noteUpdateFail
            ).run_in_background()

            self.__writeLogAndLabel(
                f"开始写入笔记更新，数量：{len(self.__notes)}...",
                self.__windows.noteFixProgressNoteLabel,
            )
            self.__writeLogAndLabel(
                f"开始下载发音，数量：{len(audios)}...",
                self.__windows.noteFixProgressAudioLabel,
            )

    def __on_noteUpdateFail(self, e: Exception):
        self.__writeLogAndLabel(
            f"笔记更新[失败]，异常：{e}", self.__windows.noteFixProgressNoteLabel
        )

    def __on_noteUpdateSuccess(self, _, total: int):
        self.__writeLogAndLabel(
            f"笔记更新[完成]，数量：{total}", self.__windows.noteFixProgressNoteLabel
        )

    def __on_audioDownloadTick(self, fileName, url, success):
        if success:
            self.__audioCntGrp.incSuccessCnt()
        else:
            self.__audioCntGrp.incFailCnt()

    def __on_audioDownloadFail(self, total: int, e: Exception):
        self.__writeLogAndLabel(
            f"发音下载[意外退出]，共{total}，成功{self.__audioCntGrp.getSuccessCnt()}，失败{self.__audioCntGrp.getFailCnt()}，异常：{e}",
            self.__windows.noteFixProgressAudioLabel,
        )

        self.__UISetEnabled(True)

    def __on_audioDownloadSuccess(self, _):
        self.__writeLogAndLabel(
            f"发音下载[完成]，成功{self.__audioCntGrp.getSuccessCnt()}，失败{self.__audioCntGrp.getFailCnt()}",
            self.__windows.noteFixProgressAudioLabel,
        )

        self.__UISetEnabled(True)
        aqt.utils.tooltip("修复完成")
