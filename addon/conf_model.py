from __future__ import annotations

import copy
import functools
import threading
import typing as T

from . import _typing as _T
from . import adv_conf
from . import constants as C
from . import global_vars as V
from .conf_migration import migrate_version
from .misc import dec_cookies, enc_cookies


def make_ast_from_bool(val: bool, api: str) -> adv_conf.FConfAST:
    return adv_conf.ApiFConfAST(api) if val else adv_conf.EmptyFConfAST()


def _set_dirty(method):
    """
    Conf setter decorator, sets self._dirty=True if value changed

    Note: Qt will trigger change event no matter value is the same or not.
    """

    @functools.wraps(method)
    def wrapper(self: Conf, val, *args, **kwargs):
        name = method.__name__
        curr_val = getattr(self, name)
        if curr_val == val:
            return
        self._dirty = True
        return method(self, val, *args, **kwargs)

    return wrapper


class Conf(_T.ListenableModel):
    lock = threading.Lock()

    @classmethod
    def getinstance(cls, confmap: _T.ConfigMap):
        "Thread safe singleton instance"
        if V.conf_instance is None:
            with cls.lock:
                if V.conf_instance is None:
                    V.conf_instance = Conf(confmap)
        return V.conf_instance

    @classmethod
    def delinstance(cls):
        "Must call only when closing addon main window"
        if V.conf_instance is not None:
            V.conf_instance = None

    def __init__(self, conf):
        super().__init__()
        # require valid `config` returned from `mw.addonManager.getConfig`
        self._map: _T.ConfigMap = conf
        self._ast_dict: dict[str, tuple[T.Optional[adv_conf.FConfAST], str]] = self._make_ast_dict()
        self._dirty = False

        migrate_version(self)

    def _make_ast_dict(self) -> dict[str, tuple[T.Optional[adv_conf.FConfAST], str]]:
        ast_dict: dict[str, tuple[T.Optional[adv_conf.FConfAST], str]] = {}
        if self.advanced_enabled:
            ast_dict[C.F_DEFINITION] = adv_conf.make_ast(self.advanced_definition)
            ast_dict[C.F_SENTENCE] = adv_conf.make_ast(self.advanced_sentence)
            ast_dict[C.F_IMAGE] = adv_conf.make_ast(self.advanced_image)
            ast_dict[C.F_PHRASE] = adv_conf.make_ast(self.advanced_phrase)
            ast_dict[C.F_AMEPHONETIC] = adv_conf.make_ast(self.advanced_AmEPhonetic)
            ast_dict[C.F_BREPHONETIC] = adv_conf.make_ast(self.advanced_BrEPhonetic)
            ast_dict[C.F_AMEPRON] = adv_conf.make_ast(self.advanced_AmEPron)
            ast_dict[C.F_BREPRON] = adv_conf.make_ast(self.advanced_BrEPron)
        else:
            ast_dict[C.F_DEFINITION] = (make_ast_from_bool(self.definition, self.selected_api), '')
            ast_dict[C.F_SENTENCE] = (make_ast_from_bool(self.sentence, self.selected_api), '')
            ast_dict[C.F_IMAGE] = (make_ast_from_bool(self.image, self.selected_api), '')
            ast_dict[C.F_PHRASE] = (make_ast_from_bool(self.phrase, self.selected_api), '')
            ast_dict[C.F_AMEPHONETIC] = (make_ast_from_bool(self.ame_phonetic, self.selected_api), '')
            ast_dict[C.F_BREPHONETIC] = (make_ast_from_bool(self.bre_phonetic, self.selected_api), '')
            ast_dict[C.F_AMEPRON] = (make_ast_from_bool(self.ame_pron, self.selected_api), '')
            ast_dict[C.F_BREPRON] = (make_ast_from_bool(self.bre_pron, self.selected_api), '')
        return ast_dict

    def get_ast_dict(self):
        return self._ast_dict

    def get_map(self):
        return self._map

    def get_saving_map(self):
        "Return a map specifically for saving to file"

        map_cp = copy.deepcopy(self._map)
        return map_cp

    def is_dirty(self):
        "Is config changed since initial state?"
        return self._dirty

    @property
    def version(self):
        """
        `config.json` schema version number

        New schema should never reuse a name on new field that was used by old
        schema and then abandoned by a semi-old schema, unless the purpose and
        usage is exactly the same as old schema. This guarantees backward and
        forward compatibility, similar to Prototype Buffer's claim.

        With great compatibility, usage of version is limited, merely to track
        schema change history. If this is the case, schema definitions are
        necessary. Schema history is useful for, e.g., making it clear where and
        how to modify when dropping support for an old version.
        """

        return self._map['version']

    @property
    def deck(self):
        return self._map['deck']

    @deck.setter
    @_set_dirty
    def deck(self, val: str):
        self._map['deck'] = val

    @property
    def selected_dict(self):
        return self._map['selected_dict']

    @selected_dict.setter
    @_set_dirty
    def selected_dict(self, val: str):
        self._map['selected_dict'] = val

    @property
    def selected_api(self):
        return self._map['selected_api']

    @selected_api.setter
    @_set_dirty
    def selected_api(self, val: str):
        self._map['selected_api'] = val

    @property
    def current_credential(self):
        return self._map['credentials'].setdefault(self.selected_dict, _T.Credential(cookie_encoded=''))

    @property
    def current_cookies(self):
        """return decoded cookies"""
        return dec_cookies(self.current_credential['cookie_encoded'])

    @current_cookies.setter
    def current_cookies(self, val: str):
        """
        val is plain text, encode it first
        Setter triggers `current_cookies` event, event argument is the plain val
        """

        cred = self.current_credential
        old = cred['cookie_encoded']
        new = enc_cookies(val)
        cred['cookie_encoded'] = new

        if old != new:
            self._dirty = True

        self._notify('current_cookies', val)

    @property
    def definition(self):
        return self._map[C.F_DEFINITION]

    @definition.setter
    @_set_dirty
    def definition(self, val: bool):
        self._map[C.F_DEFINITION] = val

    @property
    def image(self):
        return self._map[C.F_IMAGE]

    @image.setter
    @_set_dirty
    def image(self, val: bool):
        self._map[C.F_IMAGE] = val

    @property
    def sentence(self):
        return self._map[C.F_SENTENCE]

    @sentence.setter
    @_set_dirty
    def sentence(self, val: bool):
        self._map[C.F_SENTENCE] = val

    @property
    def phrase(self):
        return self._map[C.F_PHRASE]

    @phrase.setter
    @_set_dirty
    def phrase(self, val: bool):
        self._map[C.F_PHRASE] = val

    @property
    def ame_phonetic(self):
        return self._map[C.F_AMEPHONETIC]

    @ame_phonetic.setter
    @_set_dirty
    def ame_phonetic(self, val: bool):
        self._map[C.F_AMEPHONETIC] = val

    @property
    def bre_phonetic(self):
        return self._map[C.F_BREPHONETIC]

    @bre_phonetic.setter
    @_set_dirty
    def bre_phonetic(self, val: bool):
        self._map[C.F_BREPHONETIC] = val

    @property
    def bre_pron(self):
        return self._map[C.F_BREPRON]

    @bre_pron.setter
    @_set_dirty
    def bre_pron(self, val: bool):
        self._map[C.F_BREPRON] = val
        if val:
            self._map[C.F_AMEPRON] = False
            self._map[C.F_NOPRON] = False

    @property
    def ame_pron(self):
        return self._map[C.F_AMEPRON]

    @ame_pron.setter
    @_set_dirty
    def ame_pron(self, val: bool):
        self._map[C.F_AMEPRON] = val
        if val:
            self._map[C.F_BREPRON] = False
            self._map[C.F_NOPRON] = False

    @property
    def no_pron(self):
        return self._map[C.F_NOPRON]

    @no_pron.setter
    @_set_dirty
    def no_pron(self, val: bool):
        self._map[C.F_NOPRON] = val
        if val:
            self._map[C.F_BREPRON] = False
            self._map[C.F_AMEPRON] = False

    @property
    def advanced_fields(self):
        return self._map['advanced_fields']

    @property
    def advanced_enabled(self) -> bool:
        return self.advanced_fields['enabled']

    @advanced_enabled.setter
    @_set_dirty
    def advanced_enabled(self, val: bool):
        self.advanced_fields['enabled'] = val

    @property
    def advanced_enable_user_modules(self):
        return self.advanced_fields['enable_user_modules']

    @advanced_enable_user_modules.setter
    @_set_dirty
    def advanced_enable_user_modules(self, val: bool):
        self.advanced_fields['enable_user_modules'] = val

    @property
    def advanced_definition(self):
        return self.advanced_fields[C.F_DEFINITION]

    @advanced_definition.setter
    @_set_dirty
    def advanced_definition(self, val: str):
        self.advanced_fields[C.F_DEFINITION] = val
        self._ast_dict[C.F_DEFINITION] = adv_conf.make_ast(val)

    @property
    def advanced_sentence(self):
        return self.advanced_fields[C.F_SENTENCE]

    @advanced_sentence.setter
    @_set_dirty
    def advanced_sentence(self, val: str):
        self.advanced_fields[C.F_SENTENCE] = val
        self._ast_dict[C.F_SENTENCE] = adv_conf.make_ast(val)

    @property
    def advanced_image(self):
        return self.advanced_fields[C.F_IMAGE]

    @advanced_image.setter
    @_set_dirty
    def advanced_image(self, val: str):
        self.advanced_fields[C.F_IMAGE] = val
        self._ast_dict[C.F_IMAGE] = adv_conf.make_ast(val)

    @property
    def advanced_phrase(self):
        return self.advanced_fields[C.F_PHRASE]

    @advanced_phrase.setter
    @_set_dirty
    def advanced_phrase(self, val: str):
        self.advanced_fields[C.F_PHRASE] = val
        self._ast_dict[C.F_PHRASE] = adv_conf.make_ast(val)

    @property
    def advanced_AmEPhonetic(self):
        return self.advanced_fields[C.F_AMEPHONETIC]

    @advanced_AmEPhonetic.setter
    @_set_dirty
    def advanced_AmEPhonetic(self, val: str):
        self.advanced_fields[C.F_AMEPHONETIC] = val
        self._ast_dict[C.F_AMEPHONETIC] = adv_conf.make_ast(val)

    @property
    def advanced_BrEPhonetic(self):
        return self.advanced_fields[C.F_BREPHONETIC]

    @advanced_BrEPhonetic.setter
    @_set_dirty
    def advanced_BrEPhonetic(self, val: str):
        self.advanced_fields[C.F_BREPHONETIC] = val
        self._ast_dict[C.F_BREPHONETIC] = adv_conf.make_ast(val)

    @property
    def advanced_AmEPron(self):
        return self.advanced_fields[C.F_AMEPRON]

    @advanced_AmEPron.setter
    @_set_dirty
    def advanced_AmEPron(self, val: str):
        self.advanced_fields[C.F_AMEPRON] = val
        self._ast_dict[C.F_AMEPRON] = adv_conf.make_ast(val)

    @property
    def advanced_BrEPron(self):
        return self.advanced_fields[C.F_BREPRON]

    @advanced_BrEPron.setter
    @_set_dirty
    def advanced_BrEPron(self, val: str):
        self.advanced_fields[C.F_BREPRON] = val
        self._ast_dict[C.F_BREPRON] = adv_conf.make_ast(val)

    @property
    def congest(self):
        return self._map[C.F_CONGEST]

    @congest.setter
    @_set_dirty
    def congest(self, val: int):
        self._map[C.F_CONGEST] = val

    @property
    def user_agent(self):
        ua = self._map.get('user_agent')
        return ua if ua else C.USER_AGENT

    @user_agent.setter
    @_set_dirty
    def user_agent(self, val: str):
        self._map['user_agent'] = val

    @property
    def current_selected_groups(self) -> list[str]:
        return self._map['dict_saved_groups'].setdefault(self.selected_dict, [])

    @current_selected_groups.setter
    @_set_dirty
    def current_selected_groups(self, groups: list[str]):
        self._map['dict_saved_groups'][self.selected_dict] = groups

    def print(self):
        return str(self._map)
