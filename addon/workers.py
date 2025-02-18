import json
import logging
import os
from abc import abstractmethod
from itertools import chain

import requests
from aqt import QObject, pyqtSignal
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from ._typing import AbstractDictionary, AbstractQueryAPI, QueryWordData
from .constants import *
from .misc import ThreadPool, congestGenerator


class AbstractWorker(QObject):
    done = pyqtSignal(object)
    """Workers must use done to emit itself, otherwise leak!"""

    @abstractmethod
    def run(self):
        """Required!"""
        pass

    @abstractmethod
    def interrupt(self):
        """Long running worker should implement this,
        otherwise prevents anki process to end!
        
        This is invoked by WorkerManger, be careful not to cause race condition."""
        pass


class WorkerManager:

    def __init__(self):
        self._pool = ThreadPool(max_workers=3)
        self._workers: list[AbstractWorker] = []

    def start(self, worker: AbstractWorker):
        worker.done.connect(self._on_worker_done)
        self._workers.append(worker)
        self._pool.submit(lambda: (lambda worker: worker.run())(worker))

    def destroy(self):
        for worker in self._workers:
            if worker.interrupt:
                worker.interrupt()
        self._pool.wait_complete()

    def _on_worker_done(self, worker):
        logging.info("worker done: " + str(worker))
        self._workers.remove(worker)


class VersionCheckWorker(AbstractWorker):
    haveNewVersion = pyqtSignal(str, str)
    _logger = logging.getLogger("dict2Anki.workers.UpdateCheckWorker")

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
        self._interrupted = False

    def interrupt(self):
        self._interrupted = True

    def run(self):

        def _pull(*args):
            wordPerPage = self.selectedDict.getWordsByPage(*args)
            self.tick.emit()
            return wordPerPage

        for groupName, groupId in self.groups:
            totalPage = self.selectedDict.getTotalPage(groupName, groupId)
            self.setProgress.emit(totalPage)
            with ThreadPool(max_workers=3) as executor:
                for i in range(totalPage):
                    if self._interrupted:
                        return
                    executor.submit(_pull, i, groupName, groupId)
            remoteWordList = list(chain(*[ft[2] for ft in executor.result]))
            self.doneThisGroup.emit(remoteWordList)

        self.done.emit(self)


class QueryWorker(AbstractWorker):
    tick = pyqtSignal()
    rowSuccess = pyqtSignal(tuple, dict)
    rowFail = pyqtSignal(tuple)
    doneWithResult = pyqtSignal(list)
    _logger = logging.getLogger("dict2Anki.workers.QueryWorker")

    def __init__(
        self, row_words: list[tuple[int, str]], api: type[AbstractQueryAPI], congest=60
    ):
        super().__init__()
        self._row_words = row_words
        self._api = api
        self._congest = congest
        self._interrupted = False

    def interrupt(self):
        self._interrupted = True

    def run(self):

        def _query(row_word):
            row, word = row_word
            queryResult = self._api.query(word)
            if queryResult:
                self._logger.info(f"查询成功: {row_word} -- {queryResult}")
                self.rowSuccess.emit(row_word, queryResult)
            else:
                self._logger.warning(f"查询失败: {row_word}")
                self.rowFail.emit(row_word)
            self.tick.emit()
            return queryResult

        with ThreadPool(max_workers=3) as executor:
            congestGen = congestGenerator(self._congest)
            for row_word in self._row_words:
                if self._interrupted:
                    return
                next(congestGen)
                executor.submit(_query, row_word)

        results = [(r[0][0], r[2]) for r in executor.result]
        self.doneWithResult.emit(results)
        self.done.emit(self)
        return results


class AudioDownloadWorker(AbstractWorker):
    tick = pyqtSignal(tuple, bool)
    retries = Retry(total=5, backoff_factor=3, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": USER_AGENT})
    _logger = logging.getLogger("dict2Anki.workers.AudioDownloadWorker")

    def __init__(self, audios: list[tuple[str, str]], congest=60):
        super().__init__()
        self._audios = audios
        self._congest = congest
        self._interrupted = False

    def interrupt(self):
        self._interrupted = True

    def run(self):

        def _download(audio: tuple[str, str]):
            success = False
            fileName, url = audio
            try:
                r = self.session.get(url, stream=True)
                with open(fileName, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                success = True
                self._logger.info(f"发音下载完成：{audio}")
            except Exception as e:
                self._logger.warning(f"下载{audio}，异常: {e}")
                if os.path.isfile(fileName):
                    os.remove(fileName)
                success = False
            finally:
                self.tick.emit(audio, success)
            return success

        with ThreadPool(max_workers=3) as executor:
            congestGen = congestGenerator(self._congest)
            for audio in self._audios:
                if self._interrupted:
                    return
                next(congestGen)
                executor.submit(_download, audio)

        self.done.emit(self)
