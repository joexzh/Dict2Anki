from .addons import AddonManager
from .collection import Collection
from .decks import Deck
from .models import Model


class mw:
    addonManager = AddonManager()
    col = Collection(Deck(), Model())

    @staticmethod
    def reset():
        pass
