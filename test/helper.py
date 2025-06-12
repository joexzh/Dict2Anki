import json
import typing


class MockCallable:
    def __init__(self):
        self.called = 0
        self.called_with: typing.Any = None
        self.return_value: typing.Any = None

    def __call__(self, *args, **kwargs):
        self.called += 1
        self.called_with = (args, kwargs)
        return self.return_value


def fresh_config_dict():
    return json.loads(
        """{
  "deck": "",
  "selectedDict": 0,
  "selectedGroup": [[], []],
  "selectedApi": 0,
  "credential": [
    {
      "username": "",
      "password": "",
      "cookie": ""
    },
    {
      "username": "",
      "password": "",
      "cookie": ""
    }
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
  "congest": 120
}"""
    )
