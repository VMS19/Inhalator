import RPi.GPIO as GPIO


class LED(object):
    LED1 = 19
    LED2 = 20

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

    def _led(self, gpio, on):
        GPIO.setup(gpio, GPIO.OUT)
        if on:
            GPIO.output(gpio, GPIO.HIGH)
        else:
            GPIO.output(gpio, GPIO.LOW)

    def led1(self, on):
        self._led(self.LED1, on)

    def led2(self, on):
        self._led(self.LED2, on)
