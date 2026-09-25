from __future__ import annotations

import json
import logging
import os
import typing as T
from abc import abstractmethod
from itertools import chain

import requests
from aqt import QObject, pyqtBoundSignal, pyqtSignal
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from . import adv_conf, misc
from . import constants as C
from . import global_vars as V
from ._typing import AbstractDictionary, QueryWordData


class AbstractWorker(QObject):
    done = pyqtSignal(object)
    'Workers must use done to emit itself before run() returns, otherwise leak!'

    def __init__(self, parent=None):
        super().__init__(parent)
        self.interrupted = False
        'Set by WorkerManager when destroyed.'

    @abstractmethod
    def run(self):
        "Required!"
        pass


class NetworkWorker(AbstractWorker):
    retries = Retry(total=5, backoff_factor=3, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers.update({'User-Agent': V.user_agent()})

    def __init__(self, parent=None):
        super().__init__(parent)


class WorkerManager:
    _logger = logging.getLogger('dict2Anki.workers.WorkerManager')

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
    _logger = logging.getLogger('dict2Anki.workers.UpdateCheckWorker')

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            self._logger.info('检查新版本')
            rsp = requests.get(C.VERSION_CHECK_API, timeout=20).json()
            version = rsp['tag_name']
            changeLog = rsp['body']
            if version != C.VERSION:
                self._logger.info(f'检查到新版本:{version}--{changeLog.strip()}')
                self.haveNewVersion.emit(version.strip(), changeLog.strip())
            else:
                self._logger.info(f'当前为最新版本:{C.VERSION}')
        except Exception as e:
            self._logger.error(f'版本检查失败{e}')

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
    _logger = logging.getLogger('dict2Anki.workers.RemoteWordFetchingWorker')

    def __init__(self, selectedDict: type[AbstractDictionary], groups: list[tuple[str, str]]):
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


class ApiASTWorker(AbstractWorker):
    "eval AST with ApiFConfVisitor"

    rowSuccess = pyqtSignal(int, str, dict)  # row, word, query_cache
    rowFail = pyqtSignal(int, str, dict)  # row, word, query_cache
    _logger = logging.getLogger('dict2Anki.workers.ApiASTWorker')

    def __init__(
        self,
        row_words: list[tuple[int, str]],  # e.g. (0, 'hello')
        fconf_ast_dict: dict[str, adv_conf.FConfAST],
        congest: int = 120,
        parent=None,
    ):
        super().__init__(parent)
        self.row_words = row_words
        self.congest = congest
        self.fconf_ast_dict = fconf_ast_dict

    def run(self):

        def fetch_word(row: int, word: str):
            query_cache: dict[str, T.Optional[QueryWordData]] = {}
            ret_eval = False

            for field, ast in self.fconf_ast_dict.items():
                if self.interrupted:
                    break
                ret_eval = ast.eval(adv_conf.ApiFConfVisitor(word, field, query_cache)) or ret_eval
            self.rowSuccess.emit(row, word, query_cache) if ret_eval else self.rowFail.emit(row, word, query_cache)

        try:
            congestGen = misc.congestGenerator(self.congest)
            with misc.ThreadPool(max_workers=3) as pool:
                for row, word in self.row_words:
                    if self.interrupted:
                        break
                    next(congestGen)
                    pool.submit(fetch_word, row, word)
        finally:
            self.done.emit(self)
