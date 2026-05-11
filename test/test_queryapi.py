import os
import logging
from ..addon.queryApi.eudict import API
from ..addon import constants as C
import pytest
logger = logging.getLogger(__name__)
api = API()

keys = (
    C.F_TERM,
    C.F_DEFINITION,
    C.F_PHRASE,
    C.F_IMAGE,
    C.F_SENTENCE,
    C.F_BREPHONETIC,
    C.F_AMEPHONETIC,
    C.F_BREPRON,
    C.F_AMEPRON,
)


@pytest.mark.skip
def get_missing_fileds_set(res):
    ret = []
    for key in keys:
        if not res.get(key):
            ret.append(key)
    return set(ret)


@pytest.mark.skip
def test_eudict_no_phrase_and_image():
    res = api.query('stint')
    ret = get_missing_fileds_set(res)
    expect = {C.F_IMAGE, C.F_PHRASE}
    assert ret == expect


@pytest.mark.skip
def test_eudict_with_all():
    res = api.query('flower')
    ret = get_missing_fileds_set(res)
    assert ret == set()


@pytest.mark.skip
def test_eudict_with_none():
    res = api.query('asafesdf')
    ret = get_missing_fileds_set(res)
    assert ret == set(keys) - {C.F_TERM} # type: ignore


@pytest.mark.skip
def test_eudict_implication():
    # 不包含图片，定义不在正常规则内，包含 trans
    res = api.query('implication')
    ret = get_missing_fileds_set(res)
    expect = {C.F_IMAGE}
    assert ret == expect


@pytest.mark.skip
def test_eudict_epitomize():
    # 不包含图片，定义不在正常规则内
    res = api.query('epitomize')
    ret = get_missing_fileds_set(res)
    expect = {C.F_IMAGE, C.F_PHRASE}
    assert ret == expect


@pytest.mark.skip
def test_eudict_periodical():
    # 包含图片，定义不在正常规则内
    res = api.query('periodical')
    ret = get_missing_fileds_set(res)
    assert ret == set()


@pytest.mark.skip
def test_eudict_divisional():
    # 又一种特殊情况，只有一个音标
    res = api.query('divisional')
    ret = get_missing_fileds_set(res)
    expect = {C.F_IMAGE}
    assert expect == ret


@pytest.mark.skip
@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", reason="Travis中查询结果没有image字段")
def test_eudict_image_url_without_https():
    res = api.query('gelatin')
    assert res['image'].startswith('https://') # type: ignore
