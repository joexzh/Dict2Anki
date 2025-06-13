from ...addon.constants import *


NoteId = int


class Note:

    def __init__(self, nid):
        self.nid = nid

    def note_type(self):
        return {"name": MODEL_NAME}

    def __getitem__(self, item):
        return "a"

    def __setitem__(self, key, value):
        pass
