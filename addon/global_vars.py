from __future__ import annotations

import typing as T
from . import constants as C

if T.TYPE_CHECKING:
    from .conf_model import Conf


conf_instance: T.Optional[Conf] = None


def user_agent():
    if conf_instance is None:
        return C.USER_AGENT
    return conf_instance.user_agent
