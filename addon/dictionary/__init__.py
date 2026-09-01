from .. import misc
from .._typing import AbstractDictionary
from . import eudict, youdao

dictionaries: dict[str, type[AbstractDictionary]] = {eudict.Dict.name: eudict.Dict, youdao.Dict.name: youdao.Dict}

# load dictionaries from user_files/dictionary
# TODO: provide user option to load
# if enable_load: load
for mod in misc.load_all_modules('...user_files.dictionary', __package__):
    dictionaries[mod.Dict.name] = mod.Dict
