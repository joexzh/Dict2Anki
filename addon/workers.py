import json
import logging
import os
import typing
from abc import abstractmethod
from itertools import chain

import requests
from aqt import QObject, pyqtBoundSignal, pyqtSignal
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from . import misc
from ._typing import AbstractDictionary, AbstractQueryAPI, QueryWordData
from .constants import *


class AbstractWorker(QObject):
    done = pyqtSignal(object)
    """Workers must use done to emit itself before run() returns, otherwise leak!"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.interrupted = False
        """Set by WorkerManager when destroyed."""

    @abstractmethod
    def run(self):
        """Required!"""
        pass


class NetworkWorker(AbstractWorker):
    retries = Retry(total=5, backoff_factor=3, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": USER_AGENT})

    def __init__(self):
        super().__init__()


class WorkerManager:
    _logger = logging.getLogger("dict2Anki.workers.WorkerManager")

    def __init__(self):
        self._pool = misc.ThreadPool(max_workers=os.cpu_count())
        self._workers: list[AbstractWorker] = []

    def start(self, worker: AbstractWorker):
        worker.done.connect(self._on_worker_done)
        self._workers.append(worker)
        # python automatically wraps the bounded method, so `submit(worker.run)` is also ok
        self._pool.submit(lambda: (lambda worker: worker.run())(worker))

    def destroy(self):
        for worker in self._workers:
            worker.interrupted = True
            worker.disconnect()
        self._pool.exit()

    def _on_worker_done(self, worker):
        self._workers.remove(worker)


class VersionCheckWorker(AbstractWorker):
    haveNewVersion = pyqtSignal(str, str)
    _logger = logging.getLogger("dict2Anki.workers.UpdateCheckWorker")

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            self._logger.info("检查新版本")
            rsp = requests.get(VERSION_CHECK_API, timeout=20).json()
            version = rsp["tag_name"]
            changeLog = rsp["body"]
            if version != VERSION:
                self._logger.info(f"检查到新版本:{version}--{changeLog.strip()}")
                self.haveNewVersion.emit(version.strip(), changeLog.strip())
            else:
                self._logger.info(f"当前为最新版本:{VERSION}")
        except Exception as e:
            self._logger.error(f"版本检查失败{e}")

        finally:
            self.done.emit(self)


class LoginStateCheckWorker(AbstractWorker):
    logSuccess = pyqtSignal(str)
    logFailed = pyqtSignal()

    def __init__(self, checkFn, cookie):
        super().__init__()
        self.checkFn = checkFn
        self.cookie = cookie

    def run(self):
        loginState = self.checkFn(self.cookie)
        if loginState:
            self.logSuccess.emit(json.dumps(self.cookie))
        else:
            self.logFailed.emit()
        self.done.emit(self)


class RemoteWordFetchingWorker(AbstractWorker):
    tick = pyqtSignal()
    setProgress = pyqtSignal(int)
    doneThisGroup = pyqtSignal(list)
    _logger = logging.getLogger("dict2Anki.workers.RemoteWordFetchingWorker")

    def __init__(
        self, selectedDict: type[AbstractDictionary], groups: list[tuple[str, str]]
    ):
        super().__init__()
        self.selectedDict = selectedDict
        self.groups = groups

    def run(self):

        def _pull(*args):
            wordPerPage = self.selectedDict.getWordsByPage(*args)
            self.tick.emit()
            return wordPerPage

        try:
            for groupName, groupId in self.groups:

                totalPage = self.selectedDict.getTotalPage(groupName, groupId)
                self.setProgress.emit(totalPage)
                with misc.ThreadPool(max_workers=3) as executor:
                    for i in range(totalPage):
                        if self.interrupted:
                            return
                        executor.submit(_pull, i, groupName, groupId)
                remoteWordList = list(chain(*[ft[2] for ft in executor.result]))
                self.doneThisGroup.emit(remoteWordList)
        finally:
            self.done.emit(self)


def query_word(
    row: int,
    word: str,
    api: type[AbstractQueryAPI],
    logger: logging.Logger,
    sig_success: pyqtBoundSignal,
    sig_fail: pyqtBoundSignal,
    sig_done: pyqtBoundSignal,
):
    """
    Query a single word through `api`

    :param sig_success: emit(row, word, queryResult)
    :param sig_fail: emit(row, word)
    :param sig_done: emit()
    """
    queryResult = api.query(word)
    if queryResult:
        logger.info(f"查询成功: {row}, {word} -- {queryResult}")
        sig_success.emit(row, word, queryResult)
    else:
        logger.warning(f"查询失败: {row}, {word}")
        sig_fail.emit(row, word)
    sig_done.emit()
    return queryResult


def download_file(session: requests.Session, fileName, url):
    r = session.get(url, stream=True)
    if not r.ok:
        raise PermissionError(f"http status code: {r.status_code}")
    with open(fileName, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def rmv_file(fileName):
    if os.path.isfile(fileName):
        os.remove(fileName)


def downloadSingleAudio(
    fileName: str,
    url: str,
    session: requests.Session,
    logger: logging.Logger,
    tick: pyqtBoundSignal,
):
    success = False
    try:
        download_file(session, fileName, url)
        success = True
        logger.info(f"发音下载完成：{fileName}, {url}")
    except Exception as e:
        logger.warning(f"下载{fileName}, {url}，异常: {e}")
        rmv_file(fileName)
        success = False
    finally:
        tick.emit(fileName, url, success)
    return success


class QueryAllWorker(NetworkWorker):
    """Query words and download audios"""

    rowSuccess = pyqtSignal(int, str, dict)
    rowFail = pyqtSignal(int, str)
    query_word_tick = pyqtSignal()
    audio_tick = pyqtSignal(str, str, bool)
    """emit(file_name, url, success)"""
    doneWithResult = pyqtSignal(list)
    _logger = logging.getLogger("dict2Anki.workers.QueryAllWorker")

    def __init__(
        self,
        row_words: list[tuple[int, str]],
        which_pron: typing.Optional[str],
        api: type[AbstractQueryAPI],
        congest=60,
    ):
        super().__init__()
        self._row_words = row_words
        self._which_pron = which_pron
        self._api = api
        self._congest = congest
        self._results: list[tuple[int, str, typing.Optional[QueryWordData]]] = []
        """list[tuple[row, word, QueryWordData|None]]"""

    def run(self):
        try:
            tmp_audio_dir = misc.tmp_audio_dir()
            os.makedirs(tmp_audio_dir, exist_ok=True)

            congestGen = misc.congestGenerator(self._congest)
            for row, word in self._row_words:
                if self.interrupted:
                    break
                next(congestGen)
                result = query_word(
                    row,
                    word,
                    self._api,
                    self._logger,
                    self.rowSuccess,
                    self.rowFail,
                    self.query_word_tick,
                )
                if result and self._which_pron and result.get(self._which_pron):
                    tmp_audio_path = os.path.join(
                        tmp_audio_dir,
                        misc.audio_fname(self._which_pron, result[F_TERM]),
                    )
                    downloadSingleAudio(
                        tmp_audio_path,
                        result[self._which_pron],
                        self.session,
                        self._logger,
                        self.audio_tick,
                    )

                self._results.append((row, word, result))

            self.doneWithResult.emit(self._results)
        finally:
            self.done.emit(self)


class QueryWorker(AbstractWorker):
    tick = pyqtSignal()
    rowSuccess = pyqtSignal(int, str, dict)
    rowFail = pyqtSignal(int, str)
    doneWithResult = pyqtSignal(list)
    _logger = logging.getLogger("dict2Anki.workers.QueryWorker")

    def __init__(
        self, row_words: list[tuple[int, str]], api: type[AbstractQueryAPI], congest=60
    ):
        super().__init__()
        self._row_words = row_words
        self._api = api
        self._congest = congest

    def run(self):

        def _query(row, word):
            return query_word(
                row,
                word,
                self._api,
                self._logger,
                self.rowSuccess,
                self.rowFail,
                self.tick,
            )

        try:
            with misc.ThreadPool(max_workers=3) as executor:
                congestGen = misc.congestGenerator(self._congest)
                for row, word in self._row_words:
                    if self.interrupted:
                        return
                    next(congestGen)
                    executor.submit(_query, row, word)

            results = [(r[0][0], r[0][1], r[2]) for r in executor.result]
            self.doneWithResult.emit(results)
            return results
        finally:
            self.done.emit(self)


class AudioDownloadWorker(NetworkWorker):
    tick = pyqtSignal(str, str, bool)
    _logger = logging.getLogger("dict2Anki.workers.AudioDownloadWorker")

    def __init__(self, audios: list[tuple[str, str]]):
        super().__init__()
        self._audios = audios

    def run(self):

        try:
            with misc.ThreadPool(max_workers=3) as executor:
                for fileName, url in self._audios:
                    if self.interrupted:
                        return
                    executor.submit(
                        downloadSingleAudio,
                        fileName,
                        url,
                        self.session,
                        self._logger,
                        self.tick,
                    )
        finally:
            self.done.emit(self)
