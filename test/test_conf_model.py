import pytest

from ..addon.conf_model import Conf
from .helper import fresh_config_dict


@pytest.fixture
def new_conf():
    return Conf(fresh_config_dict())


def test_desk(new_conf):
    new_conf.deck = "test_deck"
    assert new_conf.deck == "test_deck"


def test_selected_dict(new_conf):
    new_conf.selected_dict = 1
    assert new_conf.selected_dict == 1


def test_selected_api(new_conf):
    new_conf.selected_api = 1
    assert new_conf.selected_api == 1


def test_current_username(new_conf):
    new_conf.current_username = "test_username"
    assert new_conf.current_username == "test_username"


def test_current_password(new_conf):
    new_conf.current_password = "test_password"
    assert new_conf.current_password == "test_password"


def test_current_cookies(new_conf):
    new_conf.current_cookies = "test_cookies"
    assert new_conf.current_cookies == "test_cookies"


def test_current_cookies_listen(new_conf):
    assert_val = ""
    expected = "hello"

    def callback(val):
        nonlocal assert_val
        assert_val = expected

    new_conf.listen("current_cookies", callback)
    new_conf.current_cookies = expected

    assert assert_val == expected


def test_current_cookies_unlisten(new_conf):
    assert_val = "hello"
    expected = "hello"

    def callback(val):
        nonlocal assert_val
        assert_val = val

    new_conf.listen("current_cookies", callback)
    new_conf.unlisten("current_cookies", callback)
    new_conf.current_cookies = "world"

    assert assert_val == expected


def test_definition(new_conf):
    new_conf.definition = False
    assert new_conf.definition == False


def test_image(new_conf):
    new_conf.image = False
    assert new_conf.image == False


def test_sentence(new_conf):
    new_conf.sentence = False
    assert new_conf.sentence == False


def test_phrase(new_conf):
    new_conf.phrase = False
    assert new_conf.phrase == False


def test_ame_phonetic(new_conf):
    new_conf.ame_phonetic = False
    assert new_conf.ame_phonetic == False


def test_bre_phonetic(new_conf):
    new_conf.bre_phonetic = False
    assert new_conf.bre_phonetic == False


def test_bre_pron(new_conf):
    new_conf.bre_pron = True
    assert new_conf.bre_pron == True
    assert new_conf.ame_pron == False
    assert new_conf.no_pron == False


def test_ame_pron(new_conf):
    new_conf.ame_pron = True
    assert new_conf.ame_pron == True
    assert new_conf.bre_pron == False
    assert new_conf.no_pron == False


def test_no_pron(new_conf):
    new_conf.no_pron = True
    assert new_conf.no_pron == True
    assert new_conf.ame_pron == False
    assert new_conf.bre_pron == False


def test_congest(new_conf):
    new_conf.congest = 200
    assert new_conf.congest == 200


def test_current_selected_groups(new_conf):
    expected = ["hello", "world", "!"]
    new_conf.current_selected_groups = expected
    assert new_conf.current_selected_groups == expected
