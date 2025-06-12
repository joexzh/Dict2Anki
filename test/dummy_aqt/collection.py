from .deck import Deck
from .models import Model
from . import notes


class Collection:
    def __init__(self, deck, model):
        self.decks: Deck = deck
        self.models: Model = model

    def reset(self):
        pass

    def remove_notes(self, *args, **kwargs):
        pass

    def get_note(self, *args, **kwargs):
        return notes.Note(1)

    def find_notes(self, *args, **kwargs):
        return []

    def new_note(self, *args):
        return notes.Note(123)

    def add_note(self, *args, **kwargs):
        pass

    def update_notes(self, *args, **kwargs):
        pass

    def update_note(self, *args, **kwargs):
        pass