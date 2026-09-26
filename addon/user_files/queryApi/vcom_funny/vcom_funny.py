import datetime
import logging
from typing import Optional

from .... import _typing as _T
from .webapi.vcom import VCOMWord, fetch_parse, session

logger = logging.getLogger('dict2Anki.queryApi.vcom_funny')
__all__ = ['API']


def parse(vcom_word: VCOMWord) -> Optional[_T.QueryWordData]:
    term = vcom_word['word']

    chunks: list[str] = []

    # definition

    definition = []

    if definitions := vcom_word['definitions']:
        # mimic the POS list above the short definition in the offline
        # dictionary "Vocabulary.com Dictionary by dfsfd@pdawikiBuild in
        # 2018/4/17"

        chunks.append('<div>')

        group = 0
        group_iter = map(lambda d: d['group'], definitions)
        first_group = next(group_iter)
        only_one_group = all(g == first_group for g in group_iter)
        last_pos = ''

        for d in definitions:
            if not only_one_group and group != d['group']:
                group = d['group']
                last_pos = ''
                chunks.append(f'{group} ')
            if last_pos != (pos := d['pos']):
                # don't duplicate pos for the same group
                last_pos = pos
                chunks.append(f'<span class="pos-{pos}">{pos}</span> ')

        chunks[-1] = chunks[-1][:-1]  # remove trailing space
        chunks.append('</div>')

    if funny_def_short := vcom_word['funny_def_short']:
        chunks.append(f'<p>{funny_def_short}</p>')
        if funny_def_long := vcom_word['funny_def_long']:
            chunks.append(f'<p>{funny_def_long}</p>')
        # append only if exist funny definition
        definition.append(''.join(chunks))

    # sentence

    sentence = []
    for vcom_s in vcom_word['sentences']:
        chunks.clear()

        sen = vcom_s['sentence']
        if len(offsets := vcom_s['offsets']) == 2:
            off1, off2 = offsets
            chunks.append(f'{sen[:off1]}<strong>{sen[off1:off2]}</strong>{sen[off2:]}')
        else:
            chunks.append(f'{sen}')

        chunks.append(
            f'<div><cite>{vcom_s["title"]}</cite> by {vcom_s["author"]}({datetime.datetime.fromtimestamp(vcom_s["date"] / 1000, datetime.timezone.utc).year})</div>'
        )

        # no front, only back
        sentence.append(('', ''.join(chunks)))

    # phonetic and pron

    phonetic_us = vcom_word['phonetics_us']
    phonetic_uk = vcom_word['phonetics_uk']
    pron_us = vcom_word['pron_audio_us']
    # pron_uk not supported, it's a mp4 file

    return _T.QueryWordData(
        term=term,
        definition=definition,
        phrase=[],
        image='',
        sentence=sentence,
        BrEPhonetic=phonetic_uk,
        AmEPhonetic=phonetic_us,
        BrEPron='',
        AmEPron=pron_us,
    )


class API(_T.AbstractQueryAPI):
    """
    Other fields not listed are empty:
    - term
    - definition: the short and long definition, for card back only
    - sentence: at most 4 examples, for card back only
    - BrEPhonetic
    - AmEPhonetic
    - AmEPron
    """

    name = 'funny Vocabulary.com API'
    desc = '不适合所有人；释义摘取两段趣味解释，有可能为空；只有释义、英式音标、美式音标、美式发音有数据，其他字段为空'
    session = session

    @classmethod
    def query(cls, word: str) -> Optional[_T.QueryWordData]:
        queryResult = None
        try:
            vcom_word = fetch_parse(word)
            queryResult = parse(vcom_word)
        except Exception as e:
            logger.exception(e)
        finally:
            logger.debug(queryResult)
            logger.info(f'{API.name}: {word}, {queryResult}')
        return queryResult
