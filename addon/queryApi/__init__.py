from .._typing import AbstractQueryAPI
from . import eudict, vcom_funny, youdao

apis: dict[str, type[AbstractQueryAPI]] = {
    youdao.API.name: youdao.API,
    eudict.API.name: eudict.API,
    vcom_funny.API.name: vcom_funny.API,
}

# TODO: scan user_files/apis to add new api
