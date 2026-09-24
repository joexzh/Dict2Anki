from .dummy_aqt import models, notes

__all__ = [
    'getDeckNames',
    'getOrCreateDeck',
    'getOrCreateModel',
    'getOrCreateModelCardTemplate',
    'getWordsByDeck',
    'getNoteIds',
    'removeNotes',
    'updateNotes',
    'media_path',
    'getNotesByDeckName',
    'new_note',
    'set_flag',
]


def getDeckNames():
    return ['deck1', 'deck2']


def getOrCreateDeck(deck_name, model):
    return deck_name


def getOrCreateModel() -> models.NoteType:
    return models.NoteType()


def getOrCreateModelCardTemplate(modelObject):
    pass


def getWordsByDeck(*args, **kwargs):
    return []


def getNoteIds(*args, **kwargs):
    return []


def removeNotes(noteIds):
    pass


def updateNotes(notes):
    pass


def media_path(fileName: str) -> str:
    return ''


def getNotesByDeckName(*args, **kwargs) -> list[notes.Note]:
    return [notes.Note(1)]


def new_note(word, model):
    return notes.Note


def set_flag(notes, flag):
    pass
