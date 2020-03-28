#import RPi.GPIO as GPIO
from threading import Event, Thread
import time

class WdTask(Thread):
    WD_REFRESH_HZ = 2000
    WD_REFRESH_SIGNAL_SEC = (1 / WD_REFRESH_HZ)
    WD_TIMEOUT = 100
    WD_GPIO = 5
    FAULT_GPIO = 19 

    def __init__(self, store):
        super(WdTask, self).__init__()
        self.daemon = True
        self.store = store

        # Set WD GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.WD_GPIO, GPIO.OUT)

        # Set FAULT leg as high
        GPIO.setup(self.FAULT_GPIO, GPIO.OUT)
        GPIO.output(self.FAULT_GPIO, GPIO.HIGH)

        # arm wd
        self.wd_refresh_time = time.time() * self.store.MS_TO_SEC

    def run(self):
        while True:
            # Check if wd arm event was set
            if self.store.arm_wd_event.isSet():
                self._wd_refresh_timer()
                self.store.arm_wd_event.clear()

            # Check if wd timeout has passed 
            wd_diff = ((time.time() * self.store.MS_TO_SEC) - self.wd_refresh_time)
            if wd_diff < self.WD_TIMEOUT:
                self._arm_wd()

    def _arm_wd(self):
        GPIO.output(self.WD_GPIO, GPIO.HIGH)
        time.sleep(self.WD_REFRESH_SIGNAL_SEC)
        GPIO.output(self.WD_GPIO, GPIO.LOW)

    def _wd_refresh_timer(self):
    	self.wd_refresh_time = time.time() * self.store.MS_TO_SEC
