import os
from typing import Optional
from .constants import *
import logging
from collections.abc import Callable
from .__typing import Config, QueryWordData

logger = logging.getLogger('dict2Anki.noteManager')
try:
    from aqt import mw
    from anki import notes, models
except ImportError:
    # from test.dummy_aqt import mw
    # from test.dummy_anki import notes, models
    pass


__TEMPLATE_NAME = 'default'


def getDeckNames():
    if not mw.col:
        raise RuntimeError
    return [deck['name'] for deck in mw.col.decks.all()]


def getWordsByDeck(deckName) -> list[str]:
    if not mw.col:
        raise RuntimeError
    noteIds = mw.col.find_notes(f'deck:"{deckName}"')
    words = []
    for nid in noteIds:
        note = mw.col.get_note(nid)
        model = note.note_type()
        if model and model.get('name', '').lower().startswith('dict2anki') and note['term']:
            words.append(note['term'])
    return words


def getNoteIds(wordList, deckName) -> list[notes.NoteId]:
    if not mw.col:
        raise RuntimeError
    noteIds = []
    for word in wordList:
        noteIds.extend(mw.col.find_notes(f'deck:"{deckName}" term:"{word}"'))
    return noteIds


def noteFilterByModelName(note: notes.Note):
    model = note.note_type()
    if model and model['name'] == MODEL_NAME:
        return True
    return False


def getNotesByDeckName(deckName: str, filter: Optional[Callable]=None) -> list[notes.Note]:
    if not mw.col:
        raise RuntimeError

    noteIds = mw.col.find_notes(f'deck:"{deckName}"')
    notes = []
    for noteId in noteIds:
        note = mw.col.get_note(noteId)
        if not filter:
            notes.append(note)
        elif filter(note):
            notes.append(note)
    return notes


def removeNotes(noteIds):
    if not mw.col:
        raise RuntimeError
    mw.col.remove_notes(noteIds)


def getOrCreateDeck(deckName, model):
    if not mw.col:
        raise RuntimeError
    deck_id = mw.col.decks.id(deckName)
    deck = mw.col.decks.get(deck_id)  # type: ignore
    mw.col.decks.select(deck['id'])  # type: ignore
    mw.col.decks.save(deck)
    model['did'] = deck['id']  # type: ignore
    mw.col.models.save(model)
    return deck


def getOrCreateModel() -> models.NoteType:
    if not mw.col:
        raise RuntimeError
    model = mw.col.models.by_name(MODEL_NAME)
    if model:
        if set([f['name'] for f in model['flds']]) == set(MODEL_FIELDS):
            return model
        else:
            logger.warning('模版字段异常，自动删除重建')
            mw.col.models.remove(model['id'])

    logger.info(f'创建新模版:{MODEL_NAME}')
    model = mw.col.models.new(MODEL_NAME)
    for field_name in MODEL_FIELDS:
        mw.col.models.add_field(model, mw.col.models.new_field(field_name))
    return model


def getOrCreateModelCardTemplate(modelObject: models.NoteType):
    if not mw.col:
        raise RuntimeError
    logger.info(f'添加卡片类型:{__TEMPLATE_NAME}')
    existingCardTemplate = modelObject['tmpls']
    if __TEMPLATE_NAME in [t.get('name') for t in existingCardTemplate]:
        return
    cardTemplate = mw.col.models.new_template(__TEMPLATE_NAME)
    cardTemplate['qfmt'] = '''
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
<div>Tap to View</div>
<hr>
短语：
<div>{{phraseFront}}</div>
<hr>
例句：
<div>{{sentenceFront}}</div>
    '''
    cardTemplate['afmt'] = '''
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
    '''
    modelObject['css'] = '''
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
    '''
    mw.col.models.addTemplate(modelObject, cardTemplate)
    mw.col.models.add(modelObject)


def addNoteToDeck(deckObject, modelObject, currentConfig: Config, oneQueryResult: QueryWordData):
    if not mw.col:
        raise RuntimeError
    modelObject['did'] = deckObject['id']

    newNote = mw.col.new_note(modelObject)
    newNote[F_TERM] = oneQueryResult[F_TERM]
    writeNoteFields(newNote, oneQueryResult, currentConfig,
                    [writeNoteDefinition, writeNotePhrase, writeNoteSentence, writeNoteImage, writeNotePron,
                     writeNoteAmEPhonetic, writeNoteBrEPhonetic])  # 写入所有字段
    mw.col.add_note(newNote, deckObject['id'])
    logger.info(f"添加笔记{newNote[F_TERM]}")


def writeNoteDefinition(note: notes.Note, queryData: QueryWordData, currentConfig: Config):
    if currentConfig[F_DEFINITION]:
        if queryData[F_DEFINITION]:
            note[F_DEFINITION] = '<br>'.join(queryData[F_DEFINITION])
    else:
        note[F_DEFINITION] = ''


def writeNotePhrase(note: notes.Note, queryData: QueryWordData, currentConfig: Config):
    if currentConfig[F_PHRASE]:
        if queryData[F_PHRASE]:
            note[f'{F_PHRASE}Front'] = '<br>'.join(
                [f'<i>{e.strip()}</i>' for e, _ in queryData[F_PHRASE]])
            note[f'{F_PHRASE}Back'] = '<br>'.join(
                [f'<i>{e.strip()}</i> {c.strip()}' for e, c in queryData[F_PHRASE]])
    else:
        note[f'{F_PHRASE}Front'] = ''
        note[f'{F_PHRASE}Back'] = ''


def writeNoteSentence(note: notes.Note, queryData: QueryWordData, currentConfig: Config):
    if currentConfig[F_SENTENCE]:
        if queryData[F_SENTENCE]:
            note[f'{F_SENTENCE}Front'] = ('<ol>'
                + '\n'.join([f'<li>{e.strip()}</li>' for e, _ in queryData[F_SENTENCE]])
                + '</ol>')
            note[f'{F_SENTENCE}Back'] = ('<ol>'
                + '\n'.join([f'<li>{e.strip()}<br>{c.strip()}</li>' for e, c in queryData[F_SENTENCE]])
                + '</ol>')
    else:
        note[f'{F_SENTENCE}Front'] = ''
        note[f'{F_SENTENCE}Back'] = ''


def writeNoteImage(note: notes.Note, queryData: QueryWordData, currentConfig: Config):
    if currentConfig[F_IMAGE]:
        if queryData[F_IMAGE]:
            note[F_IMAGE] = f'<img style="max-height:300px" src="{queryData[F_IMAGE]}">'
    else:
        note[F_IMAGE] = ''


def writeNotePron(note: notes.Note, queryData: QueryWordData, currentConfig: Config):
    if currentConfig[F_AMEPRON]:
        if queryData[F_AMEPRON]:
            note[F_AMEPRON] = f"[sound:{F_AMEPRON}_{queryData[F_TERM]}.mp3]"
    else:
        note[F_AMEPRON] = ''

    if currentConfig[F_BREPRON]:
        if queryData[F_BREPRON]:
            note[F_BREPRON] = f"[sound:{F_BREPRON}_{queryData[F_TERM]}.mp3]"
    else:
        note[F_BREPRON] = ''


def writeNoteAmEPhonetic(note: notes.Note, queryData: QueryWordData, currentConfig: Config):
    if currentConfig[F_AMEPHONETIC]:
        if queryData[F_AMEPHONETIC]:
            note[F_AMEPHONETIC] = queryData[F_AMEPHONETIC]
    else:
        note[F_AMEPHONETIC] = ''


def writeNoteBrEPhonetic(note: notes.Note, queryData: QueryWordData, currentConfig: Config):
    if currentConfig[F_BREPHONETIC]:
        if queryData[F_BREPHONETIC]:
            note[F_BREPHONETIC] = queryData[F_BREPHONETIC]
    else:
        note[F_BREPHONETIC] = ''


writeNoteFnType = Callable[[notes.Note, QueryWordData, Config], None]


def writeNoteFields(note: notes.Note, queryData: QueryWordData, currentConfig: Config,
                    modifyFieldFns: list[writeNoteFnType]):
    for fn in modifyFieldFns:
        fn(note, queryData, currentConfig)


def media_path(fileName: Optional[str]):
    '''如果有文件名，返回完整文件路径，否则返回媒体库dir'''
    if not mw.col:
        raise RuntimeError
    media_dir = mw.col.media.dir()
    if not fileName:
        return media_dir
    return os.path.join(media_dir, fileName)
