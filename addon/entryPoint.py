from .addonWindow import Windows
from .noteFixer import NoteFixer


class EntryPoint:
    """EntryPoint is an entry point, and container that 'has' the things"""

    def __init__(self):
        self.windows = Windows()
        self._noteFixer = NoteFixer(self.windows)
