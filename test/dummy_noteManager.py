from ..addon._typing import QueryWordData
from ..addon.conf_model import Conf
from ..addon.constants import *
from .dummy_aqt import models, notes


def getDeckNames():
    return ['deck1', 'deck2']


def getOrCreateDeck(deck_name, model):
    return deck_name


def getOrCreateModel() -> models.NoteType:
    return models.NoteType()


def getOrCreateModelCardTemplate(modelObject):
    pass


def addNoteToDeck(deckObject, modelObject, conf: Conf, oneQueryResult: QueryWordData):
    pass


def getWordsByDeck(*args, **kwargs):
    return []


def getNoteIds(*args, **kwargs):
    return []


def removeNotes(noteIds):
    pass


def media_path(fileName: str) -> str:
    return ''


def writeNoteFields(*args, **kwargs):
    pass

def getNotesByDeckName(*args, **kwargs) -> list[notes.Note]:
    return [notes.Note(1)]