import pytest
from aqt import Qt
from pytest import MonkeyPatch as MP
from pytestqt.qtbot import QtBot

from addon import noteManager
from addon.template import DbModel, DiskModel, Model, Template

from . import mock_helper
from .helper import MockCallable


@pytest.fixture(autouse=True)
def setup(monkeypatch: MP):
    monkeypatch.setattr(noteManager, 'template_from_db', MockCallable(('front', 'back', 'css')))
    monkeypatch.setattr(noteManager, 'update_db_model_template', MockCallable())


@pytest.fixture
def db_model():
    yield DbModel(0)


@pytest.fixture
def disk_model():
    yield DiskModel(1, 'default', DbModel(0))


def _test_model_get(model: Model, part: str):
    """
    - test _cached should be False at init
    - test can get value
    - after first get, _cached should be True because data is loaded, should not
      trigger {part}_modified event, get_part_modified() should return False
    """
    # cached should be False at init
    assert model._cached is False

    callback_called = 0

    def on_part_modify(_model: Model):
        nonlocal callback_called
        callback_called += 1

    model.listen(f'{part}_modified', on_part_modify)

    ret = model.get_part(part)
    get_fn = getattr(model, f'get_{part}')

    assert ret != '' and ret == get_fn()
    assert model._cached is True
    # should not trigger modified event
    assert callback_called == 0
    assert model.get_part_modified(part) is False


def _test_db_model_set(db_model: DbModel, part: str):
    """
    - test can set value
    - after set same value, should not trigger {part}_modified event,
      get_part_modified() should return False
    - after set different value, should trigger {part}_modified event,
      get_part_modified() should return True
    """
    db_model._front = 'front'
    db_model._back = 'back'
    db_model._css = 'css'

    callback_called = 0

    def on_part_modify(_model: DbModel):
        nonlocal callback_called
        callback_called += 1

    db_model.listen(f'{part}_modified', on_part_modify)

    unmodified_val = part
    db_model.set_part(part, unmodified_val)

    assert db_model.get_part(part) == unmodified_val
    # set the same value should not trigger modified event
    assert callback_called == 0
    assert db_model.get_part_modified(part) is False

    modified_val = f'set_{part}'
    db_model.set_part(part, modified_val)

    assert db_model.get_part(part) == modified_val
    # set different value should trigger modified event
    assert callback_called == 1
    assert db_model.get_part_modified(part) is True


def test_db_model_get_front(db_model):
    _test_model_get(db_model, 'front')


def test_db_model_get_back(db_model):
    _test_model_get(db_model, 'back')


def test_db_model_get_css(db_model):
    _test_model_get(db_model, 'css')


def test_disk_model_get_front(disk_model):
    _test_model_get(disk_model, 'front')


def test_disk_model_get_back(disk_model):
    _test_model_get(disk_model, 'back')


def test_disk_model_get_css(disk_model):
    _test_model_get(disk_model, 'css')


def test_db_model_set_front(db_model):
    _test_db_model_set(db_model, 'front')


def test_db_model_set_back(db_model):
    _test_db_model_set(db_model, 'back')


def test_db_model_set_css(db_model):
    _test_db_model_set(db_model, 'css')


def test_db_model_save(db_model: DbModel):
    """
    - test before save, if all get_part_modified() return False, should not
      trigger any modified event, and modified state should not change
    - test before save, if any get_part_modified() return True, should only
      trigger those part's modified events, matching modified state should change
    """
    front_modify_called = 0

    def on_front_modify(_model):
        nonlocal front_modify_called
        front_modify_called += 1

    back_modify_called = 0

    def on_back_modify(_model):
        nonlocal back_modify_called
        back_modify_called += 1

    css_modify_called = 0

    def on_css_modify(_model):
        nonlocal css_modify_called
        css_modify_called += 1

    db_model.listen('front_modified', on_front_modify)
    db_model.listen('back_modified', on_back_modify)
    db_model.listen('css_modified', on_css_modify)

    # db_model is unmodified before save
    db_model.save()

    assert front_modify_called == 0
    assert db_model.get_part_modified('front') is False
    assert back_modify_called == 0
    assert db_model.get_part_modified('back') is False
    assert css_modify_called == 0
    assert db_model.get_part_modified('css') is False

    db_model.set_css('set css')
    # now css_modify_called == 1
    db_model.save()

    assert front_modify_called == 0
    assert db_model.get_part_modified('front') is False
    assert back_modify_called == 0
    assert db_model.get_part_modified('back') is False
    # css_modified event triggers twice
    assert css_modify_called == 2
    assert db_model.get_part_modified('css') is False


def test_template_save(qtbot: QtBot, monkeypatch: MP):
    """
    - test can save without change selected template
    - test can save when selecting default (disk) template
    - test can save when select back to db template
    """
    mock_helper.mock_aqt_utils(monkeypatch)  # mock save tooltip

    template = Template()
    qtbot.addWidget(template)
    default_model = template._tpl_id_model_map[1]
    assert isinstance(default_model, DiskModel)
    savebtn = template.saveButton
    default_tpl_btn = template.tplButtonGroup.button(1)
    assert default_tpl_btn is not None
    front, back, css = noteManager.template_from_folder(noteManager.templates_folder(), default_model.name())

    # test can save without change selection

    savebtn.click()

    assert noteManager.update_db_model_template.called == 1  # type: ignore
    assert noteManager.update_db_model_template.called_with == (noteManager.template_from_db(), {})  # type: ignore

    # test can save default template

    default_tpl_btn.click()
    savebtn.click()

    assert noteManager.update_db_model_template.called == 2  # type: ignore
    assert noteManager.update_db_model_template.called_with == ((front, back, css), {})  # type: ignore

    # test can save after switching back

    template.dbTplButton.click()
    template.cssButton.click()
    template.plainEditText.setPlainText('css')
    savebtn.click()

    assert noteManager.update_db_model_template.called == 3  # type: ignore
    assert noteManager.update_db_model_template.called_with == ((front, back, 'css'), {})  # type: ignore
