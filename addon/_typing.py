import typing as T
from abc import ABC, abstractmethod

import requests


class Mask:
    def __init__(self, info):
        self.info = info

    def __repr__(self):
        return '*******'

    def __str__(self):
        return self.info


class Credential(T.TypedDict):
    cookie_encoded: str


class Advanced_Fields(T.TypedDict):
    enabled: bool
    enable_user_modules: bool
    definition: str
    sentence: str
    image: str
    phrase: str
    AmEPhonetic: str
    BrEPhonetic: str
    BrEPron: str
    AmEPron: str


class ConfigMap(T.TypedDict):
    version: int
    deck: str

    selectedDict: int
    'deprecated'

    selected_dict: str
    'dict name'

    selectedGroup: list[list[str]]
    'deprecated'

    dict_saved_groups: dict[str, list[str]]

    selectedApi: int
    'deprecated'

    selected_api: str
    'api name'

    credential: list[Credential]
    'deprecated'

    credentials: dict[str, Credential]
    definition: bool
    sentence: bool
    image: bool
    phrase: bool
    AmEPhonetic: bool
    BrEPhonetic: bool
    BrEPron: bool
    AmEPron: bool
    noPron: bool
    congest: int
    user_agent: str

    advanced_fields: Advanced_Fields


class AbstractDictionary(ABC):
    name: str
    '`name` has to be unique and never changes, otherwise may cause unexpected result somewhere'

    loginUrl: str
    timeout: int
    headers: dict[str, str]
    groups: list[tuple[str, str]] = []

    @staticmethod
    @abstractmethod
    def loginCheckCallbackFn(cookie: dict, content: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def checkCookie(cls, cookie: dict) -> bool:
        pass

    @classmethod
    @abstractmethod
    def getGroups(cls) -> list[tuple[str, str]]:
        pass

    @classmethod
    @abstractmethod
    def getTotalPage(cls, groupName: str, groupId: str) -> int:
        pass

    @classmethod
    @abstractmethod
    def getWordsByPage(cls, pageNo: int, groupName: str, groupId: str) -> list[str]:
        pass


class QueryWordData(T.TypedDict):
    term: str
    definition: list[str]
    phrase: list[tuple[str, str]]
    image: str
    sentence: list[tuple[str, str]]
    BrEPhonetic: str
    AmEPhonetic: str
    BrEPron: str
    AmEPron: str


class AbstractQueryAPI(ABC):
    name: str
    '`name` has to be unique and never changes, otherwise may cause unexpected result somewhere'

    session: requests.Session
    'mostly for audio download'

    @classmethod
    @abstractmethod
    def query(cls, word: str) -> T.Optional[QueryWordData]:
        """
        查询
        :param word: 单词
        :return: 查询结果 dict(term, definition, phrase, image, sentence, BrEPhonetic, AmEPhonetic, BrEPron, AmEPron)
        """
        pass


class ListenableModel:
    def __init__(self):
        self._listeners: dict[str, list[T.Callable[[T.Any], T.Any]]] = {}

    def _notify(self, event: str, val):
        if event in self._listeners:
            for fn in self._listeners[event]:
                fn(val)

    def listen(self, event: str, fn: T.Callable[[T.Any], T.Any]):
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(fn)

    def unlisten(self, event: str, fn: T.Callable[[T.Any], T.Any]):
        if event in self._listeners:
            self._listeners[event].remove(fn)
