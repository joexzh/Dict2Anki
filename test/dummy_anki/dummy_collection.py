from typing import Any
from test.dummy_anki.dummy_deck import Deck
from test.dummy_anki.dummy_notes import Note, NoteId
from test.dummy_anki.dummy_models import Model



class Collection:
    decks = Deck
    models = Model

    @staticmethod
    def reset():
        pass

    @staticmethod
    def remove_notes(noteIds: list[NoteId]):
        pass

    @staticmethod
    def get_note(NoteId):
        return Note(NoteId)

    @staticmethod
    def find_notes(query) -> list[NoteId]:
        return []

    @staticmethod
    def new_note(*args):
        return Note(123)

    @staticmethod
    def add_note(note: Note, *args):
        pass