import json
import os
import typing as T

from addon import _typing as _T


class MockCallable:
    def __init__(self):
        self.called = 0
        self.called_with: T.Any = None
        self.return_value: T.Any = None

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

# should different from `C.USER_AGENT`
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
      "cookie_encoded": ""
    }},
    {{
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

_CONFIG_V3 = """{
  "version": 3,
  "deck": "",
  "selected_dict": "欧路词典",
  "dict_saved_groups": {},
  "selected_api": "有道 API",
  "credentials": {},
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
  "user_agent": ""
}
"""

_CONFIG_V4 = """{
  "version": 4,
  "deck": "",
  "selected_dict": "欧路词典",
  "dict_saved_groups": {},
  "selected_api": "有道 API",
  "credentials": {},
  "definition": true,
  "sentence": true,
  "image": true,
  "phrase": true,
  "AmEPhonetic": true,
  "BrEPhonetic": true,
  "BrEPron": false,
  "AmEPron": true,
  "noPron": false,
  "advanced_fields": {
    "enabled": false,
    "enable_use_modules": false,
    "definition": "",
    "sentence": "",
    "image": "",
    "phrase": "",
    "AmEPhonetic": "",
    "BrEPhonetic": "",
    "AmEPron": "",
    "BrEPron": ""
  },
  "congest": 120,
  "user_agent": ""
}
"""


def fresh_v1_confmap() -> _T.ConfigMap:
    return json.loads(_CONFIG_V1)


def fresh_v2_confmap() -> _T.ConfigMap:
    return json.loads(_CONFIG_V2)


def fresh_v3_confmap() -> _T.ConfigMap:
    return json.loads(_CONFIG_V3)


def fresh_v4_confmap() -> _T.ConfigMap:
    return json.loads(_CONFIG_V4)


def fresh_latest_confmap() -> _T.ConfigMap:
    return fresh_v4_confmap()
