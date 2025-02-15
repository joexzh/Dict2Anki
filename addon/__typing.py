from abc import ABC, abstractmethod
from typing import TypedDict, Optional
from bs4 import BeautifulSoup


class Mask:
    def __init__(self, info):
        self.info = info

    def __repr__(self):
        return '*******'

    def __str__(self):
        return self.info


class Credential(TypedDict):
    username: str
    password: str
    cookie: str


class Config(TypedDict):
    deck: str
    selectedDict: int
    selectedGroup: list[list[str]]
    selectedApi: int
    username: str
    password: Mask
    cookie: Mask
    definition: bool
    sentence: bool
    image: bool
    phrase: bool
    AmEPhonetic: bool
    BrEPhonetic: bool
    BrEPron: bool
    AmEPron: bool
    noPron: bool


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


class AbstractDictionary(ABC):
    name: str
    loginUrl: str
    timeout: int
    headers: dict[str, str]

    @staticmethod
    @abstractmethod
    def loginCheckCallbackFn(cookie: dict, content: str):
        pass

    @abstractmethod
    def __init__(self):
        self.groups: list[tuple[str, str]] = []
        self.indexSoup: Optional[BeautifulSoup] = None

    @abstractmethod
    def checkCookie(self, cookie: dict) -> bool:
        pass

    @abstractmethod
    def getGroups(self) -> list[tuple[str, str]]:
        pass

    @abstractmethod
    def getTotalPage(self, groupName: str, groupId: str) -> int:
        pass

    @abstractmethod
    def getWordsByPage(self, pageNo: int, groupName: str, groupId: str) -> list[str]:
        pass


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