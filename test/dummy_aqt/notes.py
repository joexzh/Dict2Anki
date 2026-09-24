from addon import constants as C

NoteId = int


class Note:
    def __init__(self, nid):
        self.nid = nid
        self._map = {}

    def note_type(self):
        return {'name': C.MODEL_NAME}

    def __getitem__(self, item):
        return self._map[item]

    def __setitem__(self, key, value):
        self._map[key] = value
