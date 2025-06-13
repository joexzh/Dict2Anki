import logging
import os
from collections.abc import Callable
from typing import Optional

import aqt
from anki import models, notes

from . import conf_model, misc
from ._typing import QueryWordData
from .constants import *

logger = logging.getLogger("dict2Anki.noteManager")

__TEMPLATE_NAME = "default"


def getDeckNames():
    assert aqt.mw.col
    return [deck["name"] for deck in aqt.mw.col.decks.all()]


def getWordsByDeck(deckName) -> list[str]:
    assert aqt.mw.col
    noteIds = aqt.mw.col.find_notes(f'deck:"{deckName}"')
    words = []
    for nid in noteIds:
        note = aqt.mw.col.get_note(nid)
        model = note.note_type()
        if (
            model
            and model.get("name", "").lower().startswith("dict2anki")
            and note["term"]
        ):
            words.append(note["term"])
    return words


def getNoteIds(wordList, deckName) -> list[notes.NoteId]:
    assert aqt.mw.col
    noteIds = []
    for word in wordList:
        noteIds.extend(aqt.mw.col.find_notes(f'deck:"{deckName}" term:"{word}"'))
    return noteIds


def noteFilterByModelName(note: notes.Note):
    model = note.note_type()
    if model and model["name"] == MODEL_NAME:
        return True
    return False


def getNotesByDeckName(
    deckName: str, filter: Optional[Callable] = None
) -> list[notes.Note]:
    assert aqt.mw.col

    noteIds = aqt.mw.col.find_notes(f'deck:"{deckName}"')
    notes = []
    for noteId in noteIds:
        note = aqt.mw.col.get_note(noteId)
        if not filter:
            notes.append(note)
        elif filter(note):
            notes.append(note)
    return notes


def removeNotes(noteIds):
    assert aqt.mw.col
    aqt.mw.col.remove_notes(noteIds)


def updateNotes(notes):
    assert aqt.mw.col
    aqt.mw.col.update_notes(notes)


def getOrCreateDeck(deckName, model):
    assert aqt.mw.col
    deck_id = aqt.mw.col.decks.id(deckName)
    deck = aqt.mw.col.decks.get(deck_id)  # type: ignore
    aqt.mw.col.decks.select(deck["id"])  # type: ignore
    aqt.mw.col.decks.save(deck)
    model["did"] = deck["id"]  # type: ignore
    aqt.mw.col.models.save(model)
    return deck


def getOrCreateModel() -> models.NoteType:
    assert aqt.mw.col
    model = aqt.mw.col.models.by_name(MODEL_NAME)
    if model:
        if set([f["name"] for f in model["flds"]]) == set(MODEL_FIELDS):
            return model
        else:
            logger.warning("模版字段异常，自动删除重建")
            aqt.mw.col.models.remove(model["id"])

    logger.info(f"创建新模版:{MODEL_NAME}")
    model = aqt.mw.col.models.new(MODEL_NAME)
    for field_name in MODEL_FIELDS:
        aqt.mw.col.models.add_field(model, aqt.mw.col.models.new_field(field_name))
    return model


def getOrCreateModelCardTemplate(modelObject: models.NoteType):
    assert aqt.mw.col
    logger.info(f"添加卡片类型:{__TEMPLATE_NAME}")
    existingCardTemplate = modelObject["tmpls"]
    if __TEMPLATE_NAME in [t.get("name") for t in existingCardTemplate]:
        return
    cardTemplate = aqt.mw.col.models.new_template(__TEMPLATE_NAME)
    cardTemplate[
        "qfmt"
    ] = """
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
    """
    cardTemplate[
        "afmt"
    ] = """
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
    modelObject[
        "css"
    ] = """
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


def addNoteToDeck(deckObject, modelObject, conf: conf_model.Conf, oneQueryResult: QueryWordData):
    assert aqt.mw.col
    modelObject["did"] = deckObject["id"]

    newNote = aqt.mw.col.new_note(modelObject)
    newNote[F_TERM] = oneQueryResult[F_TERM]
    writeNoteFields(
        newNote,
        oneQueryResult,
        conf,
        [
            writeNoteDefinition,
            writeNotePhrase,
            writeNoteSentence,
            writeNoteImage,
            writeNotePron,
            writeNoteAmEPhonetic,
            writeNoteBrEPhonetic,
        ],
    )  # 写入所有字段
    aqt.mw.col.add_note(newNote, deckObject["id"])
    logger.info(f"添加笔记{newNote[F_TERM]}")


def writeNoteDefinition(
    note: notes.Note, queryData: Optional[QueryWordData], conf: conf_model.Conf
):
    if conf.definition:
        if queryData and queryData[F_DEFINITION]:
            note[F_DEFINITION] = "<br>".join(queryData[F_DEFINITION])
    else:
        note[F_DEFINITION] = ""


def writeNotePhrase(note: notes.Note, queryData: Optional[QueryWordData], conf: conf_model.Conf):
    if conf.phrase:
        if queryData and queryData[F_PHRASE]:
            note[f"{F_PHRASE}Front"] = "<br>".join(
                [f"<i>{e.strip()}</i>" for e, _ in queryData[F_PHRASE]]
            )
            note[f"{F_PHRASE}Back"] = "<br>".join(
                [f"<i>{e.strip()}</i> {c.strip()}" for e, c in queryData[F_PHRASE]]
            )
    else:
        clear_field(note, f"{F_PHRASE}Front")
        clear_field(note, f"{F_PHRASE}Back")


def writeNoteSentence(note: notes.Note, queryData: Optional[QueryWordData], conf: conf_model.Conf):
    if conf.sentence:
        if queryData and queryData[F_SENTENCE]:
            note[f"{F_SENTENCE}Front"] = (
                "<ol>"
                + "\n".join([f"<li>{e.strip()}</li>" for e, _ in queryData[F_SENTENCE]])
                + "</ol>"
            )
            note[f"{F_SENTENCE}Back"] = (
                "<ol>"
                + "\n".join(
                    [
                        f"<li>{e.strip()}<br>{c.strip()}</li>"
                        for e, c in queryData[F_SENTENCE]
                    ]
                )
                + "</ol>"
            )
    else:
        clear_field(note, f"{F_SENTENCE}Front")
        clear_field(note, f"{F_SENTENCE}Back")


def writeNoteImage(note: notes.Note, queryData: Optional[QueryWordData], conf: conf_model.Conf):
    if conf.image:
        if queryData and queryData[F_IMAGE]:
            note[F_IMAGE] = f'<img style="max-height:300px" src="{queryData[F_IMAGE]}">'
    else:
        clear_field(note, F_IMAGE)


def writeNotePron(note: notes.Note, queryData: Optional[QueryWordData], conf: conf_model.Conf):
    if conf.ame_pron:
        if queryData and queryData[F_AMEPRON]:
            note[F_AMEPRON] = make_pron_field(F_AMEPRON, queryData[F_TERM])
    else:
        clear_field(note, F_AMEPRON)

    if conf.bre_pron:
        if queryData and queryData[F_BREPRON]:
            note[F_BREPRON] = make_pron_field(F_BREPRON, queryData[F_TERM])
    else:
        clear_field(note, F_BREPRON)


def writeNoteAmEPhonetic(
    note: notes.Note, queryData: Optional[QueryWordData], conf: conf_model.Conf
):
    if conf.ame_phonetic:
        if queryData and queryData[F_AMEPHONETIC]:
            note[F_AMEPHONETIC] = queryData[F_AMEPHONETIC]
    else:
        clear_field(note, F_AMEPHONETIC)


def writeNoteBrEPhonetic(
    note: notes.Note, queryData: Optional[QueryWordData], conf: conf_model.Conf
):
    if conf.bre_phonetic:
        if queryData and queryData[F_BREPHONETIC]:
            note[F_BREPHONETIC] = queryData[F_BREPHONETIC]
    else:
        clear_field(note, F_BREPHONETIC)


writeNoteFnType = Callable[[notes.Note, Optional[QueryWordData], conf_model.Conf], None]


def writeNoteFields(
    note: notes.Note,
    queryData: Optional[QueryWordData],
    conf: conf_model.Conf,
    modifyFieldFns: list[writeNoteFnType],
):
    for fn in modifyFieldFns:
        fn(note, queryData, conf)


def media_path(fileName: Optional[str]):
    """如果有文件名，返回完整文件路径，否则返回媒体库dir"""
    assert aqt.mw.col
    media_dir = aqt.mw.col.media.dir()
    if not fileName:
        return media_dir
    return os.path.join(media_dir, fileName)


def make_pron_field(prefix: str, term: str):
    return f"[sound:{misc.audio_fname(prefix, term)}]"


def clear_field(note: notes.Note, field_name: str):
    note[field_name] = ""
