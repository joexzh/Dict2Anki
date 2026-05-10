from . import _typing
from .constants import *
from .misc import dec_cookies, enc_cookies


class Conf(_typing.ListenableModel):

    def __init__(self, conf):
        super().__init__()
        """require valid `config` returned from `mw.addonManager.getConfig`"""
        self._map: _typing.ConfigMap = conf

        if self.version >= 2:
            # `cookie_encoded` is added at version 2. If it's not empty in
            # config file, the raw `cookie` field must be empty. Then we should
            # decode its value and set to `cookie` field.
            creds = self._map["credential"]
            for cred in creds:
                if cred["cookie_encoded"] == "":
                    continue
                cred["cookie"] = dec_cookies(cred["cookie_encoded"])

    def encode_cookies(self):
        """Encode cookies to prevent disk scanning malware to easily collect
        sensitive data.

        We didn't track whether cookies are dirty, so this function must and
        only be called just before saving to config file"""

        # Store encode result in `cookie_encoded`, clear raw `cookies`
        # afterwards.
        creds = self._map["credential"]
        for cred in creds:
            if cred["cookie"] == "":
                continue
            cred["cookie_encoded"] = enc_cookies(cred["cookie"])
            cred["cookie"] = ""

    def get_map(self):
        return self._map

    @property
    def version(self):
        """
        `config.json` schema version number
        """

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
    def deck(self, val: str):
        self._map["deck"] = val

    @property
    def selected_dict(self):
        return self._map["selectedDict"]

    @selected_dict.setter
    def selected_dict(self, val: int):
        self._map["selectedDict"] = val

    @property
    def selected_api(self):
        return self._map["selectedApi"]

    @selected_api.setter
    def selected_api(self, val: int):
        self._map["selectedApi"] = val

    @property
    def current_credential(self):
        cred = self._map["credential"]
        while len(cred) < self.selected_dict + 1:
            cred.append(
                _typing.Credential(username="",
                                   password="",
                                   cookie="",
                                   cookie_encoded=""))
        return cred[self.selected_dict]

    @property
    def current_username(self):
        return self.current_credential["username"]

    @current_username.setter
    def current_username(self, val: str):
        self.current_credential["username"] = val

    @property
    def current_password(self):
        return self.current_credential["password"]

    @current_password.setter
    def current_password(self, val: str):
        self.current_credential["password"] = val

    @property
    def current_cookies(self):
        return self.current_credential["cookie"]

    @current_cookies.setter
    def current_cookies(self, val: str):
        """setter triggers `current_cookies` event, property value as event argument"""
        self.current_credential["cookie"] = val
        self._notify("current_cookies", val)

    @property
    def definition(self):
        return self._map[F_DEFINITION]

    @definition.setter
    def definition(self, val: bool):
        self._map[F_DEFINITION] = val

    @property
    def image(self):
        return self._map[F_IMAGE]

    @image.setter
    def image(self, val: bool):
        self._map[F_IMAGE] = val

    @property
    def sentence(self):
        return self._map[F_SENTENCE]

    @sentence.setter
    def sentence(self, val: bool):
        self._map[F_SENTENCE] = val

    @property
    def phrase(self):
        return self._map[F_PHRASE]

    @phrase.setter
    def phrase(self, val: bool):
        self._map[F_PHRASE] = val

    @property
    def ame_phonetic(self):
        return self._map[F_AMEPHONETIC]

    @ame_phonetic.setter
    def ame_phonetic(self, val: bool):
        self._map[F_AMEPHONETIC] = val

    @property
    def bre_phonetic(self):
        return self._map[F_BREPHONETIC]

    @bre_phonetic.setter
    def bre_phonetic(self, val: bool):
        self._map[F_BREPHONETIC] = val

    @property
    def bre_pron(self):
        return self._map[F_BREPRON]

    @bre_pron.setter
    def bre_pron(self, val: bool):
        self._map[F_BREPRON] = val
        if val:
            self._map[F_AMEPRON] = False
            self._map[F_NOPRON] = False

    @property
    def ame_pron(self):
        return self._map[F_AMEPRON]

    @ame_pron.setter
    def ame_pron(self, val: bool):
        self._map[F_AMEPRON] = val
        if val:
            self._map[F_BREPRON] = False
            self._map[F_NOPRON] = False

    @property
    def no_pron(self):
        return self._map[F_NOPRON]

    @no_pron.setter
    def no_pron(self, val: bool):
        self._map[F_NOPRON] = val
        if val:
            self._map[F_BREPRON] = False
            self._map[F_AMEPRON] = False

    @property
    def congest(self):
        return self._map[F_CONGEST]

    @congest.setter
    def congest(self, val: int):
        self._map[F_CONGEST] = val

    @property
    def current_selected_groups(self) -> list[str]:
        try:
            return self._map["selectedGroup"][self.selected_dict]
        except:
            return []

    @current_selected_groups.setter
    def current_selected_groups(self, groups: list[str]):
        if self._map["selectedGroup"] == None:
            self._map["selectedGroup"] = []
        while len(self._map["selectedGroup"]) < self.selected_dict + 1:
            self._map["selectedGroup"].append([])

        self._map["selectedGroup"][self.selected_dict] = groups

    def print(self):
        return str(self._map)
