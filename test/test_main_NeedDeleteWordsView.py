from ..addon import addonWindow
from .mock_helper import w_mock
import pytest


@pytest.mark.parametrize("texts", [[], ["a", "b", "c"]])
def test_add_remove_items(qtbot, w_mock, texts):
    w: addonWindow.Windows = w_mock()
    qtbot.addWidget(w)

    w.needDeleteWordsView.add_items(texts)
    items = w.needDeleteWordsView.items()
    assert len(items) == len(texts)

    w.needDeleteWordsView.remove_items(items)
    assert w.needDeleteWordsView.empty()


def test_check_uncheck(qtbot, w_mock):
    texts = ["a", "b", "c"]
    w: addonWindow.Windows = w_mock()
    qtbot.addWidget(w)
    w.needDeleteWordsView.add_items(texts)
    w.needDeleteWordsView.check_if_not_empty()

    w.needDeleteCheckBox.setChecked(False)
    assert w.needDeleteWordsView.checked_items() == []

    w.needDeleteCheckBox.setChecked(True)
    assert len(w.needDeleteWordsView.checked_items()) == len(texts)


@pytest.mark.parametrize("texts", [[], ["a", "b", "c"]])
def test_item_texts(qtbot, w_mock, texts):
    w: addonWindow.Windows = w_mock()
    qtbot.addWidget(w)
    w.needDeleteWordsView.add_items(texts)

    assert w.needDeleteWordsView.item_texts(w.needDeleteWordsView.items()) == texts


def text_clear(qtbot, w_mock, texts):
    texts = ["a", "b", "c"]
    w: addonWindow.Windows = w_mock()
    qtbot.addWidget(w)
    w.needDeleteWordsView.add_items(texts)

    assert not w.needDeleteWordsView.empty()

    w.needDeleteWordsView.clear()

    assert w.needDeleteWordsView.empty()
