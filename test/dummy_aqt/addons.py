from ..helper import MockCallable, fresh_latest_confmap


class AddonManager:
    def __init__(self):
        self.writeConfig = MockCallable()
        self.getConfig = MockCallable()
        self.getConfig.return_value = fresh_latest_confmap()
