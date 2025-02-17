from ..addon._typing import Config, QueryWordData
from ..addon.constants import *
from .dummy_anki import models

def getDeckNames():
    return ['deck1', 'deck2']


def getOrCreateDeck(deck_name, model):
    return deck_name


def getOrCreateModel() -> models.NoteType:
    return models.NoteType()


def getOrCreateModelCardTemplate(modelObject):
    pass


def addNoteToDeck(deckObject, modelObject, currentConfig: Config, oneQueryResult: QueryWordData):
    pass


def getWordsByDeck(*args, **kwargs):
    return []


def getNoteIds(*args, **kwargs):
    return []


def removeNotes(noteIds):
    pass


def media_path(fileName: str) -> str:
    return ''