from __future__ import annotations

import copy
import functools
import threading
import typing as T

from . import _typing
from .constants import *
from .misc import dec_cookies, enc_cookies


def _set_dirty(method):
    "Conf setter decorator, sets self._dirty=True whenever it's called"

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self._dirty = True
        return method(self, *args, **kwargs)

    return wrapper


class Conf(_typing.ListenableModel):
    lock = threading.Lock()
    default_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
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
    def user_agent_or_default(cls):
        if cls.instance is None:
            return cls.default_user_agent
        return cls.instance.user_agent

    def __init__(self, conf):
        super().__init__()
        # require valid `config` returned from `mw.addonManager.getConfig`
        self._map: _typing.ConfigMap = conf
        self._dirty = False

        if self.version >= 2:
            # `cookie_encoded` is added at version 2. If it's not empty in
            # config file, the raw `cookie` field must be empty. Then we should
            # decode its value and set to `cookie` field.
            creds = self._map["credential"]
            for cred in creds:
                if cred["cookie_encoded"] == "":
                    continue
                cred["cookie"] = dec_cookies(cred["cookie_encoded"])

    def get_map(self):
        return self._map

    def get_saving_map(self):
        "Return a map specifically for saving to file"
        map_cp = copy.deepcopy(self._map)
        if self.version >= 2:
            for cred in map_cp["credential"]:
                cred["cookie"] = ""
        return map_cp

    def is_dirty(self):
        "Is config changed since initial state?"
        return self._dirty

    @property
    def version(self):
        "`config.json` schema version number"

        # `config.json` file evolves, normally latest config.json is shipped
        # with latest code. If something wrong happens to Anki's add-on update
        # system, or user accidentally pastes in a config.json with older
        # version, which it's an older file, we are able to look at the version
        # number and do the proper thing.
        if "version" not in self._map:
            return 1
        return self._map["version"]

    @property
    def deck(self):
        return self._map["deck"]

    @deck.setter
    @_set_dirty
    def deck(self, val: str):
        self._map["deck"] = val

    @property
    def selected_dict(self):
        return self._map["selectedDict"]

    @selected_dict.setter
    @_set_dirty
    def selected_dict(self, val: int):
        self._map["selectedDict"] = val

    @property
    def selected_api(self):
        return self._map["selectedApi"]

    @selected_api.setter
    @_set_dirty
    def selected_api(self, val: int):
        self._map["selectedApi"] = val

    @property
    def current_credential(self):
        cred = self._map["credential"]
        while len(cred) < self.selected_dict + 1:
            cred.append(
                _typing.Credential(
                    username="", password="", cookie="", cookie_encoded=""
                )
            )
        return cred[self.selected_dict]

    @property
    def current_username(self):
        return self.current_credential["username"]

    @current_username.setter
    @_set_dirty
    def current_username(self, val: str):
        self.current_credential["username"] = val

    @property
    def current_password(self):
        return self.current_credential["password"]

    @current_password.setter
    @_set_dirty
    def current_password(self, val: str):
        self.current_credential["password"] = val

    @property
    def current_cookies(self):
        return self.current_credential["cookie"]

    @current_cookies.setter
    @_set_dirty
    def current_cookies(self, val: str):
        "setter triggers `current_cookies` event, property value as event argument"
        cred = self.current_credential
        cred["cookie"] = val

        if self.version >= 2:
            # Encode cookies to prevent disk scanning malware to easily collect
            # sensitive data.
            cred["cookie_encoded"] = enc_cookies(cred["cookie"])

        self._notify("current_cookies", val)

    @property
    def definition(self):
        return self._map[F_DEFINITION]

    @definition.setter
    @_set_dirty
    def definition(self, val: bool):
        self._map[F_DEFINITION] = val

    @property
    def image(self):
        return self._map[F_IMAGE]

    @image.setter
    @_set_dirty
    def image(self, val: bool):
        self._map[F_IMAGE] = val

    @property
    def sentence(self):
        return self._map[F_SENTENCE]

    @sentence.setter
    @_set_dirty
    def sentence(self, val: bool):
        self._map[F_SENTENCE] = val

    @property
    def phrase(self):
        return self._map[F_PHRASE]

    @phrase.setter
    @_set_dirty
    def phrase(self, val: bool):
        self._map[F_PHRASE] = val

    @property
    def ame_phonetic(self):
        return self._map[F_AMEPHONETIC]

    @ame_phonetic.setter
    @_set_dirty
    def ame_phonetic(self, val: bool):
        self._map[F_AMEPHONETIC] = val

    @property
    def bre_phonetic(self):
        return self._map[F_BREPHONETIC]

    @bre_phonetic.setter
    @_set_dirty
    def bre_phonetic(self, val: bool):
        self._map[F_BREPHONETIC] = val

    @property
    def bre_pron(self):
        return self._map[F_BREPRON]

    @bre_pron.setter
    @_set_dirty
    def bre_pron(self, val: bool):
        self._map[F_BREPRON] = val
        if val:
            self._map[F_AMEPRON] = False
            self._map[F_NOPRON] = False

    @property
    def ame_pron(self):
        return self._map[F_AMEPRON]

    @ame_pron.setter
    @_set_dirty
    def ame_pron(self, val: bool):
        self._map[F_AMEPRON] = val
        if val:
            self._map[F_BREPRON] = False
            self._map[F_NOPRON] = False

    @property
    def no_pron(self):
        return self._map[F_NOPRON]

    @no_pron.setter
    @_set_dirty
    def no_pron(self, val: bool):
        self._map[F_NOPRON] = val
        if val:
            self._map[F_BREPRON] = False
            self._map[F_AMEPRON] = False

    @property
    def congest(self):
        return self._map[F_CONGEST]

    @congest.setter
    @_set_dirty
    def congest(self, val: int):
        self._map[F_CONGEST] = val

    @property
    def user_agent(self):
        if self.version >= 2:
            return self._map["user_agent"]
        return self.default_user_agent

    @property
    def current_selected_groups(self) -> list[str]:
        try:
            return self._map["selectedGroup"][self.selected_dict]
        except:
            return []

    # Can't simply use @set_dirty decorator, this function will trigger
    # every time when a user click "yes" to query online notebook, see
    # `addonWindow`
    @current_selected_groups.setter
    def current_selected_groups(self, groups: list[str]):
        if "selectedGroup" not in self._map:
            self._map["selectedGroup"] = []

        selected_groups = self._map["selectedGroup"]

        while len(selected_groups) < self.selected_dict + 1:
            selected_groups.append([])

        if selected_groups[self.selected_dict] != groups:
            selected_groups[self.selected_dict] = groups
            self._dirty = True

    def print(self):
        return str(self._map)
