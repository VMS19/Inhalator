import time
from threading import Timer

class MockWdDriver(object):
    WD_REFRESH_HZ = 2000
    WD_REFRESH_SIGNAL_SEC = (1 / WD_REFRESH_HZ)

    def __init__(self):
        self.refresh_delay_timer = Timer(self.WD_REFRESH_SIGNAL_SEC,
                                         self._pull_wd_down)

    def arm_wd(self):
        self._pull_wd_up()
        self.refresh_delay_timer.start()

    def _pull_wd_up(self):
        pass

    def _pull_wd_down(self):
        pass
