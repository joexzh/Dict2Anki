from __future__ import annotations

import logging
import os
import typing as T

import aqt
from anki import models, notes

from . import constants as C
from . import misc
from ._typing import QueryWordData

logger = logging.getLogger('dict2Anki.noteManager')

__TEMPLATE_NAME = 'default'


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
    logger.info(f'添加卡片类型:{__TEMPLATE_NAME}')
    existingCardTemplate = modelObject['tmpls']
    if __TEMPLATE_NAME in [t.get('name') for t in existingCardTemplate]:
        return
    cardTemplate = aqt.mw.col.models.new_template(__TEMPLATE_NAME)
    cardTemplate['qfmt'] = """<table>
    <tr>
        <td>
            <h1 class="term">{{term}}</h1>
            <div>英[{{BrEPhonetic}}] 美[{{AmEPhonetic}}]{{BrEPron}}{{AmEPron}}</div>
        </td>
        <td>{{image}}</td>
    </tr>
</table>
<hr>
释义：
<div>Tap to View</div>
<hr>
短语：
<div>{{phraseFront}}</div>
<hr>
例句：
<div>{{sentenceFront}}</div>
    """
    cardTemplate['afmt'] = """
<table>
    <tr>
        <td>
            <h1 class="term">{{term}}</h1>
            <div>英[{{BrEPhonetic}}] 美[{{AmEPhonetic}}]{{BrEPron}}{{AmEPron}}</div>
        </td>
        <td>{{image}}</td>
    </tr>
</table>
<hr>
释义：
<div>{{definition}}</div>
<hr>
短语：
<div>{{phraseBack}}</div>
<hr>
例句：
<div>{{sentenceBack}}</div>
    """
    modelObject['css'] = """
.card {
    font-family: 'Noto Sans', arial, sans-serif;
    font-size: 20px;
    text-align: left;
    color: black;
    background-color: white;
}
.term {
    font-size : 35px;
}
    """
    aqt.mw.col.models.addTemplate(modelObject, cardTemplate)
    aqt.mw.col.models.add(modelObject)


def new_note(word: str, model: T.Optional[models.NotetypeDict] = None):
    assert aqt.mw.col is not None

    if model is None:
        model = getOrCreateModel()
        getOrCreateModelCardTemplate(model)

    note = aqt.mw.col.new_note(model)
    note[C.F_TERM] = word
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
        field_front = (
            ''.join((f'<div class="sentence-front">{front}</div>' for front in s_fronts))
        )

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
