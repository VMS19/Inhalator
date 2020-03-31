from threading import Thread, Timer
import logging
import time

log = logging.getLogger(__name__)


class WdTask(Thread):
    WD_TIMEOUT = 0.2  # 200 msec
    START_TIMEOUT_SEC = 5

    def __init__(self, wd, arm_wd_event):
        super(WdTask, self).__init__()
        self.daemon = True
        self.wd = wd
        self.arm_wd_event = arm_wd_event

    def run(self):
        wd_check_timer = Timer(self.START_TIMEOUT_SEC, self._wd_periodic_check)
        wd_check_timer.start()

    def _wd_periodic_check(self):
        # Check if wd arm event was set
        if self.arm_wd_event.isSet():
            self.wd.arm_wd()
            self.arm_wd_event.clear()

            wd_check_timer = Timer(self.WD_TIMEOUT, self._wd_periodic_check)
            wd_check_timer.start()

        else:
            # wd timeout has passed. will trigger HW watchdog
            log.error("watchdog not refeshed!")


