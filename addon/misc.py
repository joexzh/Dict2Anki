import base64
import importlib
import logging
import os
import pkgutil
import shutil
import tempfile
import time
import typing as T
from queue import Queue
from threading import Thread
from types import ModuleType

import requests

logger = logging.getLogger('dict2Anki.misc')


class Worker(Thread):
    def __init__(self, queue, result_queue):
        super().__init__()
        self._q = queue
        self.result_queue = result_queue
        self.daemon = True
        self.interrupted = False
        self.start()

    def run(self):
        while True:
            try:
                f, args, kwargs = self._q.get()
                if self.interrupted:
                    return
                result = f(*args, **kwargs)
                self.result_queue.put((args, kwargs, result))
            except Exception:
                # it will auto log the exception inside except block
                logger.exception('Error in thread pool worker')
            finally:
                self._q.task_done()


class ThreadPool:
    def __init__(self, max_workers):
        self._q = Queue(max_workers)
        self.results_q = Queue()

        self.result = []
        """
        each item of result is a tuple ( args, kwargs, ret ).
        'args', 'kwargs' are the unnamed and named arguments you pass to submit function
        """

        self._workers: list[Worker] = []
        # Create Worker Thread
        for _ in range(max_workers):
            self._workers.append(Worker(self._q, self.results_q))

    def submit(self, f, *args, **kwargs):
        self._q.put((f, args, kwargs))

    def wait_complete(self):
        self._q.join()
        while self.results_q.qsize() != 0:
            self.result.append(self.results_q.get())

        return self.result

    def exit(self):
        self.wait_complete()

        # At this point all threads are blocked by queue.get(),
        # so put dummy items to unblock them.
        # Till Python 3.13 we can switch to queue.shutdown()
        for worker in self._workers:
            worker.interrupted = True  # run in GIL, presume thread safe?
        for _ in range(len(self._workers)):
            self._q.put((lambda: None, (), {}))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()


def congestGenerator(n=60):
    """yields n times per minute"""
    co = n / 60
    start = time.time()
    cnt = 1
    yield  #  yield first iteration immediately

    while True:
        if (time.time() - start) * co > cnt:
            cnt += 1
            yield
        else:
            time.sleep(1)


def audio_fname(prefix: str, term: str):
    return f'{prefix}_{term}.mp3'


def tmp_audio_dir():
    return os.path.join(tempfile.gettempdir(), 'Dict2Anki', 'audios')


_RANDOM_MASK = b'0SiCw@kFBPY^4n'


def enc_cookies(cookies: str) -> str:
    """each byte xor mask and encode to base64 string"""

    byts = bytearray(cookies, 'utf-8')
    for i in range(len(byts)):
        byts[i] = byts[i] ^ _RANDOM_MASK[i % len(_RANDOM_MASK)]
    b64_str = base64.b64encode(byts).decode('utf-8')
    return b64_str


def dec_cookies(cookies_enc: str) -> str:
    """revert enc_cookies"""

    byts = bytearray(base64.b64decode(cookies_enc))
    for i in range(len(byts)):
        byts[i] = byts[i] ^ _RANDOM_MASK[i % len(_RANDOM_MASK)]
    return byts.decode('utf-8')


def load_all_modules(rel_package: str, package: T.Optional[str]):
    """
    Load and return all modules found in package path `rel_package`, relative to
    caller's `__package__`.

    Usage:

    ```python
    mods = load_all_modules('...user_files.queryApi', __package__)
    ```
    """
    mods: list[ModuleType] = []
    pkg = importlib.import_module(rel_package, package)

    for _finder, mod_name, _ispkg in pkgutil.iter_modules(pkg.__path__):
        full_name = f'{pkg.__name__}.{mod_name}'
        mods.append(importlib.import_module(full_name))
    return mods


def download_file(session: requests.Session, fileName: str, url: str):
    r = session.get(url, stream=True)
    if not r.ok:
        raise PermissionError(f'http status code: {r.status_code}')
    with open(fileName, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def rm_file(fpath: str):
    if os.path.isfile(fpath):
        os.remove(fpath)


def mv_file(src: str, dst: str):
    if os.path.isfile(src):
        rm_file(dst)
        shutil.move(src, dst)
        return True
    return False
