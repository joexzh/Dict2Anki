from .addonWindow import Windows
from .repair import Repair


class EntryPoint:
    """EntryPoint is an entry point, and container that 'has' the things"""

    def __init__(self):
        self.windows = Windows()
        self._noteFixer = Repair(self.windows)
