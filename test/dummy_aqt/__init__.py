from .addonManager import AddonManager
from .collection import Collection
from .deck import Deck
from .models import Model


class mw:
    addonManager = AddonManager()
    col = Collection(Deck(), Model())

    @staticmethod
    def reset():
        pass
