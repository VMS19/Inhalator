import time
import logging
from threading import Thread

log = logging.getLogger(__name__)


class WdTask(Thread):
    WD_TIMEOUT = 0.25  # 250 msec
    GRACE_TIME = 4  # We allow the application this much time to start.

    def __init__(self, wd, arm_wd_event):
        super(WdTask, self).__init__()
        self.daemon = True
        self.wd = wd
        self.arm_wd_event = arm_wd_event
        self.log = logging.getLogger(self.__class__.__name__)

    def run(self):
        self.log.info(
            f"WD Task started. Waiting {self.GRACE_TIME} seconds for "
            f"application to start")
        # Let the application the opportunity to start.
        time.sleep(self.GRACE_TIME)
        self.log.info("Grace time passed, arming the dog")
        self.wd.arm()
        while True:
            time.sleep(self.WD_TIMEOUT)
            if self.arm_wd_event.isSet():
                self.log.debug("Refreshing WD")
                self.wd.arm()
                self.arm_wd_event.clear()
            else:
                self.log.warning("Application missed checking-in in time!")
