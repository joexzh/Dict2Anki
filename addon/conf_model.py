from . import _typing
from .constants import *


class Conf(_typing.ListenableModel):

    def __init__(self, conf):
        super().__init__()
        """require valid `config` returned from `mw.addonManager.getConfig`"""
        self._map: _typing.ConfigMap = conf

    def get_map(self):
        return self._map

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
            cred.append(_typing.Credential(username="", password="", cookie=""))
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
