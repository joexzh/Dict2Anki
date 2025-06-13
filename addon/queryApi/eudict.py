import logging
from typing import Optional

from bs4 import BeautifulSoup

from .._typing import AbstractQueryAPI, QueryWordData
from ..constants import *
from .. import dictionary

logger = logging.getLogger('dict2Anki.queryApi.eudict')
__all__ = ['API']


class Parser:
    def __init__(self, html: str, term: str):
        self._soap = BeautifulSoup(html, 'html.parser')
        self.term = term
        self._pronunciations = None

    @staticmethod
    def __fix_url_without_http(url):
        if len(url) > 1 and url[0:2] == '//':
            return 'https:' + url
        else:
            return url
        
    @staticmethod
    def __make_pron_url(url):
        if not url or 'http' in url:
            return url
        else:
            return 'https://api.frdic.com/api/v2/speech/speakweb?' + url

    @property
    def definition(self) -> list[str]:
        ret = []
        div = self._soap.select_one('div #ExpFCChild')
        if not div:
            return ret

        els = div.select('li') # 多词性
        if not els: # 单一词性
            els = div.select('.exp')
        if not els: # 还有一奇怪的情况，不在任何的标签里面，比如 https://dict.eudic.net/dicts/en/encyclopedia
            # 移除一些干扰text
            els_rm = div.select('#trans') # 时态text
            els_rm.extend(div.select('script'))
            els_rm.extend(div.select('a')) # 赞踩这些字样
            for el_rm in els_rm:
                if not el_rm.decomposed:
                    el_rm.decompose()

            els = [div]

        for el in els:
            ret.append(el.get_text(strip=True))

        return ret

    @property
    def pronunciations(self) -> dict[str, str]:
        if self._pronunciations:
            return self._pronunciations

        pron = {
            F_BREPHONETIC: '',
            F_BREPRON: '',
            F_AMEPHONETIC: '',
            F_AMEPRON: ''
        }

        try:
            if el_phon_line := self._soap.select_one('.phonitic-line'):
                links = el_phon_line.select('a')
                phons = el_phon_line.select('.Phonitic')

                if len(links) == 1: # 存在<a>标签，1个发音，例如 https://dict.eudic.net/dicts/en/hyperplane
                    pron[F_BREPRON] = self.__make_pron_url(links[0]['data-rel'])
                    pron[F_AMEPRON] = self.__make_pron_url(links[0]['data-rel'])
                    pron[F_BREPHONETIC] = phons[0].get_text(strip=True)
                    pron[F_AMEPHONETIC] = phons[0].get_text(strip=True)
                elif len(links) > 1: # 存在<a>标签，2个发音
                    pron[F_BREPRON] = self.__make_pron_url(links[0]['data-rel'])
                    pron[F_AMEPRON] = self.__make_pron_url(links[1]['data-rel'])
                    pron[F_BREPHONETIC] = phons[0].get_text(strip=True)
                    pron[F_AMEPHONETIC] = phons[0].get_text(strip=True) if len(phons) == 1 else phons[1].get_text(strip=True)
            elif link := self._soap.select_one('div .gv_details .voice-button'):
                # 只有"全球发音"，没有音标
                pron[F_BREPRON] = self.__make_pron_url(link['data-rel'])
                pron[F_AMEPRON] = self.__make_pron_url(link['data-rel'])
            elif link := self._soap.select_one('#tbOrgText a.voice-button'):
                # 在“参考译文”中，例如 https://dict.eudic.net/dicts/en/azeroth
                pron[F_BREPRON] = self.__make_pron_url(link['data-rel'])
                pron[F_AMEPRON] = self.__make_pron_url(link['data-rel'])
        except (TypeError, KeyError, IndexError):
            pass

        self._pronunciations = pron
        return pron

    @property
    def BrEPhonetic(self) -> str:
        """英式音标"""
        return self.pronunciations[F_BREPHONETIC]

    @property
    def AmEPhonetic(self) -> str:
        """美式音标"""
        return self.pronunciations[F_AMEPHONETIC]

    @property
    def BrEPron(self) -> str:
        """英式发音url"""
        return self.pronunciations[F_BREPRON]

    @property
    def AmEPron(self) -> str:
        """美式发音url"""
        return self.pronunciations[F_AMEPRON]

    @property
    def sentence(self) -> list[tuple[str, str]]:
        els = self._soap.select('div #ExpLJChild .lj_item')
        ret = []
        for el in els:
            el_line = el.select_one('p.line')
            if el_line:
                el_index = el_line.select_one('.index')
                el_index.extract() if el_index else None
                el_ext = el.select_one('p.exp')
                ret.append((el_line.get_text(), el_ext.get_text(strip=True) if el_ext else ''))
        return ret

    @property
    def image(self) -> str:
        el = self._soap.select_one('div .word-thumbnail-container img')
        ret = ''
        if el and 'title' not in el.attrs and 'src' in el.attrs:
            ret = self.__fix_url_without_http(el['src'])
        return ret

    @property
    def phrase(self) -> list[tuple[str, str]]:
        els = self._soap.select('div #ExpSPECChild #phrase')
        ret = []
        for el in els:
            el_phrase = el.find('i')
            el_exp = el.find(class_='exp')
            if el_phrase:
                ret.append((el_phrase.get_text(strip=True), el_exp.get_text(strip=True) if el_exp else ''))
        return ret

    @property
    def result(self):
        return QueryWordData(
            term=self.term,
            definition=self.definition,
            phrase=self.phrase,
            image=self.image,
            sentence=self.sentence,
            BrEPhonetic=self.BrEPhonetic,
            AmEPhonetic=self.AmEPhonetic,
            BrEPron=self.BrEPron,
            AmEPron=self.AmEPron
        )


class API(AbstractQueryAPI):
    import warnings
    warnings.warn("Deprecated. Will be removed next major version release.", DeprecationWarning, stacklevel=2)

    name = '欧路词典 API'
    # 重用 dictionary.Eudict 的 session。因为如果未登录，网页会返回反爬虫的版本
    timeout = dictionary.eudict.Eudict.timeout
    session = dictionary.eudict.Eudict.session
    url = 'https://dict.eudic.net/dicts/en/{}'
    parser = Parser

    @classmethod
    def query(cls, word: str) -> Optional[QueryWordData]:
        queryResult = None
        try:
            rsp = cls.session.get(cls.url.format(word), timeout=cls.timeout)
            logger.debug(f'code:{rsp.status_code}- word:{word} text:{rsp.text[:100]}')
            queryResult = cls.parser(rsp.text, word).result
        except Exception as e:
            logger.exception(e)
        finally:
            logger.debug(queryResult)
            return queryResult
