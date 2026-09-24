import os

import aqt.utils
import pytest
from pytest import MonkeyPatch as MP

from addon import constants as C
from addon import misc, noteManager, queryApi, repair, workers
from addon.addonWindow import Windows

from . import helper, mock_helper
from .dummy_aqt import notes
from .mock_helper import w_mock


def test_model_init_zero():
    g = repair.Stats()
    assert g.total == 0
    assert g.success_cnt == 0
    assert g.fail_cnt == 0


def test_model_reset():
    g = repair.Stats()
    g.reset(111, 222, 333)
    assert g.total == 111
    assert g.success_cnt == 222
    assert g.fail_cnt == 333


def test_model_reset_listen():
    g = repair.Stats()
    expected = 1
    assert_val = 0

    def callback(grp):
        nonlocal assert_val
        assert_val = grp.total

    g.listen('reset', callback)
    g.reset(expected)

    assert assert_val == expected


def test_model_incSuccessCnt():
    g = repair.Stats()
    g.incSuccessCnt()
    assert g.success_cnt == 1


def test_model_incSuccessCnt_listen():
    g = repair.Stats()
    expected = 1
    assert_val = 0

    def callback(grp):
        nonlocal assert_val
        assert_val = grp.success_cnt

    g.listen('incSuccessCnt', callback)
    g.incSuccessCnt()

    assert assert_val == expected


def test_model_incFailCnt():
    g = repair.Stats()
    g.incFailCnt()
    assert g.fail_cnt == 1


def test_model_incFailCnt_listen():
    g = repair.Stats()
    expected = 1
    assert_val = 0

    def callback(grp):
        nonlocal assert_val
        assert_val = grp.fail_cnt

    g.listen('incFailCnt', callback)
    g.incFailCnt()

    assert assert_val == expected


@pytest.mark.parametrize(
    'case, field_config, visit_api_return, n_notes, expected_mv_file_called',
    [
        (1, 'api:"有道 API"', True, 100, 200),
        (2, 'api:"有道 API" | api:"欧路词典 API" | flag:1', False, 100, 400),
        (3, 'wrong', True, 100, 0),
        (4, '', True, 100, 0),
    ],
)
def test_query(
    monkeypatch: MP,
    w_mock,
    qtbot,
    case: int,
    field_config: str,
    visit_api_return: bool,
    n_notes: int,
    expected_mv_file_called: int,
):
    """
    ## param set 1
    all field config: `api:"有道 API"`
    all visit_api functions return True
    notes have initial value
    Test:
    - notes should be modified
    - misc.mv_file should be called n_notes * 2 times

    ## param set 2
    all field config: `api:"有道 API" | api:"欧路词典 API" | flag:1`
    all visit_api functions return False
    notes have initial value
    Test:
    - notes should not be modified
    - notes should be flagged
    - misc.mv_file should be called n_notes * 4 times (each note has 2 pron
      field, each field has 2 API)

    ## param set 3
    all field config: `wrong` (wrong format)
    Test: aqt.utils.show_critical should be called

    ## param set 4
    all field config: (empty)
    notes have initial value
    Test:
    - notes should be wiped out
    - misc.mv_file should be called 0 times
    """

    field_val = 'Leeroy Jenkins'
    notes_ = []

    def mock_notes(*args, **kwargs):
        for i in range(n_notes):
            note = notes.Note(1)
            for f in C.MODEL_FIELDS:
                note[f] = field_val
            notes_.append(note)
        return notes_

    # all note fields has value `Leeroy Jenkins`
    monkeypatch.setattr(noteManager, 'getNotesByDeckName', mock_notes)

    # By default query_data has value, return None only in this case
    if visit_api_return is False:

        def mock_query_data_none(*args, **kwargs):
            return None

        monkeypatch.setattr(queryApi.youdao.API, 'query', mock_query_data_none)
        monkeypatch.setattr(queryApi.eudict.API, 'query', mock_query_data_none)

        # to make MoveAudioFConfVisitor.visit_api return False
        monkeypatch.setattr(misc, 'mv_file', helper.MockCallable(return_value=False))

    w: Windows = w_mock()
    r = w.repair
    model = r._model
    qtbot.addWidget(w)

    w.conf.advanced_enabled = True
    w.conf.advanced_definition = field_config
    w.conf.advanced_sentence = field_config
    w.conf.advanced_phrase = field_config
    w.conf.advanced_image = field_config
    w.conf.advanced_AmEPhonetic = field_config
    w.conf.advanced_BrEPhonetic = field_config
    w.conf.advanced_AmEPron = field_config
    w.conf.advanced_BrEPron = field_config

    monkeypatch.setattr(r, '_checkLoginState', lambda *args, **kwargs: True)

    w.repairDefCB.setChecked(True)
    w.repairPhraseCB.setChecked(True)
    w.repairSentenceCB.setChecked(True)
    w.repairImgCB.setChecked(True)
    w.repairAmEPhoneticCB.setChecked(True)
    w.repairBrEPhoneticCB.setChecked(True)
    w.repairPronCB.setChecked(True)

    w.repairBtn.click()

    def check_show_critical():
        assert aqt.utils.show_critical.called

    if case == 3:
        qtbot.waitUntil(check_show_critical)
        return

    def check_tooltip():
        assert aqt.utils.tooltip.called_with == (('修复完成',), {})

    # wait until finish tooltip
    qtbot.waitUntil(check_tooltip)

    if case == 1:
        # notes should be modified, pick the first note to check
        assert (
            notes_[0][C.F_DEFINITION]
            == f'<div class="definition">{mock_helper.query_data_mock[C.F_DEFINITION][0]}</div>'
        )
    elif case == 2:
        # notes should not be modified, pick the first note to check
        assert notes_[0][C.F_DEFINITION] == field_val

        # all notes are flagged
        assert model.note_stats.fail_cnt == n_notes
        # all move audios failed, n_notes * 2: us and en pron
        assert model.audio_stats.fail_cnt == n_notes * 2
    elif case == 4:
        # notes should be wiped, pick the first to check
        assert notes_[0][C.F_DEFINITION] == ''

    assert misc.mv_file.called == expected_mv_file_called
    assert model.note_stats.total == n_notes
