from ..helper import MockCallable, fresh_config_dict


class AddonManager:
    def __init__(self):
        self.writeConfig = MockCallable()
        self.getConfig = MockCallable()
        self.getConfig.return_value = fresh_config_dict()
