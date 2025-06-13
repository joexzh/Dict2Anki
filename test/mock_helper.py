import aqt.utils
import pytest
import requests

from ..addon import addonWindow, misc, noteManager, queryApi, workers
from ..addon.constants import *
from . import dummy_aqt, dummy_noteManager, helper


def mock_noteManager(monkeypatch):
    monkeypatch.setattr(noteManager, "getDeckNames", dummy_noteManager.getDeckNames)
    monkeypatch.setattr(
        noteManager, "getOrCreateDeck", dummy_noteManager.getOrCreateDeck
    )
    monkeypatch.setattr(
        noteManager, "getOrCreateModel", dummy_noteManager.getOrCreateModel
    )
    monkeypatch.setattr(
        noteManager,
        "getOrCreateModelCardTemplate",
        dummy_noteManager.getOrCreateModelCardTemplate,
    )
    monkeypatch.setattr(noteManager, "addNoteToDeck", dummy_noteManager.addNoteToDeck)
    monkeypatch.setattr(noteManager, "getWordsByDeck", dummy_noteManager.getWordsByDeck)
    monkeypatch.setattr(noteManager, "getNoteIds", dummy_noteManager.getNoteIds)
    monkeypatch.setattr(noteManager, "removeNotes", dummy_noteManager.removeNotes)
    monkeypatch.setattr(noteManager, "media_path", dummy_noteManager.media_path)
    monkeypatch.setattr(
        noteManager, "writeNoteFields", dummy_noteManager.writeNoteFields
    )
    monkeypatch.setattr(
        noteManager, "getNotesByDeckName", dummy_noteManager.getNotesByDeckName
    )


def mock_aqt_mw(monkeypatch):
    monkeypatch.setattr(aqt, "mw", dummy_aqt.mw)


def mock_aqt_utils(monkeypatch):
    ask_user = helper.MockCallable()
    ask_user.return_value = True
    monkeypatch.setattr(aqt.utils, "askUser", ask_user)
    monkeypatch.setattr(aqt.utils, "openLink", helper.MockCallable())
    monkeypatch.setattr(aqt.utils, "tooltip", helper.MockCallable())
    monkeypatch.setattr(aqt.utils, "showInfo", helper.MockCallable())
    monkeypatch.setattr(aqt.utils, "showCritical", helper.MockCallable())


def mock_requests(monkeypatch):
    j = helper.MockCallable()
    j.return_value = {"tag_name": VERSION, "body": "changeLog"}

    class MockResponse:
        json = j

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockResponse)


query_data_mock = {
    "term": "test",
    "definition": ["测试"],
    "phrase": [],
    "image": "https://test.jpg",
    "sentence": [
        (
            "They test.",
            "他们测试",
        ),
    ],
    "BrEPhonetic": "ə; eɪ",
    "AmEPhonetic": "ə; eɪ",
    "BrEPron": "http://test.mp3",
    "AmEPron": "http://test.mp3",
}


def mock_query_api(monkeypatch):
    monkeypatch.setattr(
        queryApi.youdao.API, "query", lambda *args, **kwargs: query_data_mock
    )

    monkeypatch.setattr(workers, "download_file", lambda *args, **kwargs: None)
    monkeypatch.setattr(workers, "rmv_file", lambda *args, **kwargs: None)

    monkeypatch.setattr(
        workers.NetworkWorker.session,
        "get",
        lambda *args, **kwargs: requests.Response(),
    )

    def mock_congest_generator(*args, **kwargs):
        while True:
            yield

    monkeypatch.setattr(misc, "congestGenerator", mock_congest_generator)


class WindowMock:
    def __init__(self, monkeypatch):
        mock_aqt_mw(monkeypatch)
        mock_noteManager(monkeypatch)
        mock_aqt_utils(monkeypatch)
        mock_requests(monkeypatch)
        mock_query_api(monkeypatch)

    def __call__(self):
        return addonWindow.Windows()


@pytest.fixture
def w_mock(monkeypatch):
    return WindowMock(monkeypatch)
