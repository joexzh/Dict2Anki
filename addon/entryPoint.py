from .addonWindow import Windows
from . import repair


class EntryPoint:
    """EntryPoint is an entry point, and container that 'has' the things"""

    def __init__(self):
        self.windows = Windows()
        self._repair = repair.make_repair(self.windows)
