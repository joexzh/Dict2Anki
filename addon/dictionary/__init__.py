from .._typing import AbstractDictionary
from . import eudict, youdao

dictionaries: dict[str, type[AbstractDictionary]] = {
    eudict.Dict.name: eudict.Dict,
    youdao.Dict.name: youdao.Dict
}

# TODO: iter user_files/dictionaries/ to add new dict