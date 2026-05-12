import pytest

from ..addon import misc
from ..addon.conf_model import Conf
from . import helper


@pytest.fixture
def new_conf():
    return Conf(helper.fresh_config_dict())


def test_init_should_not_dirty(new_conf: Conf):
    assert new_conf.is_dirty() is False


def test_desk(new_conf):
    new_conf.deck = 'test_deck'

    assert new_conf.deck == 'test_deck'
    assert new_conf.is_dirty() is True


def test_selected_dict(new_conf):
    new_conf.selected_dict = 1

    assert new_conf.selected_dict == 1
    assert new_conf.is_dirty() is True


def test_selected_api(new_conf):
    new_conf.selected_api = 1

    assert new_conf.selected_api == 1
    assert new_conf.is_dirty() is True


def test_current_cookies(new_conf):
    new_conf.current_cookies = 'test_cookies'

    assert new_conf.current_cookies == 'test_cookies'
    assert new_conf.current_credential['cookie_encoded'] != ''
    assert new_conf.is_dirty() is True


def test_current_cookies_listen(new_conf):
    assert_val = ''
    expected = 'hello'

    def callback(val):
        nonlocal assert_val
        assert_val = expected

    new_conf.listen('current_cookies', callback)
    new_conf.current_cookies = expected

    assert assert_val == expected


def test_current_cookies_unlisten(new_conf):
    assert_val = 'hello'
    expected = 'hello'

    def callback(val):
        nonlocal assert_val
        assert_val = val

    new_conf.listen('current_cookies', callback)
    new_conf.unlisten('current_cookies', callback)
    new_conf.current_cookies = 'world'

    assert assert_val == expected


def test_definition(new_conf):
    new_conf.definition = False

    assert new_conf.definition is False
    assert new_conf.is_dirty() is True


def test_image(new_conf):
    new_conf.image = False

    assert new_conf.image is False


def test_sentence(new_conf):
    new_conf.sentence = False

    assert new_conf.sentence is False
    assert new_conf.is_dirty() is True


def test_phrase(new_conf):
    new_conf.phrase = False

    assert new_conf.phrase is False
    assert new_conf.is_dirty() is True


def test_ame_phonetic(new_conf):
    new_conf.ame_phonetic = False

    assert new_conf.ame_phonetic is False
    assert new_conf.is_dirty() is True


def test_bre_phonetic(new_conf):
    new_conf.bre_phonetic = False

    assert new_conf.bre_phonetic is False
    assert new_conf.is_dirty() is True


def test_bre_pron(new_conf):
    new_conf.bre_pron = True

    assert new_conf.bre_pron is True
    assert new_conf.ame_pron is False
    assert new_conf.no_pron is False
    assert new_conf.is_dirty() is True


def test_ame_pron(new_conf):
    new_conf.ame_pron = True

    assert new_conf.ame_pron is True
    assert new_conf.bre_pron is False
    assert new_conf.no_pron is False
    assert new_conf.is_dirty() is True


def test_no_pron(new_conf):
    new_conf.no_pron = True

    assert new_conf.no_pron is True
    assert new_conf.ame_pron is False
    assert new_conf.bre_pron is False
    assert new_conf.is_dirty() is True


def test_congest(new_conf):
    new_conf.congest = 200

    assert new_conf.congest == 200
    assert new_conf.is_dirty() is True


def test_user_agent_has_instance():
    """
    For v1: should match default value

    For v2: should match the value in user config
    """

    # don't modify conf through singleton instance, otherwise will mess up other
    # tests
    Conf.getinstance(helper.fresh_config_dict())
    assert_ua = Conf.user_agent_or_default()

    if helper.env_conf_v() >= 2:
        assert assert_ua == helper.USER_AGENT
    else:
        assert assert_ua == Conf.default_user_agent


def test_user_agent_no_instance():
    Conf.instance = None
    assert Conf.user_agent_or_default() == Conf.default_user_agent


def test_current_selected_groups(new_conf):
    expected = []
    new_conf.current_selected_groups = expected

    assert new_conf.current_selected_groups == expected
    # assign same value should not make dirty
    assert new_conf.is_dirty() is False

    expected = ['hello', 'world', '!']
    new_conf.current_selected_groups = expected

    assert new_conf.current_selected_groups == expected
    assert new_conf.is_dirty() is True


def test_saving_map(new_conf: Conf):
    "should delete `version` and clear `cookie`"

    new_conf.current_cookies = 'test_cookies'
    map_cp = new_conf.get_saving_map()

    assert 'version' not in map_cp
    assert not any(map(lambda cred: cred['cookie'], map_cp['credential']))


def test_encode_cookies_at_init():
    cookies = 'azAZ09~!@#$%^&*()_+-=[]{}\|;:\'",<.>/?~`'
    cookies_enc = misc.enc_cookies(cookies)

    conf_map = helper.fresh_config_dict()
    conf_map['credential'] = [
        {'cookie': cookies},
        {'cookie': ''},
    ]
    conf = Conf(conf_map)

    conf.selected_dict = 0
    assert conf.current_credential['cookie_encoded'] == cookies_enc

    conf.selected_dict = 1
    assert conf.current_credential['cookie_encoded'] == ''


def test_decode_cookies_at_init():
    cookies = 'azAZ09~!@#$%^&*()_+-=[]{}\|;:\'",<.>/?~`'
    cookies_enc = misc.enc_cookies(cookies)

    conf_map = helper.fresh_config_dict()
    conf_map['credential'] = [
        {'cookie': '', 'cookie_encoded': cookies_enc},
        {'cookie': ''},
    ]
    conf = Conf(conf_map)

    conf.selected_dict = 0
    assert conf.current_cookies == cookies

    conf.selected_dict = 1
    assert conf.current_cookies == ''
