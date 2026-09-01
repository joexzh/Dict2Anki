from .. import misc
from .._typing import AbstractQueryAPI
from . import eudict, youdao

apis: dict[str, type[AbstractQueryAPI]] = {
    youdao.API.name: youdao.API,
    eudict.API.name: eudict.API,
}

# load apis from user_files/queryApi
# TODO: provide user option to load
# if enable_load: load
for mod in misc.load_all_modules('...user_files.queryApi', __package__):
    apis[mod.API.name] = mod.API
