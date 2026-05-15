from __future__ import annotations

import copy
import functools
import threading
import typing as T

from . import _typing
from . import constants as C
from .misc import dec_cookies, enc_cookies


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


class Conf(_typing.ListenableModel):
    lock = threading.Lock()
    default_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36'
    instance: T.Optional[Conf] = None

    @classmethod
    def getinstance(cls, conf):
        "Thread safe singleton instance"
        if cls.instance is None:
            with cls.lock:
                if cls.instance is None:
                    cls.instance = Conf(conf)
        return cls.instance

    @classmethod
    def delinstance(cls):
        "Must call only when closing addon main window"
        if cls.instance:
            cls.instance = None

    @classmethod
    def user_agent_or_default(cls):
        if cls.instance is None:
            return cls.default_user_agent
        return cls.instance.user_agent

    def __init__(self, conf):
        super().__init__()
        # require valid `config` returned from `mw.addonManager.getConfig`
        self._map: _typing.ConfigMap = conf
        self._dirty = False

        # `cookie_encoded` is added at version 2.
        # Case 1: `cookie` is not empty. It's the first time from v1 to v2,
        #   should encode `cookie` and write encoded result to `cookie_encoded`.
        # Case 2: `cookie_encoded` not in cred. It's the first time from v1 to
        #   v2, set default value '' to it.
        # Case 3: `cookie_encoded` is not empty. It's normal v2 config, should
        #   decode `cookie_encoded` and write decoded result to `cookie`.
        creds = self._map['credential']
        for cred in creds:
            if cred['cookie'] != '':
                # case 1
                cred['cookie_encoded'] = enc_cookies(cred['cookie'])
                self._dirty = True
            elif 'cookie_encoded' not in cred:
                # case 2
                cred['cookie_encoded'] = ''
                self._dirty = True
            elif cred['cookie_encoded'] != '':
                # case 3
                cred['cookie'] = dec_cookies(cred['cookie_encoded'])

    def get_map(self):
        return self._map

    def get_saving_map(self):
        "Return a map specifically for saving to file"

        map_cp = copy.deepcopy(self._map)
        for cred in map_cp['credential']:
            cred['cookie'] = ''

        # According to https://addon-docs.ankiweb.net/addon-config.html ,
        # mw.addonManager.getConfig() prefers keys in meta.json, then falls back
        # to the default config.json, internally something like this:
        # `defaults.update(meta_config)`
        #
        # So delete any key that must not override the default value
        map_cp.pop('version', None)
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

        # compatible to version 1
        return self._map.get('version', 1)

    @property
    def deck(self):
        return self._map['deck']

    @deck.setter
    @_set_dirty
    def deck(self, val: str):
        self._map['deck'] = val

    @property
    def selected_dict(self):
        return self._map['selectedDict']

    @selected_dict.setter
    @_set_dirty
    def selected_dict(self, val: int):
        self._map['selectedDict'] = val

    @property
    def selected_api(self):
        return self._map['selectedApi']

    @selected_api.setter
    @_set_dirty
    def selected_api(self, val: int):
        self._map['selectedApi'] = val

    @property
    def current_credential(self):
        cred = self._map['credential']
        while len(cred) < self.selected_dict + 1:
            cred.append(_typing.Credential(cookie='', cookie_encoded=''))
        return cred[self.selected_dict]

    @property
    def current_cookies(self):
        return self.current_credential['cookie']

    @current_cookies.setter
    @_set_dirty
    def current_cookies(self, val: str):
        "setter triggers `current_cookies` event, property value as event argument"

        cred = self.current_credential
        cred['cookie'] = val

        # Encode cookies to prevent disk scanning malware from easily collecting
        # sensitive data.
        cred['cookie_encoded'] = enc_cookies(cred['cookie'])

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
    def congest(self):
        return self._map[C.F_CONGEST]

    @congest.setter
    @_set_dirty
    def congest(self, val: int):
        self._map[C.F_CONGEST] = val

    @property
    def user_agent(self):
        # compatible to version 1
        return self._map.get('user_agent', self.default_user_agent)

    @user_agent.setter
    @_set_dirty
    def user_agent(self, val: str):
        self._map['user_agent'] = val

    @property
    def current_selected_groups(self) -> list[str]:
        try:
            return self._map['selectedGroup'][self.selected_dict]
        except (KeyError, IndexError):
            return []

    @current_selected_groups.setter
    @_set_dirty
    def current_selected_groups(self, groups: list[str]):
        selected_groups = self._map.get('selectedGroup')

        if selected_groups is None:
            selected_groups = self._map['selectedGroup'] = []

        while len(selected_groups) < self.selected_dict + 1:
            selected_groups.append([])

        selected_groups[self.selected_dict] = groups

    def print(self):
        return str(self._map)
