import json
import logging
import os
from abc import abstractmethod
from itertools import chain

import requests
from aqt import QObject, pyqtBoundSignal, pyqtSignal
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from ._typing import AbstractDictionary, AbstractQueryAPI, QueryWordData
from .constants import *
from .misc import ThreadPool, congestGenerator


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


class WorkerManager:
    _logger = logging.getLogger("dict2Anki.workers.WorkerManager")

    def __init__(self):
        self._pool = ThreadPool(max_workers=os.cpu_count())
        self._workers: list[AbstractWorker] = []

    def start(self, worker: AbstractWorker):
        worker.done.connect(self._on_worker_done)
        self._workers.append(worker)
        self._pool.submit(lambda: (lambda worker: worker.run())(worker))

    def destroy(self):
        for worker in self._workers:
            worker.interrupted = True
        self._pool.wait_complete()

    def _on_worker_done(self, worker):
        self._logger.info("worker done: " + str(worker))
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
                with ThreadPool(max_workers=3) as executor:
                    for i in range(totalPage):
                        if self.interrupted:
                            return
                        executor.submit(_pull, i, groupName, groupId)
                remoteWordList = list(chain(*[ft[2] for ft in executor.result]))
                self.doneThisGroup.emit(remoteWordList)
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
            queryResult = self._api.query(word)
            if queryResult:
                self._logger.info(f"查询成功: {row}, {word} -- {queryResult}")
                self.rowSuccess.emit(row, word, queryResult)
            else:
                self._logger.warning(f"查询失败: {row}, {word}")
                self.rowFail.emit(row, word)
            self.tick.emit()
            return queryResult

        try:
            with ThreadPool(max_workers=3) as executor:
                congestGen = congestGenerator(self._congest)
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


class NetworkWorker(AbstractWorker):
    retries = Retry(total=5, backoff_factor=3, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": USER_AGENT})

    def __init__(self):
        super().__init__()


def downloadSingleAudio(
    fileName: str,
    url: str,
    session: requests.Session,
    logger: logging.Logger,
    tick: pyqtBoundSignal,
):
    success = False
    try:
        r = session.get(url, stream=True)
        with open(fileName, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        success = True
        logger.info(f"发音下载完成：{fileName}, {url}")
    except Exception as e:
        logger.warning(f"下载{fileName}, {url}，异常: {e}")
        if os.path.isfile(fileName):
            os.remove(fileName)
        success = False
    finally:
        tick.emit(fileName, url, success)
    return success


class AudioDownloadWorker(NetworkWorker):
    tick = pyqtSignal(str, str, bool)
    _logger = logging.getLogger("dict2Anki.workers.AudioDownloadWorker")

    def __init__(self, audios: list[tuple[str, str]]):
        super().__init__()
        self._audios = audios

    def run(self):

        try:
            with ThreadPool(max_workers=3) as executor:
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
