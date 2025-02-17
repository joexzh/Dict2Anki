import logging
import time
from math import ceil
from typing import Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .._typing import AbstractDictionary
from ..constants import USER_AGENT

logger = logging.getLogger('dict2Anki.dictionary.eudict')


class Eudict(AbstractDictionary):
    name = '欧路词典'
    loginUrl = 'https://dict.eudic.net/account/login'
    timeout = 10
    headers = {
        'User-Agent': USER_AGENT,
    }
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers.update(headers)
    groups: list[tuple[str, str]] = []

    _indexSoup: Optional[BeautifulSoup] = None


    @classmethod
    def checkCookie(cls, cookie: dict) -> bool:
        """
        cookie有效性检验
        :param cookie:
        :return: Boolean cookie是否有效
        """
        rsp = requests.get('https://my.eudic.net/studylist', cookies=cookie, headers=cls.headers)
        if 'dict.eudic.net/account/login' not in rsp.url:
            cls._indexSoup = BeautifulSoup(rsp.text, features="html.parser")
            logger.info('Cookie有效')
            cookiesJar = requests.utils.cookiejar_from_dict(cookie, cookiejar=None, overwrite=True)
            cls.session.cookies = cookiesJar
            return True
        logger.info('Cookie失效')
        return False

    @staticmethod
    def loginCheckCallbackFn(cookie, content):
        if 'EudicWebSession' in cookie:
            return True
        return False

    @classmethod
    def getGroups(cls) -> list[tuple[str, str]]:
        """
        获取单词本分组
        :return: [(group_name,group_id)]
        """
        if cls._indexSoup is None:
            return []
        elements = cls._indexSoup.select('a.media_heading_a.new_cateitem_click')
        groups = []
        if elements:
            groups = [(el.get_text(strip=True), str(el['data-id'])) for el in elements]

        logger.info(f'单词本分组:{groups}')
        cls.groups = groups
        return groups

    @classmethod
    def getTotalPage(cls, groupName: str, groupId: str) -> int:
        """
        获取分组下总页数
        :param groupName: 分组名称
        :param groupId:分组id
        :return:
        """
        try:
            r = cls.session.post(
                url='https://my.eudic.net/StudyList/WordsDataSource',
                timeout=cls.timeout,
                data={'categoryid': groupId}
            )
            records = r.json()['recordsTotal']
            totalPages = ceil(records / 100)
            logger.info(f'该分组({groupName}-{groupId})下共有{totalPages}页')
            return totalPages
        except Exception as error:
            logger.exception(f'网络异常{error}')
            return 0

    @classmethod
    def getWordsByPage(cls, pageNo: int, groupName: str, groupId: str) -> list[str]:
        wordList = []
        data = {
            'columns[2][data]': 'word',
            'start': pageNo * 100,
            'length': 100,
            'categoryid': groupId,
            '_': int(time.time()) * 1000,
        }
        try:
            logger.info(f'获取单词本({groupName}-{groupId})第:{pageNo + 1}页')
            r = cls.session.post(
                url='https://my.eudic.net/StudyList/WordsDataSource',
                timeout=cls.timeout,
                data=data
            )
            wl = r.json()
            wordList = list(set(word['uuid'] for word in wl['data']))
        except Exception as error:
            logger.exception(f'网络异常{error}')
        finally:
            logger.info(wordList)
            return wordList
