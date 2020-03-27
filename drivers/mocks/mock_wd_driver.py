import time


class MockWdDriver(object):
    WD_SIGNAL_LEN = 0.05

    def __init__(self):
        pass

    def arm_wd(self):
        # Simulate watchdog arm swing delay
        time.sleep(self.WD_SIGNAL_LEN)
