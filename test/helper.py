import json
import os
import typing

from ..addon import _typing


class MockCallable:
    def __init__(self):
        self.called = 0
        self.called_with: typing.Any = None
        self.return_value: typing.Any = None

    def __call__(self, *args, **kwargs):
        self.called += 1
        self.called_with = (args, kwargs)
        return self.return_value


_CONFIG_V1 = """{
  "deck": "",
  "selectedDict": 0,
  "selectedGroup": [[], []],
  "selectedApi": 0,
  "credential": [],
  "definition": true,
  "sentence": true,
  "image": true,
  "phrase": true,
  "AmEPhonetic": true,
  "BrEPhonetic": true,
  "BrEPron": false,
  "AmEPron": true,
  "noPron": false,
  "congest": 120
}
"""

# should different from `addon.Conf.default_user_agent`
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36'
)

_CONFIG_V2 = f"""{{
  "version": 2,
  "deck": "",
  "selectedDict": 0,
  "selectedGroup": [[], []],
  "selectedApi": 0,
  "credential": [
    {{
      "cookie": "",
      "cookie_encoded": ""
    }},
    {{
      "cookie": "",
      "cookie_encoded": ""
    }}
  ],
  "definition": true,
  "sentence": true,
  "image": true,
  "phrase": true,
  "AmEPhonetic": true,
  "BrEPhonetic": true,
  "BrEPron": false,
  "AmEPron": true,
  "noPron": false,
  "congest": 120,
  "user_agent": "{USER_AGENT}"
}}
"""


def env_conf_v():
    return int(os.getenv('DICT2ANKI_CONFIGV', '1'))


def fresh_config_dict() -> _typing.ConfigMap:
    if env_conf_v() >= 2:
        return json.loads(_CONFIG_V2)
    else:
        return json.loads(_CONFIG_V1)
