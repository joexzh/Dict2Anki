import typing
from .misc import Mask


class Credential(typing.TypedDict):
    username: str
    password: str
    cookie: str


class Config(typing.TypedDict):
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


class QueryWordData(typing.TypedDict):
    term: str
    definition: list[str]
    phrase: list[tuple[str, str]]
    image: str
    sentence: list[tuple[str, str]]
    BrEPhonetic: str
    AmEPhonetic: str
    BrEPron: str
    AmEPron: str