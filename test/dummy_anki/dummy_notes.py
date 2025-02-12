from typing import NewType


NoteId = NewType("NoteId", int)


class Note:

    def __init__(self, nid):
        self.nid = nid

    @staticmethod
    def note_type():
        return dict()

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass
