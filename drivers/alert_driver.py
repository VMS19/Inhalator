import RPi.GPIO as GPIO


class AlertDriver(object):
    SYSTEM_FAULT_GPIO = 20
    MEDICAL_CONTITION_GPIO = 19
    FAULT_BUZZER_GPIO = 13
    WD_GPIO = 26
    LED_GREEN = GPIO.HIGH
    LED_RED = GPIO.LOW

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        # Set System fault GPIO
        GPIO.setup(self.SYSTEM_FAULT_GPIO, GPIO.OUT)
        GPIO.output(self.SYSTEM_FAULT_GPIO, self.LED_GREEN)

        # Set medical contition GPIO
        GPIO.setup(self.MEDICAL_CONTITION_GPIO, GPIO.OUT)
        GPIO.output(self.MEDICAL_CONTITION_GPIO, self.LED_GREEN)

        # Set buzzer GPIO
        GPIO.setup(self.FAULT_BUZZER_GPIO, GPIO.OUT)
        GPIO.output(self.FAULT_BUZZER_GPIO, GPIO.HIGH)

        # Set wd GPIO
        GPIO.setup(self.WD_GPIO, GPIO.OUT)
        GPIO.output(self.WD_GPIO, self.LED_GREEN)

    def set_system_fault_alert(self, value: bool, mute: bool):
        led = self.LED_GREEN
        if not value:
            led = self.LED_RED

        GPIO.output(self.SYSTEM_FAULT_GPIO, led)
        self.set_buzzer(value or mute)

    def set_medical_condition_alert(self, value: bool, mute: bool):
        led = self.LED_GREEN
        if not value:
            led = self.LED_RED

        GPIO.output(self.MEDICAL_CONTITION_GPIO, led)
        self.set_buzzer(value or mute)

    def set_buzzer(self, value: bool):
        gpio_state = GPIO.HIGH
        if not value:
            gpio_state = GPIO.LOW

        GPIO.output(self.FAULT_BUZZER_GPIO, gpio_state)
