import logging
from math import ceil
from typing import Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .._typing import AbstractDictionary
from ..constants import USER_AGENT

logger = logging.getLogger('dict2Anki.dictionary.youdao')


class Youdao(AbstractDictionary):
    name = '有道词典'
    loginUrl = 'http://account.youdao.com/login?service=dict&back_url=http://dict.youdao.com/wordbook/wordlist%3Fkeyfrom%3Dnull'
    timeout = 10
    headers = {
        'Host': 'dict.youdao.com',
        'User-Agent': USER_AGENT,
    }
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    groups: list[tuple[str, str]] = []

    _indexSoup: Optional[BeautifulSoup] = None

    @classmethod
    def checkCookie(cls, cookie: dict) -> bool:
        """
        cookie有效性检验
        :param cookie:
        :return: bool
        """
        rsp = requests.get('http://dict.youdao.com/login/acc/query/accountinfo', cookies=cookie, headers=cls.headers)
        if rsp.json().get('code', None) == 0:
            cls._indexSoup = BeautifulSoup(rsp.text, features="html.parser")
            logger.info('Cookie有效')
            cookiesJar = requests.utils.cookiejar_from_dict(cookie, cookiejar=None, overwrite=True)
            cls.session.cookies = cookiesJar
            return True
        logger.info('Cookie失效')
        return False

    @staticmethod
    def loginCheckCallbackFn(cookie, content):
        if 'DICT_SESS' in cookie:
            return True
        return False

    @classmethod
    def getGroups(cls) -> list[tuple[str, str]]:
        """
        获取单词本分组
        :return: [(group_name,group_id)]
        """
        r = cls.session.get(
            url='http://dict.youdao.com/wordbook/webapi/books',
            timeout=cls.timeout,
        )
        groups = [(g['bookName'], g['bookId']) for g in r.json()['data']]
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
            r = cls.session.get(
                url='http://dict.youdao.com/wordbook/webapi/words',
                timeout=cls.timeout,
                params={'bookId': groupId, 'limit': 1, 'offset': 0}
            )
            totalWords = r.json()['data']['total']
            totalPages = ceil(totalWords / 15)  # 这里按网页默认每页取15个
            logger.info(f'该分组({groupName}-{groupId})下共有{totalPages}页')
            return totalPages
        except Exception as error:
            logger.exception(f'网络异常{error}')
            return 0

    @classmethod
    def getWordsByPage(cls, pageNo: int, groupName: str, groupId: str) -> list[str]:
        """
        获取分组下每一页的单词
        :param pageNo: 页数
        :param groupName: 分组名
        :param groupId: 分组id
        :return:
        """
        wordList = []
        try:
            logger.info(f'获取单词本({groupName}-{groupId})第:{pageNo}页')
            r = cls.session.get(
                'http://dict.youdao.com/wordbook/webapi/words',
                timeout=cls.timeout,
                params={'bookId': groupId, 'limit': 15, 'offset': pageNo * 15}
            )
            wordList = [item['word'] for item in r.json()['data']['itemList']]
        except Exception as e:
            logger.exception(f'网络异常{e}')
        finally:
            logger.info(wordList)
            return wordList
