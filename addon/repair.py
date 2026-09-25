from __future__ import annotations

import json
import logging
import typing as T

import aqt
import aqt.utils

from . import _typing as _T
from . import adv_conf, dictionary, noteManager, queryApi, workers
from . import constants as C

if T.TYPE_CHECKING:
    from .addonWindow import Windows

_logger = logging.getLogger('dict2Anki.repair')


class Stats(_T.ListenableModel):
    def __init__(self):
        super().__init__()
        self._total = 0
        self._success_cnt = 0
        self._fail_cnt = 0

    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, val: int):
        "trigger `total` event, `self` as event parameter"
        self._total = val
        self._notify('total', self)

    @property
    def success_cnt(self):
        return self._success_cnt

    @success_cnt.setter
    def success_cnt(self, val: int):
        "trigger `success_cnt` event, `self` as event parameter"
        self._success_cnt = val
        self._notify('success_cnt', self)

    @property
    def fail_cnt(self):
        return self._fail_cnt

    @fail_cnt.setter
    def fail_cnt(self, val: int):
        "trigger `fail_cnt` event, `self` as event parameter"
        self._fail_cnt = val
        self._notify('fail_cnt', self)

    def reset(self, total: int = 0, success_cnt: int = 0, fail_cnt: int = 0):
        "trigger `reset` event, `self` as event parameter"
        self._total = total
        self._success_cnt = success_cnt
        self._fail_cnt = fail_cnt
        self._notify('reset', self)

    def incSuccessCnt(self):
        "trigger `incSuccessCnt` event, `self` as event parameter"
        self._success_cnt += 1
        self._notify('incSuccessCnt', self)

    def incFailCnt(self):
        "trigger `incFailCnt` event, `self` as event parameter"
        self._fail_cnt += 1
        self._notify('incFailCnt', self)


class RepairModel:
    def __init__(self):
        self.query_stats = Stats()
        self.audio_stats = Stats()
        self.note_stats = Stats()


class Repair:
    def __init__(self, windows: Windows):
        self._w = windows
        self._model = RepairModel()
        self._register_model_events(self._model)
        self._notes = []
        self._query_cache_list: list[dict[str, T.Optional[_T.QueryWordData]]] = []
        'same length as self._notes'
        self._ensured_selected_dict: dict[str, adv_conf.FConfAST] = {}
        self._listen_ui_events()

    def _listen_ui_events(self):

        def on_enter_pressed():
            text = self._w.repairFilterLineEdit.text()
            note_ids = noteManager.get_note_ids(self._w.conf.deck, text)
            self._w.repairFilterLabel.setText(str(len(note_ids)))

        self._w.repairFilterLineEdit.returnPressed.connect(on_enter_pressed)
        self._w.repairBtn.clicked.connect(self._on_repairBtnClick)

    def _register_model_events(self, model: RepairModel):
        def update_label_note_reset(stats: Stats):
            self._w.repairProgressNoteLabel.setText(f'等待更新笔记，总数：{stats.total} . . . ')

        def update_label_note(stats: Stats):
            self._w.repairProgressNoteLabel.setText(f'笔记更新完成：总数 {stats.total}，标记 {stats.fail_cnt}')

        model.note_stats.listen('reset', update_label_note_reset)
        model.note_stats.listen('fail_cnt', update_label_note)

        def update_label_query(stats: Stats):
            self._w.repairProgressQueryLabel.setText(
                f'检查笔记：{stats.success_cnt + stats.fail_cnt} / {stats.total}，成功：{stats.success_cnt}，失败：{stats.fail_cnt} . . . '
            )

        model.query_stats.listen('reset', update_label_query)
        model.query_stats.listen('incSuccessCnt', update_label_query)
        model.query_stats.listen('incFailCnt', update_label_query)

        def update_label_audio(stats: Stats):
            self._w.repairProgressAudioLabel.setText(
                f'下载发音：成功：{stats.success_cnt}，失败：{stats.fail_cnt} . . . '
            )

        model.audio_stats.listen('reset', update_label_audio)
        model.audio_stats.listen('incSuccessCnt', update_label_audio)
        model.audio_stats.listen('incFailCnt', update_label_audio)

    def _warning(self) -> str:
        conf = self._w.conf

        return rf"""默认设置:

Deck：          {conf.deck}
线上单词本：    {self._w.get_current_dict().name}{conf.current_selected_groups}
查词API：       {self._w.get_current_api().name}
释义：          {conf.advanced_definition if conf.advanced_enabled else conf.definition}
例句：          {conf.advanced_sentence if conf.advanced_enabled else conf.sentence}
短语：          {conf.advanced_phrase if conf.advanced_enabled else conf.phrase}
图片：          {conf.advanced_image if conf.advanced_enabled else conf.image}
英式音标：      {conf.advanced_BrEPhonetic if conf.advanced_enabled else conf.bre_phonetic}
美式音标：      {conf.advanced_AmEPhonetic if conf.advanced_enabled else conf.ame_phonetic}
英式发音：      {conf.advanced_BrEPron if conf.advanced_enabled else conf.bre_pron}
美式发音：      {conf.advanced_AmEPron if conf.advanced_enabled else conf.ame_pron}"""

    def _writeLogAndLabel(self, msg: str, label: aqt.QLabel):
        _logger.info(msg)
        label.setText(msg)

    def _enable_ui(self, b):
        self._w.repairBtn.setEnabled(b)
        self._w.repairCBGroupBox.setEnabled(b)
        self._w.resetProgressBar(1)

    def _get_selected_field_set(self):
        selected_field_set: set[str] = set()

        if self._w.repairDefCB.isChecked():
            selected_field_set.add(C.F_DEFINITION)

        if self._w.repairSentenceCB.isChecked():
            selected_field_set.add(C.F_SENTENCE)

        if self._w.repairPhraseCB.isChecked():
            selected_field_set.add(C.F_PHRASE)

        if self._w.repairImgCB.isChecked():
            selected_field_set.add(C.F_IMAGE)

        if self._w.repairBrEPhoneticCB.isChecked():
            selected_field_set.add(C.F_BREPHONETIC)

        if self._w.repairAmEPhoneticCB.isChecked():
            selected_field_set.add(C.F_AMEPHONETIC)

        if self._w.repairBrEPronCB.isChecked():
            selected_field_set.add(C.F_BREPRON)

        if self._w.repairAmEPronCB.isChecked():
            selected_field_set.add(C.F_AMEPRON)

        return selected_field_set

    def _on_repairBtnClick(self):
        selected_field_set = self._get_selected_field_set()

        if not selected_field_set:
            aqt.utils.showInfo('请选择要修复的字段', parent=self._w)
            return

        selected_ast_dict_tuple = {
            field: ast_tuple for field, ast_tuple in self._w.conf.get_ast_dict().items() if field in selected_field_set
        }

        ast_dict, errmsg = adv_conf.ensure_ast_dict_errmsg_for_ui(selected_ast_dict_tuple)
        if errmsg:
            aqt.utils.show_critical(errmsg)
            return

        if not self._w.conf.advanced_enabled and not self._checkLoginState():
            self._writeLogAndLabel('请在登录后重试', self._w.repairProgressNoteLabel)
            return

        _logger.info(self._w.conf.print())
        if not aqt.utils.askUser(f'{self._warning()}\n\n可能要花费较长时间，是否继续?', parent=self._w):
            return

        self._ensured_selected_dict = ast_dict
        self._repair()

    def _checkLoginState(self) -> bool:
        self._writeLogAndLabel('正在检查登录信息 . . .', self._w.repairProgressNoteLabel)
        currentApi = self._w.get_current_api()
        currentDict = self._w.get_current_dict()

        if currentApi == queryApi.eudict.API:
            if currentDict != dictionary.eudict.Dict:
                aqt.utils.showCritical(
                    f'当前选择的是[{queryApi.eudict.API.name}]，请前往[同步]页面选择[{dictionary.eudict.Dict.name}]以获取登录信息'
                )
                return False
            else:
                if currentDict.checkCookie(json.loads(str(self._w.conf.current_cookies) or '{}')):
                    return True
                else:
                    self._w.simpleLogin()
                    return False

        else:
            return True

    def _repair(self):
        self._enable_ui(False)
        self._w.repairProgressQueryLabel.clear()
        self._w.repairProgressAudioLabel.clear()

        self._notes = list(noteManager.getNotesByDeckName(self._w.conf.deck, self._w.repairFilterLineEdit.text()))
        if len(self._notes) == 0:
            self._writeLogAndLabel('没有要更新的笔记', self._w.repairProgressNoteLabel)
            return self._complete(None, None)

        self._model.note_stats.reset(len(self._notes))
        self._queryWords(self._notes)

    def _queryWords(self, notes):
        self._query_cache_list = [{}] * len(notes)
        row_words: list[tuple[int, str]] = [(0, '')] * len(notes)

        for i, note in enumerate(notes):
            row_words[i] = (i, note[C.F_TERM])

        self._w.resetProgressBar(len(row_words))
        self._model.query_stats.reset(len(row_words))
        self._model.audio_stats.reset(0)

        worker = workers.ApiASTWorker(row_words, self._ensured_selected_dict, self._w.conf.congest, parent=self._w)
        worker.rowSuccess.connect(self._on_queryRowSuccess)
        worker.rowFail.connect(self._on_queryRowFail)
        worker.done.connect(self._on_queryDone)
        self._w.workerman.start(worker)

    def _on_queryRowSuccess(self, row, _word, query_cache):
        self._model.query_stats.incSuccessCnt()
        self._query_cache_list[row] = query_cache
        self._w.progressBar.setValue(self._w.progressBar.value() + 1)

    def _on_queryRowFail(self, row, _word, query_cache):
        self._model.query_stats.incFailCnt()
        self._query_cache_list[row] = query_cache
        self._w.progressBar.setValue(self._w.progressBar.value() + 1)

    def _on_queryDone(self, _worker):
        # update notes, set flag, move mp3 files
        flaged = 0
        for i, query_cache in enumerate(self._query_cache_list):
            note = self._notes[i]
            word = note[C.F_TERM]
            flag_ref = [-1]

            adv_conf.eval_asts_set_note(word, note, query_cache, self._ensured_selected_dict, flag_ref)

            if flag_ref[0] >= 0:
                flaged += 1

            def move_audio(word: str, field: str):
                if ast := self._ensured_selected_dict.get(field):
                    if ast.eval(adv_conf.MoveAudioFConfVisitor(word, field)):
                        self._model.audio_stats.incSuccessCnt()
                    else:
                        self._model.audio_stats.incFailCnt()

            # move audio file
            move_audio(word, C.F_AMEPRON)
            move_audio(word, C.F_BREPRON)

        noteManager.updateNotes(self._notes)
        self._model.note_stats.fail_cnt = flaged
        self._complete(None, None)

    def _complete(self, msg, label):
        if msg:
            self._writeLogAndLabel(msg, label)
        self._enable_ui(True)
        self._clear()
        aqt.mw.reset()

        aqt.utils.tooltip('修复完成')

    def _clear(self):
        self._notes.clear()
        self._query_cache_list.clear()
        self._ensured_selected_dict.clear()
