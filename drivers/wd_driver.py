import time
from threading import Timer

import RPi.GPIO as GPIO


class WdDriver(object):
    WD_REFRESH_HZ = 2000
    WD_REFRESH_SIGNAL_SEC = (1 / WD_REFRESH_HZ)
    WD_GPIO = 5
    FAULT_GPIO = 19

    def __init__(self):
        # Set WD GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.WD_GPIO, GPIO.OUT)

        # Set FAULT leg as high
        GPIO.setup(self.FAULT_GPIO, GPIO.OUT)
        GPIO.output(self.FAULT_GPIO, GPIO.HIGH)
        self.refresh_delay_timer = Timer(self.WD_REFRESH_SIGNAL_SEC,
                                         self._pull_wd_down)

    def _pull_wd_up(self):
        GPIO.output(self.WD_GPIO, GPIO.HIGH)

    def _pull_wd_down(self):
        GPIO.output(self.WD_GPIO, GPIO.LOW)

    def arm_wd(self):
        self._pull_wd_up()
        self.refresh_delay_timer.start()
