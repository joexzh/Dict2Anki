from __future__ import annotations

import json
import logging
import typing as T

import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from ..... import global_vars as V

logger = logging.getLogger('dict2Anki.queryApi.webapi.vcom')
__all__ = ['fetch_parse']


class DefInstance(T.TypedDict):
    words: list[str]
    definition: str


# `type of` contains space, so must use this form to define `Definition`
Definition = T.TypedDict(
    'Definition',
    {
        'pos': str,  # part of speech
        'pos_color': str,
        'definition': str,
        'group': int,  # maybe useful to group definitions
        'example': list[str],  # strs with html tag
        'synonyms': list[DefInstance],
        'antonyms': list[DefInstance],
        'examples': list[DefInstance],
        'types': list[DefInstance],
        'type of': list[DefInstance],
    },
)


class WordFamily(T.TypedDict):
    word: str
    # you will encounter this word once every `freq` pages.
    freq: int
    parent: str


class Sentence(T.TypedDict):
    # a pair of ints indicate the word location in sentence
    offsets: tuple[int, int]
    sentence: str
    author: str
    title: str
    # timestamp in milliseconds
    date: int


class VCOMWord(T.TypedDict):
    word: str
    phonetics_us: str
    phonetics_uk: str
    pron_audio_us: str
    pron_audio_uk: str
    funny_def_short: str
    funny_def_long: str
    definitions: list[Definition]
    word_family: list[WordFamily]
    sentences: list[Sentence]


def make_empty_definition() -> Definition:
    return {
        'pos': '',
        'pos_color': '',
        'definition': '',
        'group': 0,
        'example': [],
        'synonyms': [],
        'antonyms': [],
        'examples': [],
        'types': [],
        'type of': [],
    }


def make_empty_vcomword(word: str) -> VCOMWord:
    return VCOMWord(
        word=word,
        phonetics_us='',
        phonetics_uk='',
        pron_audio_us='',
        pron_audio_uk='',
        funny_def_short='',
        funny_def_long='',
        definitions=[],
        word_family=[],
        sentences=[],
    )


def make_session():
    headers = {'User-Agent': V.user_agent()}
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers.update(headers)
    return session


session = make_session()
_pos_map = {
    'pos_n': {'name': 'n', 'color': '#0FA646'},
    'pos_v': {'name': 'v', 'color': '#CD4D03'},
    'pos_a': {'name': 'adj', 'color': '#007BC4'},
    'pos_r': {'name': 'adv', 'color': '#7B61FF'},
    'pos_pron': {'name': 'pron', 'color': '#44AA02'},
    'pos_prep': {'name': 'prep', 'color': '#BE6DCF'},
    'pos_conj': {'name': 'conj', 'color': '#CF8300'},
    'pos_interj': {'name': 'interj', 'color': '#FA52B7'},
    'pos_art': {'name': 'art', 'color': '#ED5362'},
    'pos_idm': {'name': 'idm', 'color': '#00A886'},
    'pos_abbr': {'name': 'abbr', 'color': '#EB7302'},
}


def parse_word_area(soup: BeautifulSoup, ret: VCOMWord):
    audio_url = 'https://audio.vocabulary.com/1.0/us/{}.mp3'

    word_area_tag = soup.find(class_='word-area')
    if word_area_tag is None:
        raise LookupError('can not find word_area')

    ipa_tags = word_area_tag.select('.ipa-section .ipa-with-audio')

    for ipa_tag in ipa_tags:
        if ipa_tag.find(class_='us-flag-icon'):
            phonetic_field = 'phonetics_us'

            if audio_tag := ipa_tag.select_one('.audio[data-audio]'):
                # `pron_audio_us`
                ret['pron_audio_us'] = audio_url.format(audio_tag['data-audio'])

        elif ipa_tag.find(class_='uk-flag-icon'):
            phonetic_field = 'phonetics_uk'

            if audio_tag := ipa_tag.find('audio', class_='pron-audio'):
                # `pron_audio_uk`
                ret['pron_audio_uk'] = audio_tag.get('src', '')
        else:
            continue

        if phonetic_tag := ipa_tag.find(class_='span-replace-h3'):
            # `phonetic_us` / `phonetic_uk`
            ret[phonetic_field] = phonetic_tag.get_text(strip=True)

    if short_tag := word_area_tag.find(class_='short'):
        # `funny_def_short`
        ret['funny_def_short'] = short_tag.decode_contents()

    if long_tag := word_area_tag.find(class_='long'):
        # `funny_def_long`
        ret['funny_def_long'] = long_tag.decode_contents()


def parse_def_instance(ins_tag: Tag) -> list[DefInstance]:
    ret: list[DefInstance] = []

    if dd_tags := ins_tag.select(':scope > .div-replace-dd '):
        # for `types` special case: if expandable, skip the first 2 elements,
        if len(dd_tags) > 0 and 'more' in dd_tags[0].get('class', []):
            dd_tags = dd_tags[2:]

        for dd_tag in dd_tags:
            def_tag = dd_tag.find(class_='definition')
            ret.append(
                {
                    'words': [word_tag.get_text(strip=True) for word_tag in dd_tag.find_all('a', class_='word')],
                    'definition': def_tag.get_text(strip=True) if def_tag else '',
                }
            )

    else:
        # for `synonyms` special case: no class div-replace-dd,
        ret.append(
            {
                'words': [word_tag.get_text(strip=True) for word_tag in ins_tag.find_all('a', class_='word')],
                'definition': '',
            }
        )

    return ret


def parse_def(soup: BeautifulSoup) -> list[Definition]:
    ret_defs = []
    def_li_tags = soup.select('.word-definitions > ol > li')
    group = 0

    for li_tag in def_li_tags:
        ret_def = make_empty_definition()

        li_classes: list[str] = li_tag.get('class', [])
        pos_cls = next(filter(lambda c: c.startswith('pos_'), li_classes), None)

        if 'ord1' in li_classes and 'sord1' in li_classes:
            # beginning of a new group
            group += 1
        ret_def['group'] = group

        if def_tag := li_tag.find(class_='definition'):
            if def_tag.find(class_='pos-icon') and pos_cls:
                # `pos`
                ret_def['pos'] = _pos_map[pos_cls]['name']
                # `pos_color`
                ret_def['pos_color'] = _pos_map[pos_cls]['color']

            # `definition`
            ret_def['definition'] = next(
                (str(child).strip() for child in def_tag.children if isinstance(child, NavigableString)), ''
            )

        if defContent_tag := li_tag.find(class_='defContent'):
            # `example`, strip the first and last `“` and `”`
            ret_def['example'] = [
                example_tag.decode_contents()[1:-1] for example_tag in defContent_tag.select(':scope > .example')
            ]

            for ins_tag in defContent_tag.select(':scope > .instances'):
                # `synonyms`, may have multiple ins_tags, concat them
                ret_def['synonyms'] += parse_def_instance(ins_tag)

            for ins_tag in defContent_tag.select(':scope > .more-info-section > .more-info > .instances'):
                if (
                    (detail_tag := ins_tag.find(class_='detail'))
                    and (detail_colon := detail_tag.get_text(strip=True))
                    and (detail := detail_colon[:-1])
                ):
                    # `antonyms / examples / types / type of`
                    ret_def[detail] = parse_def_instance(ins_tag)

        ret_defs.append(ret_def)

    return ret_defs


def parse_word_family(soup: BeautifulSoup) -> list[WordFamily]:
    ret: list[WordFamily] = []

    if (wf_tag := soup.find('vcom:wordfamily')) and (wf_data := wf_tag.get('data', '[]')):
        wf_arr = json.loads(wf_data)

        for wf_obj in wf_arr:
            word: str = wf_obj['word']
            ffreq: int = wf_obj['ffreq']
            freq = 1 + int((1 / (ffreq / 4000)))  # see [[README.md###calculate freq]]
            parent = wf_obj.get('parent', '')
            ret.append({'word': word, 'freq': freq, 'parent': parent})

    return ret


def parse_page(html: str, vcom_word: VCOMWord):
    soup = BeautifulSoup(html, 'html.parser')
    parse_word_area(soup, vcom_word)
    vcom_word['definitions'] = parse_def(soup)
    vcom_word['word_family'] = parse_word_family(soup)


def parse_sentences(json_obj: dict[str, T.Any]) -> list[Sentence]:
    ret = []
    if arr := json_obj.get('sentences'):
        # take the first 4 item of arr
        for item in arr[:4]:
            s = Sentence(sentence='', offsets=(0, 0), author='', title='', date=0)
            s['offsets'] = tuple(item['offsets'])
            s['sentence'] = item['sentence']
            item_vol = item['volume']
            s['author'] = item_vol['author']
            s['title'] = item_vol['title']
            s['date'] = item_vol['datePublished']

            ret.append(s)
    return ret


def fetch_parse_sentences(word: str) -> list[Sentence]:
    url = f'https://corpus.vocabulary.com/api/1.0/examples/random.json?maxResults=4&query={word}&startOffset=0'
    r = session.get(url, timeout=10)
    r.raise_for_status()
    return parse_sentences(r.json())


def fetch_parse(word: str) -> VCOMWord:
    url = f'https://www.vocabulary.com/dictionary/{word}'
    r = session.get(url, timeout=10)
    r.raise_for_status()

    vcom_word = make_empty_vcomword(word)
    parse_page(r.text, vcom_word)
    try:
        vcom_word['sentences'] = fetch_parse_sentences(word)
    except Exception as e:
        logger.exception(e)
    return vcom_word
