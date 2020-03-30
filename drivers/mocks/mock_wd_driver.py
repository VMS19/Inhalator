import time
from threading import Timer, Lock

class MockWdDriver(object):
    WD_REFRESH_HZ = 2000
    WD_REFRESH_SIGNAL_SEC = (1 / WD_REFRESH_HZ)

    def __init__(self):
        self.arm_wd_lock = Lock()

    def arm_wd(self):
        self.arm_wd_lock.acquire()
        refresh_delay_timer = Timer(self.WD_REFRESH_SIGNAL_SEC,
                                    self._pull_wd_down)
        self._pull_wd_up()
        refresh_delay_timer.start()

    def _pull_wd_up(self):
        pass

    def _pull_wd_down(self):
        self.arm_wd_lock.release()
