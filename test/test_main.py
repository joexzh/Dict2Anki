import copy

import aqt
import aqt.utils
import pytest
import requests
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from ..addon import dictionary
from ..addon.addonWindow import Windows, noteManager
from ..addon.constants import *
from .mock_helper import w_mock


def test_start_up_with_fresh_config(qtbot, w_mock):
    w: Windows = w_mock()
    qtbot.addWidget(w)

    assert w.conf.no_pron == False
    assert ADDON_FULL_NAME in w.windowTitle()
    assert aqt.mw.addonManager.getConfig.called > 0
    assert w.usernameLineEdit.text() == w.passwordLineEdit.text() == w.cookieLineEdit.text() == ''

def test_version_check(qtbot, monkeypatch, w_mock):
    new_tag = "v99999.0.0"
    monkeypatch.setitem(requests.get("").json.return_value, "tag_name", new_tag)

    w = w_mock()
    qtbot.addWidget(w)

    def check_askUser():
        assert aqt.utils.askUser.called_with == ((
            f"有新版本:{new_tag.strip()}是否更新？\n\n{requests.get('').json.return_value['body'].strip()}",), {})

    qtbot.waitUntil(check_askUser)
    assert requests.get("").json.called > 0


@pytest.mark.parametrize('index', [0, 1])
def test_dictionary_combobox_change(index, monkeypatch, w_mock, qtbot):
    monkeypatch.setitem(aqt.mw.addonManager.getConfig.return_value, "credential", [
        {'username': '0', 'password': '0', 'cookie': '0'},
        {'username': '1', 'password': '1', 'cookie': '1'}])

    w: Windows = w_mock()
    qtbot.addWidget(w)
    w.dictionaryComboBox.setCurrentIndex(index)

    assert w.conf.selected_dict == index
    assert w.dictionaryComboBox.currentText() in w.currentDictionaryLabel.text()
    assert w.conf.current_cookies == aqt.mw.addonManager.getConfig.return_value['credential'][index]["cookie"]
    assert w.cookieLineEdit.text() == w.conf.current_cookies


def test_get_deck_list(qtbot, monkeypatch, w_mock):
    monkeypatch.setitem(aqt.mw.addonManager.getConfig.return_value, "deck", "b")
    monkeypatch.setattr(noteManager, "getDeckNames", lambda: ["a", "b", "c"])

    w: Windows = w_mock()
    qtbot.addWidget(w)

    assert [w.deckComboBox.itemText(row) for row in range(w.deckComboBox.count())] == ['a', 'b', 'c']
    assert w.deckComboBox.currentText() == 'b'
    assert w.conf.deck == "b"


@pytest.mark.parametrize('local_words,remote_words,test_index', [
    ([], [], 0),
    ([], ['a', 'b'], 1),
    (['a'], ['a'], 2),
    (['a'], ['a', 'b'], 3),
    (['a', 'b'], ['c', 'd'], 4),
    (['a', 'b'], ['c', 'b'], 5),
])
def test_fetch_word_and_compare(monkeypatch, w_mock, qtbot, local_words, remote_words, test_index):
    monkeypatch.setattr(noteManager, "getWordsByDeck", lambda x: copy.deepcopy(local_words))
    monkeypatch.setattr(dictionary.eudict.Eudict, "getTotalPage", lambda x, y: 1)
    monkeypatch.setattr(dictionary.eudict.Eudict, "getWordsByPage", lambda x,y,z: copy.deepcopy(remote_words))

    w: Windows = w_mock()
    qtbot.addWidget(w)

    w.conf.selected_dict = dictionary.dictionaries.index(dictionary.eudict.Eudict)
    # value of w.conf is from monkeypatch, also need monkeypatch to modify it
    monkeypatch.setattr(w.conf, "current_selected_groups", ["group_1"]) # "group_1" is dummy value
    w.get_current_dict().groups = [(w.conf.current_selected_groups[0], "1")] # "1" is dummy value
    w.getRemoteWordList(w.conf.current_selected_groups)

    def check_tooltip():
        assert aqt.utils.tooltip.called

    qtbot.waitUntil(check_tooltip)

    item_in_list_widget = [w.newWordListWidget.item(row) for row in range(w.newWordListWidget.count())]
    item_in_del_widget = [w.needDeleteWordListWidget.item(row) for row in
                        range(w.needDeleteWordListWidget.count())]
    words_in_list_widget = [i.text() for i in item_in_list_widget]  # type: ignore
    words_in_del_widget = [i.text() for i in item_in_del_widget]  # type: ignore

    assert all([item.data(Qt.ItemDataRole.UserRole) is None for item in item_in_list_widget])  # type: ignore
    if test_index == 0:
        assert item_in_list_widget == []
        assert item_in_del_widget == []
        assert aqt.utils.tooltip.called_with == (('无需同步',), {})
    elif test_index == 1:
        assert sorted(words_in_list_widget) == sorted(remote_words)
        assert item_in_del_widget == []
    elif test_index == 2:
        assert item_in_list_widget == []
        assert item_in_del_widget == []
        assert aqt.utils.tooltip.called_with == (('无需同步',), {})
    elif test_index == 3:
        assert words_in_list_widget == ['b']
        assert item_in_del_widget == []
    elif test_index == 4:
        assert sorted(words_in_list_widget) == sorted(remote_words)
        assert sorted(words_in_del_widget) == sorted(local_words)
    elif test_index == 5:
        assert words_in_list_widget == ['c']
        assert words_in_del_widget == ['a']
