from .. import misc
from .._typing import AbstractQueryAPI
from . import eudict, youdao

apis: dict[str, type[AbstractQueryAPI]] = {
    youdao.API.name: youdao.API,
    eudict.API.name: eudict.API,
}

default_api = youdao.API


def load_usr_mod():
    "load user modules in user_files/queryApi"
    for mod in misc.load_all_modules('..user_files.queryApi', __package__):
        if hasattr(mod, 'API') and isinstance(mod.API, type) and issubclass(mod.API, AbstractQueryAPI):
            apis[mod.API.name] = mod.API
