import logging
import os
import tempfile
import time
from queue import Queue
from threading import Thread

logger = logging.getLogger("dict2Anki.misc")


class Worker(Thread):
    def __init__(self, queue, result_queue):
        super(Worker, self).__init__()
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
            except Exception as e:
                logger.exception(e)
            finally:
                self._q.task_done()


class ThreadPool:
    def __init__(self, max_workers):
        self._q = Queue(max_workers)
        self.results_q = Queue()
        self.result = []
        """each item of result is a tuple ( args, kwargs, ret ).
        'args', 'kwargs' are the unnamed and named arguments you pass to submit function"""
        self._workers: list[Worker] = []
        # Create Worker Thread
        for _ in range(max_workers):
            self._workers.append(Worker(self._q, self.results_q))

    def submit(self, f, *args, **kwargs):
        self._q.put((f, args, kwargs))

    def wait_complete(self):
        self._q.join()
        while not self.results_q.qsize() == 0:
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
            self._q.put((lambda: None, tuple(), dict()))

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
    return f"{prefix}_{term}.mp3"


def tmp_audio_dir():
    return os.path.join(tempfile.gettempdir(), "Dict2Anki", "audios")
