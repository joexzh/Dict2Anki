import json
import logging
import os
from itertools import chain

import requests
from aqt import QObject, QRunnable, QThread, pyqtSignal
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from ._typing import AbstractDictionary, AbstractQueryAPI, QueryWordData
from .constants import *
from .misc import ThreadPool, congestGenerator


class VersionCheckWorker(QObject):
    haveNewVersion = pyqtSignal(str, str)
    finished = pyqtSignal()
    start = pyqtSignal()
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
            self.finished.emit()


class LoginStateCheckWorker(QObject):
    start = pyqtSignal()
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


class RemoteWordFetchingWorker(QObject):
    start = pyqtSignal()
    tick = pyqtSignal()
    setProgress = pyqtSignal(int)
    done = pyqtSignal()
    doneThisGroup = pyqtSignal(list)
    _logger = logging.getLogger("dict2Anki.workers.RemoteWordFetchingWorker")

    def __init__(self, selectedDict: type[AbstractDictionary], groups: list[tuple[str, str]]):
        super().__init__()
        self.selectedDict = selectedDict
        self.groups = groups

    def run(self):
        currentThread = QThread.currentThread()
        if currentThread is None:
            raise RuntimeError

        def _pull(*args):
            if currentThread.isInterruptionRequested():
                return
            wordPerPage = self.selectedDict.getWordsByPage(*args)
            self.tick.emit()
            return wordPerPage

        for groupName, groupId in self.groups:
            totalPage = self.selectedDict.getTotalPage(groupName, groupId)
            self.setProgress.emit(totalPage)
            with ThreadPool(max_workers=3) as executor:
                for i in range(totalPage):
                    executor.submit(_pull, i, groupName, groupId)
            remoteWordList = list(chain(*[ft[2] for ft in executor.result]))
            self.doneThisGroup.emit(remoteWordList)

        self.done.emit()


class QueryWorker(QObject, QRunnable):
    start = pyqtSignal()
    tick = pyqtSignal()
    rowSuccess = pyqtSignal(tuple, dict)
    rowFail = pyqtSignal(tuple)
    done = pyqtSignal(list)
    _logger = logging.getLogger("dict2Anki.workers.QueryWorker")

    def __init__(self, row_words: list[tuple[int, str]], api: type[AbstractQueryAPI], congest=60):
        super().__init__()
        self._row_words = row_words
        self._api = api
        self._congest = congest

    def run(self):
        currentThread = QThread.currentThread()
        if currentThread is None:
            raise RuntimeError

        def _query(row_word):
            row, word = row_word
            if currentThread.isInterruptionRequested():
                return
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
                next(congestGen)
                executor.submit(_query, row_word)

        results = [(r[0][0], r[2]) for r in executor.result]
        self.done.emit(results)
        return results


class AudioDownloadWorker(QObject):
    start = pyqtSignal()
    tick = pyqtSignal(tuple, bool)
    done = pyqtSignal(list)
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

    def run(self):
        currentThread = QThread.currentThread()
        if currentThread is None:
            raise RuntimeError

        def _download(audio: tuple[str, str]):
            success = False
            fileName, url = audio
            try:
                if currentThread.isInterruptionRequested():
                    return
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
                next(congestGen)
                executor.submit(_download, audio)

        results = [(r[0][0] ,r[2]) for r in executor.result]
        self.done.emit(results)
        return results
