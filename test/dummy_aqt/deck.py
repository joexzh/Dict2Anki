from typing import Any

DeckDict = dict[str, Any]


class Deck:
    def id(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        pass

    def reset(self, *args, **kwargs):
        pass

    def save(self, *args, **kwargs):
        pass

    def all(self) -> list[DeckDict]:
        return []
