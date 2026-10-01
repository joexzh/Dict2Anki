from __future__ import annotations

import functools
import logging
import os
import typing as T
from pathlib import Path

import aqt
from anki import models, notes

from . import constants as C
from . import misc
from ._typing import QueryWordData

logger = logging.getLogger('dict2Anki.noteManager')

TEMPLATE_NAME = 'default'


def getDeckNames():
    assert aqt.mw.col
    return [deck['name'] for deck in aqt.mw.col.decks.all()]


def getWordsByDeck(deckName) -> list[str]:
    assert aqt.mw.col
    noteIds = aqt.mw.col.find_notes(f'deck:"{deckName}"')
    words = []
    for nid in noteIds:
        note = aqt.mw.col.get_note(nid)
        model = note.note_type()
        if model and model.get('name', '').lower().startswith('dict2anki') and note['term']:
            words.append(note['term'])
    return words


def get_note_ids(deckName: str, other_cond: T.Optional[str] = None):
    """Don't forget to escape `"` in `other_cond`.
    E.g., `other_cond = f'term:"{word} flag:1"'`, caller must escape
    double-quotes in `word`, replace `"` with `\\"`.
    """
    assert aqt.mw.col is not None

    if other_cond is None:
        other_cond = ''

    escaped_deckName = deckName.replace('"', '\\"')

    # ensure notes have the field "term"
    search_str = f'deck:"{escaped_deckName}" term:* {other_cond}'
    return aqt.mw.col.find_notes(search_str)


def getNoteIds(wordList: T.Iterable[str], deckName: str) -> list[notes.NoteId]:
    assert aqt.mw.col
    noteIds = []
    for word in wordList:
        escaped_word = word.replace('"', '\\"')
        noteIds.extend(get_note_ids(deckName, f'term:"{escaped_word}"'))
    return noteIds


def getNotesByDeckName(deckName: str, other_cond: T.Optional[str] = None):
    """Don't forget to escape `"` in `other_cond`.
    E.g., `other_cond = f'term:"{word}"'`, you must escape double-quotes in `word`.
    """
    assert aqt.mw.col is not None
    return (aqt.mw.col.get_note(nid) for nid in get_note_ids(deckName, other_cond))


def removeNotes(noteIds: T.Sequence[notes.NoteId]):
    assert aqt.mw.col
    aqt.mw.col.remove_notes(noteIds)


def updateNotes(notes: T.Sequence[notes.Note]):
    assert aqt.mw.col
    aqt.mw.col.update_notes(notes)


def getOrCreateDeck(deckName, model):
    assert aqt.mw.col
    deck_id = aqt.mw.col.decks.id(deckName)
    deck = aqt.mw.col.decks.get(deck_id)  # type: ignore
    aqt.mw.col.decks.select(deck['id'])  # type: ignore
    aqt.mw.col.decks.save(deck)
    model['did'] = deck['id']  # type: ignore
    aqt.mw.col.models.save(model)
    return deck


def getOrCreateModel() -> models.NoteType:
    assert aqt.mw.col
    model = aqt.mw.col.models.by_name(C.MODEL_NAME)
    if model:
        if set([f['name'] for f in model['flds']]) == set(C.MODEL_FIELDS):
            return model
        else:
            logger.warning('模版字段异常，自动删除重建')
            aqt.mw.col.models.remove(model['id'])

    logger.info(f'创建新模版:{C.MODEL_NAME}')
    model = aqt.mw.col.models.new(C.MODEL_NAME)
    for field_name in C.MODEL_FIELDS:
        aqt.mw.col.models.add_field(model, aqt.mw.col.models.new_field(field_name))
    return model


def getOrCreateModelCardTemplate(modelObject: models.NoteType):
    assert aqt.mw.col
    templates = modelObject['tmpls']
    for template in templates:
        if TEMPLATE_NAME == template.get('name'):
            return template

    logger.info(f'添加卡片类型:{TEMPLATE_NAME}')
    template = aqt.mw.col.models.new_template(TEMPLATE_NAME)
    front, back, css = template_from_folder(templates_folder(), TEMPLATE_NAME)
    template['qfmt'] = front
    template['afmt'] = back
    modelObject['css'] = css
    aqt.mw.col.models.addTemplate(modelObject, template)
    aqt.mw.col.models.add(modelObject)
    return template


def update_db_model_template(front: T.Optional[str], back: T.Optional[str], css: T.Optional[str]):
    assert aqt.mw.col

    model = getOrCreateModel()
    template = getOrCreateModelCardTemplate(model)
    if front is not None:
        template['qfmt'] = front
    if back is not None:
        template['afmt'] = back
    if css is not None:
        model['css'] = css
    aqt.mw.col.models.save(model)


def template_from_db() -> tuple[str, str, str]:
    model = getOrCreateModel()
    template = getOrCreateModelCardTemplate(model)
    return template['qfmt'], template['afmt'], model['css']  # type: ignore


def templates_folder() -> Path:
    "addon/templates"
    folder = Path(__file__).parent / 'templates'
    return folder


@functools.cache
def template_from_folder(folder: T.Union[Path, str], template_name: str) -> tuple[str, str, str]:
    """Get front, back, css content from {folder}/{tpl_name}/{front.html,back.html,css.css}

    Raises:
        FileNotFoundError
    """
    tpl_d = Path(folder) / template_name
    front_f = tpl_d / 'front.html'
    back_f = tpl_d / 'back.html'
    css_f = tpl_d / 'css.css'

    if not front_f.is_file():
        raise FileNotFoundError(f'{front_f} not exist')
    if not back_f.is_file():
        raise FileNotFoundError(f'{back_f} not exist')
    if not css_f.is_file():
        raise FileNotFoundError(f'{css_f} not exist')

    back = back_f.read_text(encoding='utf-8')
    front = front_f.read_text(encoding='utf-8')
    css = css_f.read_text(encoding='utf-8')

    return (front, back, css)


def new_note(word: str, model: T.Optional[models.NotetypeDict] = None):
    assert aqt.mw.col is not None

    if model is None:
        model = getOrCreateModel()
        getOrCreateModelCardTemplate(model)

    note = aqt.mw.col.new_note(model)
    note[C.F_TERM] = word
    return note


def create_sample_note(front: str, back: str, css: str):
    "create a sample note with term:'saber'"
    model = getOrCreateModel()
    template = getOrCreateModelCardTemplate(model)
    note = new_note('saber', model)
    template['qfmt'] = front
    template['afmt'] = back
    model['css'] = css
    api_data: QueryWordData = {
        'term': 'saber',
        'definition': [
            'n. 军刀；佩剑；骑兵',
            'vt. 用马刀砍或杀',
            'n. （Saber）人名；（法）萨贝；（阿拉伯）萨比尔',
            'n.a fencing sword with a v-shaped blade and a slightly curved handle',
            'v.cut or injure with a saber',
        ],
        'phrase': [
            ('Saber Marionette', '机械女神；机械女神J；机械女神R'),
            ('Saber-toothed cat', '剑齿虎'),
            ('Saber Dance', '剑舞；军刀舞曲；马刀舞曲；马刀舞'),
            ('Saber saws', '小刀锯'),
            ('Beat Saber', '节奏光剑；节奏空间'),
            ('beam saber', '光束剑；光剑；雷射剑'),
            ('royal saber', '皇家救星；皇家圣枪；皇家枪击；皇家之剑'),
            ('saber-toothed tiger', '剑齿虎'),
        ],
        'image': 'https://ydlunacommon.nosdn.127.net/55f362d2a08ab991487661dead0c1514.png?',
        'sentence': [
            ('We dig up in France and there is the saber, right?', '我们在法国进行挖掘，然后就发现了那把军刀，是吧？'),
            (
                'Smilodon is an extinct genus of machairodont felid. It is perhaps one of the most famous prehistoric mammals and the best known saber-toothed cat.',
                '剑齿虎，是已经灭绝的剑形齿类动物的一种，这也许是史前哺乳动物中最出名的一种了，也是最有名的剑齿类猫科动物。',
            ),
            (
                'I remember playing as a lad in France burying my little toy saber.',
                '我记得年轻时在法国埋了我的玩具剑。',
            ),
        ],
        'BrEPhonetic': 'ˈseɪbə(r)',
        'AmEPhonetic': 'ˈseɪbər',
        'BrEPron': 'http://dict.youdao.com/dictvoice?audio=saber&type=1',
        'AmEPron': 'http://dict.youdao.com/dictvoice?audio=saber&type=2',
    }
    set_field_definition(note, api_data)
    set_field_phrase(note, api_data)
    set_field_sentence(note, api_data)
    set_field_image(note, api_data)
    set_field_BrEPhonetic(note, api_data)
    set_field_AmEPhonetic(note, api_data)
    set_field_BrEPron(note, api_data)
    set_field_AmEPron(note, api_data)
    return note


def set_flag(notes: T.Iterable[notes.Note], flag: int):
    """set flag for cards of notes"""
    assert aqt.mw.col is not None
    for note in notes:
        card_ids = note.card_ids()
        aqt.mw.col.set_user_flag_for_cards(flag, card_ids)


def to_field_definition(api_definition: list[str]) -> str:
    return ''.join((f'<div class="definition">{definition.strip()}</div>' for definition in api_definition))


def set_field_definition(note: notes.Note, query_data: QueryWordData) -> bool:
    if api_definition := query_data[C.F_DEFINITION]:
        note[C.F_DEFINITION] = to_field_definition(api_definition)
        return True
    return False


def empty_field_definition(note: notes.Note):
    note[C.F_DEFINITION] = ''


def to_field_phrase(api_phrase: list[tuple[str, str]]) -> tuple[str, str]:
    return (
        ''.join([f'<div class="phrase-front">{front.strip()}</div>' for front, _ in api_phrase]),
        ''.join(
            [
                f'<div><span class="phrase-front">{front.strip()}</span> <span class="phrase-back">{back.strip()}</span></div>'
                for front, back in api_phrase
            ]
        ),
    )


def set_field_phrase(note: notes.Note, query_data: QueryWordData) -> bool:
    if api_data_phrase := query_data[C.F_PHRASE]:
        field_tuple = to_field_phrase(api_data_phrase)
        note[C.F_PHRASE_FRONT] = field_tuple[0]
        note[C.F_PHRASE_BACK] = field_tuple[1]
        return True
    return False


def empty_field_phrase(note: notes.Note):
    clear_field(note, C.F_PHRASE_FRONT)
    clear_field(note, C.F_PHRASE_BACK)


def to_field_sentence(api_sentence: list[tuple[str, str]]) -> tuple[str, str]:
    field_front = ''
    field_back = ''
    s_front_backs = [(front.strip(), back.strip()) for front, back in api_sentence if front.strip() or back.strip()]

    if s_fronts := [front for front, _ in s_front_backs if front]:
        field_front = ''.join((f'<div class="sentence-front">{front}</div>' for front in s_fronts))

    if s_front_backs:
        chunks = []
        for front, back in s_front_backs:
            if front:
                chunks.append(f'<div class="sentence-front">{front}</div>')
            if back:
                chunks.append(f'<div class="sentence-back">{back}</div>')
        field_back = ''.join(chunks)

    return (field_front, field_back)


def set_field_sentence(note: notes.Note, query_data: QueryWordData) -> bool:
    if api_sentence := query_data[C.F_SENTENCE]:
        field_tuple = to_field_sentence(api_sentence)
        note[C.F_SENTENCE_FRONT] = field_tuple[0]
        note[C.F_SENTENCE_BACK] = field_tuple[1]
        return True
    return False


def empty_field_sentence(note: notes.Note):
    clear_field(note, C.F_SENTENCE_FRONT)
    clear_field(note, C.F_SENTENCE_BACK)


def to_field_image(api_image: str) -> str:
    return f'<img class="image" src="{api_image}">'


def set_field_image(note: notes.Note, query_data: QueryWordData) -> bool:
    if api_image := query_data[C.F_IMAGE]:
        note[C.F_IMAGE] = to_field_image(api_image)
        return True
    return False


def empty_field_image(note: notes.Note):
    clear_field(note, C.F_IMAGE)


def set_field_BrEPron(note: notes.Note, query_data: QueryWordData) -> bool:
    if query_data[C.F_BREPRON]:
        note[C.F_BREPRON] = make_pron_field(C.F_BREPRON, query_data[C.F_TERM])
        return True
    return False


def empty_field_BrEPron(note: notes.Note):
    clear_field(note, C.F_BREPRON)


def set_field_AmEPron(note: notes.Note, query_data: QueryWordData) -> bool:
    if query_data[C.F_AMEPRON]:
        note[C.F_AMEPRON] = make_pron_field(C.F_AMEPRON, query_data[C.F_TERM])
        return True
    return False


def empty_field_AmEPron(note: notes.Note):
    clear_field(note, C.F_AMEPRON)


def set_field_AmEPhonetic(note: notes.Note, query_data: QueryWordData) -> bool:
    if query_data[C.F_AMEPHONETIC]:
        note[C.F_AMEPHONETIC] = query_data[C.F_AMEPHONETIC]
        return True
    return False


def empty_field_AmEPhonetic(note: notes.Note):
    clear_field(note, C.F_AMEPHONETIC)


def set_field_BrEPhonetic(note: notes.Note, query_data: QueryWordData) -> bool:
    if query_data[C.F_BREPHONETIC]:
        note[C.F_BREPHONETIC] = query_data[C.F_BREPHONETIC]
        return True
    return False


def empty_field_BrEPhonetic(note: notes.Note):
    clear_field(note, C.F_BREPHONETIC)


def set_field(note: notes.Note, field: str, query_data: QueryWordData) -> bool:
    set_field_fn = globals().get(f'set_field_{field}')
    if set_field_fn is None:
        raise AttributeError(f'set_field: missing function set_field_{field}')
    return set_field_fn(note, query_data)


def empty_field(note: notes.Note, field: str):
    empty_field_fn = globals().get(f'empty_field_{field}')
    if empty_field_fn is None:
        raise AttributeError(f'empty_field: missing function empty_field_{field}')
    empty_field_fn(note)


def media_path(fileName: T.Optional[str] = None):
    """如果有文件名，返回完整文件路径，否则返回媒体库dir"""
    assert aqt.mw.col
    media_dir = aqt.mw.col.media.dir()
    if not fileName:
        return media_dir
    return os.path.join(media_dir, fileName)


def make_pron_field(prefix: str, term: str):
    return f'[sound:{misc.audio_fname(prefix, term)}]'


def clear_field(note: notes.Note, field_name: str):
    note[field_name] = ''
