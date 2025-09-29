import time

import aqt

from ..addon import workers


class DummyWorker(workers.AbstractWorker):
    sig_1 = aqt.pyqtSignal()
    sig_2 = aqt.pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            while True:
                if self.interrupted:
                    break
                time.sleep(0.01)

        finally:
            self.done.emit(self)


def test_workerman_destroy_disconnect():
    def on_sig_1():
        pass

    def on_sig_2(s):
        pass

    man = workers.WorkerManager()
    worker = DummyWorker()
    worker.sig_1.connect(on_sig_1)
    worker.sig_2.connect(on_sig_2)
    man.start(worker)

    assert 2 == aqt.QObject.receivers(worker, worker.sig_1) + aqt.QObject.receivers(
        worker, worker.sig_2
    )

    man.destroy()

    assert 0 == aqt.QObject.receivers(worker, worker.sig_1) + aqt.QObject.receivers(
        worker, worker.sig_2
    )
