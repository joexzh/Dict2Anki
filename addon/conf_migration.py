from __future__ import annotations

import typing as T

from . import _typing as _T
from . import dictionary, queryApi
from .misc import enc_cookies

if T.TYPE_CHECKING:
    from .conf_model import Conf


LATEST_VERSION = 3


def migrate_v1_v2(confmap: _T.ConfigMap):
    """
    Migrate version 1 to 2
    - Add `cookie_encoded`
    - Remove `cookie`
    """
    confmap['version'] = 2
    creds = confmap['credential']
    cookie_enc = 'cookie_encoded'

    for cred in creds:
        cred.pop('username', None)
        cred.pop('password', None)

        if cred['cookie'] != '':
            cred[cookie_enc] = enc_cookies(cred['cookie'])

        if cookie_enc not in cred:
            cred[cookie_enc] = ''

        del cred['cookie']


def migrate_v2_v3(confmap: _T.ConfigMap):
    """
    Migrate version 2 to 3

    version 2:
    - `selectedDict` 0 is eudic, 1 is youdao
    - `selectedApi` 0 is youdao, 1 is eudic
    - `selectedGroup` at 0 is eudic, 1 is youdao
    - `credential` at 0 is eudic, 1 is youdao

    version 3:
    - `selectedDict`  -->  `selected_dict`
    - `selectedApi`   -->  `selected_api`
    - `selectedGroup` -->  `dict_saved_groups`
    - `credential`    -->  `credentials`
    """
    confmap['version'] = 3

    if confmap['selectedDict'] == 0:
        confmap['selected_dict'] = dictionary.eudict.Dict.name
    else:
        # default is youdao
        confmap['selected_dict'] = dictionary.youdao.Dict.name

    del confmap['selectedDict']

    if confmap['selectedApi'] == 1:
        confmap['selected_api'] = queryApi.eudict.API.name
    else:
        # default is youdao
        confmap['selected_api'] = queryApi.youdao.API.name

    del confmap['selectedApi']

    groups = confmap['dict_saved_groups'] = {}
    for i, group in enumerate(confmap['selectedGroup']):
        if i == 0:
            groups[dictionary.eudict.Dict.name] = group
        elif i == 1:
            groups[dictionary.youdao.Dict.name] = group

    del confmap['selectedGroup']

    creds = confmap['credentials'] = {}
    for i, cred in enumerate(confmap['credential']):
        if i == 0:
            creds[dictionary.eudict.Dict.name] = cred
        elif i == 1:
            creds[dictionary.youdao.Dict.name] = cred

    del confmap['credential']


def migrate_v3_v4(confmap: _T.ConfigMap):
    confmap['version'] = 4


def migrate_version(conf: Conf):
    """
    Migrate to latest version
    """

    # previous version user's meta.json doesn't have a version, force to correct
    # it. I mess up.
    if 'selectedDict' in conf._map:
        migrate_v1_v2(conf._map)
        migrate_v2_v3(conf._map)
        conf._dirty = True

    if conf.version == 3:
        migrate_v3_v4(conf._map)
        conf._dirty = True
