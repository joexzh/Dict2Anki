from ..addon._typing import QueryWordData, ConfigMap
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


def addNoteToDeck(deckObject, modelObject, configMap: ConfigMap, oneQueryResult: QueryWordData):
    pass


def getWordsByDeck(*args, **kwargs):
    return []


def getNoteIds(*args, **kwargs):
    return []


def removeNotes(noteIds):
    pass


def media_path(fileName: str) -> str:
    return ''