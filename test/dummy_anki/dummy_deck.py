from typing import Any

DeckDict = dict[str, Any]


class Deck:
    @staticmethod
    def id(*args, **kwargs):
        pass

    @staticmethod
    def get(*args, **kwargs):
        pass

    @staticmethod
    def reset(*args, **kwargs):
        pass

    @staticmethod
    def save(*args, **kwargs):
        pass

    @staticmethod
    def all() -> list[DeckDict]:
        return []
