import typing as T

from addon import adv_conf, conf_migration, dictionary, misc, queryApi
from addon import constants as C
from addon import global_vars as G
from addon.conf_model import Conf

from . import helper


def new_conf():
    return Conf(helper.fresh_latest_confmap())


def same_val_should_not_dirty(attr, val, conf: T.Optional[Conf] = None):
    if conf is None:
        conf = new_conf()

    attr_name = getattr(attr, 'fget', attr).__name__
    setattr(conf, attr_name, val)
    # force reset dirty to False
    conf._dirty = False
    setattr(conf, attr_name, val)

    assert conf.is_dirty() is False


def test_ast_old_at_init():
    # test make ast from old config at init
    conf = new_conf()

    assert isinstance(conf._ast_dict[C.F_DEFINITION][0], adv_conf.ApiFConfAST)
    assert isinstance(conf._ast_dict[C.F_PHRASE][0], adv_conf.ApiFConfAST)
    assert isinstance(conf._ast_dict[C.F_SENTENCE][0], adv_conf.ApiFConfAST)
    assert isinstance(conf._ast_dict[C.F_IMAGE][0], adv_conf.ApiFConfAST)
    assert isinstance(conf._ast_dict[C.F_AMEPHONETIC][0], adv_conf.ApiFConfAST)
    assert isinstance(conf._ast_dict[C.F_BREPHONETIC][0], adv_conf.ApiFConfAST)
    assert isinstance(conf._ast_dict[C.F_AMEPRON][0], adv_conf.ApiFConfAST)
    assert isinstance(conf._ast_dict[C.F_BREPRON][0], adv_conf.EmptyFConfAST)
    assert conf.is_dirty() is False


def test_desk():
    # test value can be assigned

    conf = new_conf()
    assert_val = 'test_deck'
    conf.deck = assert_val

    assert conf.deck == assert_val
    assert conf.is_dirty() is True


def test_desk_dirty():
    same_val_should_not_dirty(Conf.deck, 'test_desk')


def test_selected_dict():
    conf = new_conf()
    conf.selected_dict = '1'

    assert conf.selected_dict == '1'
    assert conf.is_dirty() is True


def test_selected_dict_dirty():
    same_val_should_not_dirty(Conf.selected_dict, 1)


def test_selected_api():
    # test value can be assigned. Default `selected_api` is not '1'

    conf = new_conf()
    conf.selected_api = '1'

    assert conf.selected_api == '1'
    assert conf.is_dirty() is True

    # test AST can be made. Default `definition` is True, `advanced_enabled` is
    # False.

    ast = conf._ast_dict[C.F_DEFINITION][0]

    assert isinstance(ast, adv_conf.ApiFConfAST)
    assert ast.api == '1'


def test_selected_api_dirty():
    same_val_should_not_dirty(Conf.selected_api, 1)


def test_current_cookies():
    conf = new_conf()
    val = 'test_cookies'
    conf.current_cookies = val

    assert conf.current_cookies == val
    cookie_encoded = conf.current_credential['cookie_encoded']
    assert cookie_encoded != '' and cookie_encoded != val
    assert conf.is_dirty() is True


def test_current_cookies_dirty():
    same_val_should_not_dirty(Conf.current_cookies, 'test_cookies')


def test_current_cookies_listen():
    conf = new_conf()
    assert_val = ''
    expected = 'hello'

    def callback(val):
        nonlocal assert_val
        assert_val = expected

    conf.listen('current_cookies', callback)
    conf.current_cookies = expected

    assert assert_val == expected


def test_current_cookies_unlisten():
    conf = new_conf()
    assert_val = 'hello'
    expected = 'hello'

    def callback(val):
        nonlocal assert_val
        assert_val = val

    conf.listen('current_cookies', callback)
    conf.unlisten('current_cookies', callback)
    conf.current_cookies = 'world'

    assert assert_val == expected


def test_definition():
    # test value can be assigned. Default `definition` is True

    conf = new_conf()
    conf.definition = False

    assert conf.definition is False
    assert conf.is_dirty() is True

    # test AST can be made, should be `EmptyFConfAST`

    assert isinstance(conf._ast_dict[C.F_DEFINITION][0], adv_conf.EmptyFConfAST)

    # test AST should not change because default `advanced_enabled` is False
    conf.advanced_definition = 'api:hello'
    assert isinstance(conf._ast_dict[C.F_DEFINITION][0], adv_conf.EmptyFConfAST)


def test_definition_dirty():
    same_val_should_not_dirty(Conf.definition, False)


def test_image():
    # test value can be assigned. Default `image` is True

    conf = new_conf()
    conf.image = False

    assert conf.image is False

    # test AST can be made, should be `EmptyFConfAST`.

    assert isinstance(conf._ast_dict[C.F_IMAGE][0], adv_conf.EmptyFConfAST)

    # test AST should not change because default `advanced_enabled` is False
    conf.advanced_image = 'api:hello'
    assert isinstance(conf._ast_dict[C.F_IMAGE][0], adv_conf.EmptyFConfAST)


def test_image_dirty():
    same_val_should_not_dirty(Conf.image, False)


def test_sentence():
    # test value can be assigned. Default `sentence` is True

    conf = new_conf()
    conf.sentence = False

    assert conf.sentence is False
    assert conf.is_dirty() is True

    # test AST can be made, should be `EmptyFConfAST`.

    assert isinstance(conf._ast_dict[C.F_SENTENCE][0], adv_conf.EmptyFConfAST)

    # test AST should not change because default `advanced_enabled` is False
    conf.advanced_sentence = 'api:hello'
    assert isinstance(conf._ast_dict[C.F_SENTENCE][0], adv_conf.EmptyFConfAST)


def test_sentence_dirty():
    same_val_should_not_dirty(Conf.sentence, False)


def test_phrase():
    # test value can be assigned. Default `phrase` is True

    conf = new_conf()
    conf.phrase = False

    assert conf.phrase is False
    assert conf.is_dirty() is True

    # test AST can be made, should be `EmptyFConfAST`.

    assert isinstance(conf._ast_dict[C.F_PHRASE][0], adv_conf.EmptyFConfAST)

    # test AST should not change because default `advanced_enabled` is False
    conf.advanced_phrase = 'api:hello'
    assert isinstance(conf._ast_dict[C.F_PHRASE][0], adv_conf.EmptyFConfAST)


def test_phrase_dirty():
    same_val_should_not_dirty(Conf.phrase, False)


def test_ame_phonetic():
    # test value can be assigned. Default `ame_phonetic` is True

    conf = new_conf()
    conf.ame_phonetic = False

    assert conf.ame_phonetic is False
    assert conf.is_dirty() is True

    # test AST can be made, should be `EmptyConfAST`.

    assert isinstance(conf._ast_dict[C.F_AMEPHONETIC][0], adv_conf.EmptyFConfAST)

    # test AST should not change because default `advanced_enabled` is False
    conf.advanced_AmEPhonetic = 'api:hello'
    assert isinstance(conf._ast_dict[C.F_AMEPHONETIC][0], adv_conf.EmptyFConfAST)


def test_ame_phonetic_dirty():
    same_val_should_not_dirty(Conf.ame_phonetic, False)


def test_bre_phonetic():
    # test value can be assigned. Default `bre_phonetic` is True

    conf = new_conf()
    conf.bre_phonetic = False

    assert conf.bre_phonetic is False
    assert conf.is_dirty() is True

    # test AST can be made, should be `EmptyConfAST`.

    assert isinstance(conf._ast_dict[C.F_BREPHONETIC][0], adv_conf.EmptyFConfAST)

    # test AST should not change because default `advanced_enabled` is False
    conf.advanced_BrEPhonetic = 'api:hello'
    assert isinstance(conf._ast_dict[C.F_BREPHONETIC][0], adv_conf.EmptyFConfAST)


def test_bre_phonetic_dirty():
    same_val_should_not_dirty(Conf.bre_phonetic, False)


def test_bre_pron():
    # test value can be assigned. Default `bre_pron` is False

    conf = new_conf()
    conf.bre_pron = True

    assert conf.bre_pron is True
    assert conf.ame_pron is False
    assert conf.no_pron is False
    assert conf.is_dirty() is True

    # test AST can be made, should be `ApiFConfAST`

    assert isinstance(conf._ast_dict[C.F_BREPRON][0], adv_conf.ApiFConfAST)

    # test AST should not change because `advanced_enabled` is False
    conf.advanced_BrEPron = 'flag:1'
    assert isinstance(conf._ast_dict[C.F_BREPRON][0], adv_conf.ApiFConfAST)


def test_bre_pron_dirty():
    # json file defaults to False
    same_val_should_not_dirty(Conf.bre_pron, True)


def test_ame_pron():
    # test value can be assigned. Default `ame_pron` is True

    conf_map = helper.fresh_latest_confmap()
    conf_map['AmEPron'] = False
    conf_map['BrEPron'] = False
    conf_map['noPron'] = True
    conf = Conf(conf_map)

    conf.ame_pron = True

    assert conf.ame_pron is True
    assert conf.bre_pron is False
    assert conf.no_pron is False
    assert conf.is_dirty() is True

    # test AST can be made, should be `ApiFConfAST`

    assert isinstance(conf._ast_dict[C.F_AMEPRON][0], adv_conf.ApiFConfAST)

    # test AST should not change because default `advanced_enabled` is False
    conf.advanced_AmEPron = 'flag:1'
    assert isinstance(conf._ast_dict[C.F_AMEPRON][0], adv_conf.ApiFConfAST)


def test_ame_pron_dirty():
    # json file defaults to True
    conf_map = helper.fresh_latest_confmap()
    conf_map['AmEPron'] = False
    conf_map['BrEPron'] = False
    conf_map['noPron'] = True
    conf = Conf(conf_map)
    same_val_should_not_dirty(Conf.ame_pron, True, conf)


def test_no_pron():
    # test value can be assigned. Default `no_pron` is False

    conf = new_conf()
    conf.no_pron = True

    assert conf.no_pron is True
    assert conf.ame_pron is False
    assert conf.bre_pron is False
    assert conf.is_dirty() is True

    # test AST can be made, both 'AmEPron' and 'BrEPron's' should be `EmptyFConfAST`

    assert isinstance(conf._ast_dict[C.F_AMEPRON][0], adv_conf.EmptyFConfAST)
    assert isinstance(conf._ast_dict[C.F_BREPRON][0], adv_conf.EmptyFConfAST)


def test_no_pron_dirty():
    same_val_should_not_dirty(Conf.no_pron, True)


def test_congest():
    conf = new_conf()
    conf.congest = 200

    assert conf.congest == 200
    assert conf.is_dirty() is True


def test_congest_dirty():
    same_val_should_not_dirty(Conf.congest, 200)


def new_conf_adv():
    conf_str = 'api:hello | api:world | flag:1'
    confmap = helper.fresh_latest_confmap()
    confmap['advanced_fields']['enabled'] = True
    confmap['advanced_fields']['enable_user_modules'] = True
    confmap['advanced_fields']['definition'] = conf_str
    confmap['advanced_fields']['sentence'] = conf_str
    confmap['advanced_fields']['phrase'] = conf_str
    confmap['advanced_fields']['image'] = conf_str
    confmap['advanced_fields']['AmEPhonetic'] = conf_str
    confmap['advanced_fields']['BrEPhonetic'] = conf_str
    confmap['advanced_fields']['AmEPron'] = conf_str
    confmap['advanced_fields']['BrEPron'] = conf_str
    return Conf(confmap)


def test_adv_ast_at_init():
    # test make ast from advanced config at init

    conf = new_conf_adv()

    assert isinstance(conf._ast_dict[C.F_DEFINITION][0], adv_conf.OrFConfAST)
    assert isinstance(conf._ast_dict[C.F_SENTENCE][0], adv_conf.OrFConfAST)
    assert isinstance(conf._ast_dict[C.F_PHRASE][0], adv_conf.OrFConfAST)
    assert isinstance(conf._ast_dict[C.F_IMAGE][0], adv_conf.OrFConfAST)
    assert isinstance(conf._ast_dict[C.F_AMEPHONETIC][0], adv_conf.OrFConfAST)
    assert isinstance(conf._ast_dict[C.F_BREPHONETIC][0], adv_conf.OrFConfAST)
    assert isinstance(conf._ast_dict[C.F_AMEPRON][0], adv_conf.OrFConfAST)
    assert isinstance(conf._ast_dict[C.F_BREPRON][0], adv_conf.OrFConfAST)
    assert conf.is_dirty() is False


def test_adv_enabled():
    # test value can be assigned

    conf = new_conf_adv()
    conf.advanced_enabled = False

    assert conf.advanced_enabled is False
    assert conf.is_dirty() is True

    # test ASTs are changed to Api from old config
    assert isinstance(conf._ast_dict[C.F_DEFINITION][0], adv_conf.ApiFConfAST)

    conf.advanced_enabled = True

    # test ASTs are changed back to OR
    assert isinstance(conf._ast_dict[C.F_DEFINITION][0], adv_conf.OrFConfAST)


def test_adv_enable_user_modules():
    # test value can be assigned

    conf = new_conf_adv()
    conf.advanced_enable_user_modules = False

    assert conf.advanced_enable_user_modules is False
    assert conf.is_dirty() is True


def test_adv_definition():
    # test value can be assigned

    conf = new_conf_adv()
    conf.advanced_definition = 'flag:1'

    assert conf.advanced_definition == 'flag:1'
    # test AST is changed
    assert isinstance(conf._ast_dict[C.F_DEFINITION][0], adv_conf.NoteFlagFConfAST)
    assert conf.is_dirty() is True

    # test AST should not change because `advanced_enabled` is True
    conf.definition = True
    assert isinstance(conf._ast_dict[C.F_DEFINITION][0], adv_conf.NoteFlagFConfAST)


def test_adv_sentence():
    # test value can be assigned

    conf = new_conf_adv()
    conf.advanced_sentence = 'flag:1'

    assert conf.advanced_sentence == 'flag:1'
    # test AST is changed
    assert isinstance(conf._ast_dict[C.F_SENTENCE][0], adv_conf.NoteFlagFConfAST)
    assert conf.is_dirty() is True

    # test AST should not change because `advanced_enabled` is True
    conf.sentence = True
    assert isinstance(conf._ast_dict[C.F_SENTENCE][0], adv_conf.NoteFlagFConfAST)


def test_adv_phrase():
    # test value can be assigned

    conf = new_conf_adv()
    conf.advanced_phrase = 'flag:1'

    assert conf.advanced_phrase == 'flag:1'
    # test AST is changed
    assert isinstance(conf._ast_dict[C.F_PHRASE][0], adv_conf.NoteFlagFConfAST)
    assert conf.is_dirty() is True

    # test AST should not change because `advanced_enabled` is True
    conf.phrase = True
    assert isinstance(conf._ast_dict[C.F_PHRASE][0], adv_conf.NoteFlagFConfAST)


def test_adv_image():
    # test value can be assigned

    conf = new_conf_adv()
    conf.advanced_image = 'flag:1'

    assert conf.advanced_image == 'flag:1'
    # test AST is changed
    assert isinstance(conf._ast_dict[C.F_IMAGE][0], adv_conf.NoteFlagFConfAST)
    assert conf.is_dirty() is True

    # test AST should not change because `advanced_enabled` is True
    conf.image = True
    assert isinstance(conf._ast_dict[C.F_IMAGE][0], adv_conf.NoteFlagFConfAST)


def test_adv_ame_phonetic():
    # test value can be assigned

    conf = new_conf_adv()
    conf.advanced_AmEPhonetic = 'flag:1'

    assert conf.advanced_AmEPhonetic == 'flag:1'
    # test AST is changed
    assert isinstance(conf._ast_dict[C.F_AMEPHONETIC][0], adv_conf.NoteFlagFConfAST)
    assert conf.is_dirty() is True

    # test AST should not change because `advanced_enabled` is True
    conf.ame_phonetic = True
    assert isinstance(conf._ast_dict[C.F_AMEPHONETIC][0], adv_conf.NoteFlagFConfAST)


def test_adv_bre_phonetic():
    # test value can be assigned

    conf = new_conf_adv()
    conf.advanced_BrEPhonetic = 'flag:1'

    assert conf.advanced_BrEPhonetic == 'flag:1'
    # test AST is changed
    assert isinstance(conf._ast_dict[C.F_BREPHONETIC][0], adv_conf.NoteFlagFConfAST)
    assert conf.is_dirty() is True

    # test AST should not change because `advanced_enabled` is True
    conf.bre_phonetic = True
    assert isinstance(conf._ast_dict[C.F_BREPHONETIC][0], adv_conf.NoteFlagFConfAST)


def test_adv_ame_pron():
    # test value can be assigned

    conf = new_conf_adv()
    conf.advanced_AmEPron = 'flag:1'

    assert conf.advanced_AmEPron == 'flag:1'
    # test AST is changed
    assert isinstance(conf._ast_dict[C.F_AMEPRON][0], adv_conf.NoteFlagFConfAST)
    assert conf.is_dirty() is True

    # test AST should not change because `advanced_enabled` is True
    conf.ame_pron = True
    assert isinstance(conf._ast_dict[C.F_AMEPRON][0], adv_conf.NoteFlagFConfAST)


def test_adv_bre_pron():
    # test value can be assigned

    conf = new_conf_adv()
    conf.advanced_BrEPron = 'flag:1'

    assert conf.advanced_BrEPron == 'flag:1'
    # test AST is changed
    assert isinstance(conf._ast_dict[C.F_BREPRON][0], adv_conf.NoteFlagFConfAST)
    assert conf.is_dirty() is True

    # test AST should not change because `advanced_enabled` is True
    conf.bre_pron = True
    assert isinstance(conf._ast_dict[C.F_BREPRON][0], adv_conf.NoteFlagFConfAST)


def test_user_agent_has_instance():

    # don't forget to clear the singleton instance before this test ends
    Conf.getinstance(helper.fresh_latest_confmap())
    assert_ua = G.user_agent()

    assert assert_ua == C.USER_AGENT

    G.conf_instance = None


def test_user_agent_no_instance():
    G.conf_instance = None
    assert G.user_agent() == C.USER_AGENT


def test_user_agent_dirty():
    same_val_should_not_dirty(Conf.user_agent, helper.USER_AGENT)


def test_current_selected_groups():
    expected = ['hello', 'world', '!']
    conf = new_conf()
    conf.current_selected_groups = expected

    assert conf.current_selected_groups == expected
    assert conf.is_dirty() is True


def test_current_selected_groups_dirty():
    same_val_should_not_dirty(Conf.current_selected_groups, [])


def test_migration_v1_v2():
    confmap = helper.fresh_v1_confmap()
    confmap['credential'] = [{'cookie': '0'}, {'cookie': '1'}]  # type: ignore
    cookie0_encoded = misc.enc_cookies('0')
    cookie1_encoded = misc.enc_cookies('1')

    conf_migration.migrate_v1_v2(confmap)
    creds = confmap['credential']

    assert 'cookie' not in creds[0]
    assert creds[0]['cookie_encoded'] == cookie0_encoded

    assert 'cookie' not in creds[1]
    assert creds[1]['cookie_encoded'] == cookie1_encoded


def test_migration_v2_v3():
    confmap = helper.fresh_v2_confmap()
    conf_migration.migrate_v2_v3(confmap)

    assert 'selectedDict' not in confmap
    assert 'selectedApi' not in confmap
    assert 'selectedGroup' not in confmap
    assert 'credential' not in confmap

    assert confmap['selected_dict'] == dictionary.eudict.Dict.name
    assert confmap['selected_api'] == queryApi.youdao.API.name
    assert confmap['dict_saved_groups'][dictionary.eudict.Dict.name] == []
    assert confmap['credentials'][dictionary.eudict.Dict.name]['cookie_encoded'] == ''


def test_decode_cookies_at_init():
    cookies = """azAZ09~!@#$%^&*()_+-=[]{}\\|;:'",<.>/?~`"""
    cookies_enc = misc.enc_cookies(cookies)

    confmap = helper.fresh_v3_confmap()
    confmap['credentials'] = {
        dictionary.eudict.Dict.name: {'cookie_encoded': cookies_enc},
        dictionary.youdao.Dict.name: {'cookie_encoded': ''},
    }
    conf = Conf(confmap)

    conf.selected_dict = dictionary.eudict.Dict.name
    assert conf.current_cookies == cookies

    conf.selected_dict = dictionary.youdao.Dict.name
    assert conf.current_cookies == ''
