import time
import os

OS_RASPB = os.uname()[1] == 'raspberrypi'
if OS_RASPB:
    import RPi.GPIO as GPIO


class WdDriver(object):
    WD_SIGNAL_LEN = 0.05
    WD_GPIO = 18

    def __init__(self):
        if OS_RASPB:
            # Set WD GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.WD_GPIO, GPIO.OUT)

    if OS_RASPB:
        def arm_wd(self):
                GPIO.output(self.WD_GPIO, GPIO.HIGH)
                time.sleep(self.WD_SIGNAL_LEN)
                GPIO.output(self.WD_GPIO, GPIO.LOW)
    else:
        def arm_wd(self):
            pass
