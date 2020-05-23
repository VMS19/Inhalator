import time
import logging
from threading import Thread

log = logging.getLogger(__name__)


class WdTask(Thread):
    # We've seen that timeout between two arms were about 300-400ms,
    # although the timeout was 300ms, and the HW watchdog is every 500ms.
    # If we're at the 400ms limit and there was a 100ms delay in the main loop
    # the WD will rise.
    # Lowering the wd_arm time will help us make sure the main loop
    # refreshes the WD even if a delay in the main loop occurred
    WD_TIMEOUT = 0.2  # 200 msec

    def __init__(self, wd, arm_wd_event):
        super(WdTask, self).__init__()
        self.daemon = True
        self.wd = wd
        self.arm_wd_event = arm_wd_event
        self.log = logging.getLogger(self.__class__.__name__)

    def run(self):
        self.log.info("WD Task started")
        self.wd.arm()
        while True:
            time.sleep(self.WD_TIMEOUT)
            if self.arm_wd_event.isSet():
                self.log.debug("Refreshing WD")
                self.wd.arm()
                self.arm_wd_event.clear()
            else:
                self.log.warning("Application missed checking-in in time!")
