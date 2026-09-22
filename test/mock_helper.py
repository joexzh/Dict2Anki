import aqt.utils
import pytest
import requests

from addon import addonWindow, misc, noteManager, queryApi, workers
from addon import constants as C
from . import dummy_aqt, dummy_noteManager, helper


def mock_module(monkeypatch, target_mod, mod):
    "replace attributes in target_mod with those found in mod.__all__"
    for name in mod.__all__:
        if not name.startswith('_'):
            monkeypatch.setattr(target_mod, name, getattr(mod, name))


def mock_noteManager(monkeypatch):
    mock_module(monkeypatch, noteManager, dummy_noteManager)


def mock_aqt_mw(monkeypatch):
    monkeypatch.setattr(aqt, 'mw', dummy_aqt.mw)


def mock_aqt_utils(monkeypatch):
    ask_user = helper.MockCallable()
    ask_user.return_value = True
    monkeypatch.setattr(aqt.utils, 'askUser', ask_user)
    monkeypatch.setattr(aqt.utils, 'openLink', helper.MockCallable())
    monkeypatch.setattr(aqt.utils, 'tooltip', helper.MockCallable())
    monkeypatch.setattr(aqt.utils, 'showInfo', helper.MockCallable())
    monkeypatch.setattr(aqt.utils, 'showCritical', helper.MockCallable())


def mock_requests(monkeypatch):
    j = helper.MockCallable()
    j.return_value = {'tag_name': C.VERSION, 'body': 'changeLog'}

    class MockResponse:
        json = j

    monkeypatch.setattr(requests, 'get', lambda *args, **kwargs: MockResponse)


def mock_session_get(monkeypatch: pytest.MonkeyPatch, session: requests.Session, r_text='', r_json_obj=None):
    if r_json_obj is None:
        r_json_obj = dict()

    j = helper.MockCallable()
    j.return_value = r_json_obj

    r_raise_for_status = helper.MockCallable()

    class MockResponse:
        text = r_text
        json = j
        raise_for_status = r_raise_for_status

    monkeypatch.setattr(session, 'get', lambda *args, **kwargs: MockResponse)


query_data_mock = {
    'term': 'test',
    'definition': ['测试'],
    'phrase': [],
    'image': 'https://test.jpg',
    'sentence': [
        (
            'They test.',
            '他们测试',
        ),
    ],
    'BrEPhonetic': 'ə; eɪ',
    'AmEPhonetic': 'ə; eɪ',
    'BrEPron': 'http://test.mp3',
    'AmEPron': 'http://test.mp3',
}


def mock_query_api(monkeypatch):
    monkeypatch.setattr(queryApi.youdao.API, 'query', lambda *args, **kwargs: query_data_mock)

    monkeypatch.setattr(
        workers.NetworkWorker.session,
        'get',
        lambda *args, **kwargs: requests.Response(),
    )


def mock_misc(monkeypatch):

    def mock_congest_generator(*args, **kwargs):
        while True:
            yield

    monkeypatch.setattr(misc, 'congestGenerator', mock_congest_generator)
    monkeypatch.setattr(misc, 'download_file', lambda *args, **kwargs: None)
    monkeypatch.setattr(misc, 'rm_file', lambda *args, **kwargs: None)
    monkeypatch.setattr(misc, 'mv_file', lambda *args, **kwargs: True)


class WindowMock:
    def __init__(self, monkeypatch):
        mock_aqt_mw(monkeypatch)
        mock_noteManager(monkeypatch)
        mock_aqt_utils(monkeypatch)
        mock_requests(monkeypatch)
        mock_query_api(monkeypatch)
        mock_misc(monkeypatch)

    def __call__(self):
        return addonWindow.Windows()


@pytest.fixture
def w_mock(monkeypatch):
    return WindowMock(monkeypatch)
