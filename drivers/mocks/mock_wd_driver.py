import time


class MockWdDriver(object):
    WD_REFRESH_HZ = 2000
    WD_REFRESH_SIGNAL_SEC = (1 / WD_REFRESH_HZ)

    def __init__(self):
        pass

    def arm_wd(self):
        # Simulate watchdog arm swing delay
        time.sleep(self.WD_REFRESH_SIGNAL_SEC)
