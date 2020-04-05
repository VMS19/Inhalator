import RPi.GPIO as GPIO


class AlertDriver(object):
    SYSTEM_FAULT_GPIO = 26
    MEDICAL_CONTITION_GPIO = 19
    FAULT_BUZZER_GPIO = 13
    RESERVED_GPIO = 20
    LED_GREEN = GPIO.LOW
    LED_RED = GPIO.HIGH


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

        # Set reserved GPIO
        GPIO.setup(self.RESERVED_GPIO, GPIO.OUT)
        GPIO.output(self.RESERVED_GPIO, self.LED_GREEN)

    def alert_system_fault_on(self):
        self.alert_buzzer_on()
        GPIO.output(self.SYSTEM_FAULT_GPIO, self.LED_RED)

    def alert_system_fault_off(self):
        self.alert_buzzer_off()
        GPIO.output(self.SYSTEM_FAULT_GPIO, self.LED_GREEN)

    def alert_medical_condition_on(self):
        self.alert_buzzer_on()
        GPIO.output(self.MEDICAL_CONTITION_GPIO, self.LED_RED)

    def alert_medical_condition_off(self):
        self.alert_buzzer_off()
        GPIO.output(self.MEDICAL_CONTITION_GPIO, self.LED_GREEN)

    def alert_buzzer_on(self):
        GPIO.output(self.FAULT_BUZZER_GPIO, GPIO.LOW)

    def alert_buzzer_off(self):
        GPIO.output(self.FAULT_BUZZER_GPIO, GPIO.HIGH)
