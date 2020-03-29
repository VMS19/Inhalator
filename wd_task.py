from threading import Event, Thread
import time
import logging

log = logging.getLogger(__name__)


class WdTask(Thread):
    WD_TIMEOUT = 100

    def __init__(self, store, wd, arm_wd_event):
        super(WdTask, self).__init__()
        self.daemon = True
        self.store = store
        self.wd = wd
        self.arm_wd_event = arm_wd_event

        # arm wd
        self.wd_refresh_time = time.time() * self.store.MS_TO_SEC

    def run(self):
        while True:
            # Check if wd arm event was set
            if self.arm_wd_event.isSet():
                self._wd_refresh_timer()
                self.arm_wd_event.clear()

            # Check if wd timeout has passed 
            wd_diff = ((time.time() * self.store.MS_TO_SEC) - self.wd_refresh_time)
            if wd_diff < self.WD_TIMEOUT:
                self.wd.arm_wd()
            else:
                log.error("wd not refeshed!")

    def _wd_refresh_timer(self):
    	self.wd_refresh_time = time.time() * self.store.MS_TO_SEC
