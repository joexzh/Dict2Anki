from .. import misc
from .._typing import AbstractDictionary
from . import eudict, youdao

dictionaries: dict[str, type[AbstractDictionary]] = {eudict.Dict.name: eudict.Dict, youdao.Dict.name: youdao.Dict}

default_dict = youdao.Dict


def load_usr_mod():
    "load user modules in user_files/dictionary"
    for mod in misc.load_all_modules('..user_files.dictionary', __package__):
        if hasattr(mod, 'Dict') and isinstance(mod.Dict, type) and issubclass(mod.Dict, AbstractDictionary):
            dictionaries[mod.Dict.name] = mod.Dict
