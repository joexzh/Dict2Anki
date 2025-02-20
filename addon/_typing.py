from abc import ABC, abstractmethod
from typing import Optional, TypedDict

from bs4 import BeautifulSoup


class Mask:
    def __init__(self, info):
        self.info = info

    def __repr__(self):
        return "*******"

    def __str__(self):
        return self.info


class Credential(TypedDict):
    username: str
    password: str
    cookie: str


class ConfigMap(TypedDict):
    deck: str
    selectedDict: int
    selectedGroup: list[list[str]]
    selectedApi: int
    credential: list[Credential]
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


class AbstractDictionary(ABC):
    name: str
    loginUrl: str
    timeout: int
    headers: dict[str, str]
    groups: list[tuple[str, str]] = []

    @staticmethod
    @abstractmethod
    def loginCheckCallbackFn(cookie: dict, content: str):
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


class QueryWordData(TypedDict):
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

    @classmethod
    @abstractmethod
    def query(cls, word: str) -> Optional[QueryWordData]:
        """
        查询
        :param word: 单词
        :return: 查询结果 dict(term, definition, phrase, image, sentence, BrEPhonetic, AmEPhonetic, BrEPron, AmEPron)
        """
        pass
