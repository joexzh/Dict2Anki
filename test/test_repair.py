import os

import aqt.utils
import pytest

from ..addon import noteManager, queryApi, repair, workers
from ..addon.addonWindow import Windows
from . import mock_helper
from .dummy_aqt import notes


class RepairMock:
    def __init__(self, monkeypatch, w_mock: mock_helper.WindowMock):
        self.w_mock = w_mock

    def __call__(self, windows, model):
        return repair.Repair(windows, model)


@pytest.fixture
def r_mock(monkeypatch):
    return RepairMock(monkeypatch, mock_helper.WindowMock(monkeypatch))


def test_model_init_zero():
    g = repair.CntGrp()
    assert g.total == 0
    assert g.success_cnt == 0
    assert g.fail_cnt == 0


def test_model_reset():
    g = repair.CntGrp()
    g.reset(111, 222, 333)
    assert g.total == 111
    assert g.success_cnt == 222
    assert g.fail_cnt == 333


def test_model_reset_listen():
    g = repair.CntGrp()
    expected = 1
    assert_val = 0

    def callback(grp):
        nonlocal assert_val
        assert_val = grp.total

    g.listen("reset", callback)
    g.reset(expected)

    assert assert_val == expected


def test_model_incSuccessCnt():
    g = repair.CntGrp()
    g.incSuccessCnt()
    assert g.success_cnt == 1


def test_model_incSuccessCnt_listen():
    g = repair.CntGrp()
    expected = 1
    assert_val = 0

    def callback(grp):
        nonlocal assert_val
        assert_val = grp.success_cnt

    g.listen("incSuccessCnt", callback)
    g.incSuccessCnt()

    assert assert_val == expected


def test_model_incFailCnt():
    g = repair.CntGrp()
    g.incFailCnt()
    assert g.fail_cnt == 1


def test_model_incFailCnt_listen():
    g = repair.CntGrp()
    expected = 1
    assert_val = 0

    def callback(grp):
        nonlocal assert_val
        assert_val = grp.fail_cnt

    g.listen("incFailCnt", callback)
    g.incFailCnt()

    assert assert_val == expected


def test_selected_remove_only(qtbot, monkeypatch, r_mock):
    w = Windows()
    model = repair.RepairModel()
    r: repair.Repair = r_mock(w, model)
    qtbot.addWidget(w)

    monkeypatch.setattr(r, "_checkLoginState", lambda *args, **kwargs: True)

    monkeypatch.setattr(w.conf, "definition", False)
    monkeypatch.setattr(w.conf, "sentence", False)
    monkeypatch.setattr(w.conf, "image", False)
    monkeypatch.setattr(w.conf, "phrase", False)
    monkeypatch.setattr(w.conf, "ame_phonetic", False)
    monkeypatch.setattr(w.conf, "bre_phonetic", False)
    monkeypatch.setattr(w.conf, "ame_pron", False)
    monkeypatch.setattr(w.conf, "bre_pron", False)
    monkeypatch.setattr(w.conf, "no_pron", True)

    w.repairDefCB.setChecked(True)
    w.repairPhraseCB.setChecked(True)
    w.repairSentenceCB.setChecked(True)
    w.repairImgCB.setChecked(True)
    w.repairAmEPhoneticCB.setChecked(True)
    w.repairBrEPhoneticCB.setChecked(True)
    w.repairPronCB.setChecked(True)

    w.repairBtn.click()

    def check_label():
        assert aqt.utils.tooltip.called

    qtbot.waitUntil(check_label)

    assert model.noteGrp.total == 1
    assert model.noteGrp.success_cnt == 1
    assert (
        w.repairProgressNoteLabel.text()
        == f"更新本地笔记：{model.noteGrp.success_cnt} / {model.noteGrp.total} . . . "
    )
    assert model.queryGrp.total == 0
    assert model.audioGrp.total == 0


@pytest.mark.parametrize(
    "num, query_fail_num, audio_download_fail", [(13, 0, 0), (17, 11, 5), (23, 0, 19)]
)
def test_query(monkeypatch, r_mock, qtbot, num, query_fail_num, audio_download_fail):
    """- all query succeed
    - mix success and failure
    - some audio succeed"""

    def mock_notes(*args, **kwargs):
        return [notes.Note(1)] * num

    monkeypatch.setattr(noteManager, "getNotesByDeckName", mock_notes)

    # mock query result
    def mock_query_data():
        i = -1

        def query_data(*args, **kwargs):
            nonlocal i
            i += 1
            if i < query_fail_num:
                return None
            return mock_helper.query_data_mock

        return query_data

    monkeypatch.setattr(queryApi.youdao.API, "query", mock_query_data())

    # mock download_file
    def mock_download_file():
        i = -1

        def download_file(*args, **kwargs):
            nonlocal i
            i += 1
            if i < audio_download_fail:
                raise Exception("test: audio download failed")

        return download_file

    monkeypatch.setattr(workers, "download_file", mock_download_file())
    monkeypatch.setattr(os.path, "isfile", lambda *args, **kwargs: False)

    w = Windows()
    model = repair.RepairModel()
    r: repair.Repair = r_mock(w, model)
    qtbot.addWidget(w)

    monkeypatch.setattr(r, "_checkLoginState", lambda *args, **kwargs: True)

    w.repairDefCB.setChecked(True)
    w.repairPhraseCB.setChecked(True)
    w.repairSentenceCB.setChecked(True)
    w.repairImgCB.setChecked(True)
    w.repairAmEPhoneticCB.setChecked(True)
    w.repairBrEPhoneticCB.setChecked(True)
    w.repairPronCB.setChecked(True)

    w.repairBtn.click()

    def check_tooltip():
        assert aqt.utils.tooltip.called

    qtbot.waitUntil(check_tooltip)

    def check_audio_label():
        assert (
            w.repairProgressAudioLabel.text()
            == f"下载发音，成功：{num - query_fail_num - audio_download_fail}，失败：{audio_download_fail} . . . "
        )

    qtbot.waitUntil(check_audio_label)

    assert model.noteGrp.total == num
    assert model.noteGrp.success_cnt == num - query_fail_num
    assert (
        w.repairProgressNoteLabel.text()
        == f"更新本地笔记：{model.noteGrp.success_cnt} / {model.noteGrp.total} . . . "
    )

    assert model.queryGrp.total == num
    assert model.queryGrp.success_cnt == num - query_fail_num
    assert model.queryGrp.fail_cnt == query_fail_num
    assert (
        w.repairProgressQueryLabel.text()
        == f"调用{r._api_name}：{model.queryGrp.success_cnt + model.queryGrp.fail_cnt} / {model.queryGrp.total}，成功：{model.queryGrp.success_cnt}，失败：{r._model.queryGrp.fail_cnt} . . . "
    )

    assert model.audioGrp.success_cnt == num - query_fail_num - audio_download_fail
    assert model.audioGrp.fail_cnt == audio_download_fail
