import RPi.GPIO as GPIO


class WdDriver(object):
    WD_REFRESH_HZ = 10.0
    WD_REFRESH_SIGNAL_SEC = (1 / WD_REFRESH_HZ)
    SYSTEM_FAULT_GPIO = 5
    MEDICAL_CONTITION_GPIO = 13
    FAULT_BUZZER_GPIO = 1

    def __init__(self):
        # Set System fault GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.SYSTEM_FAULT_GPIO, GPIO.OUT)

        # Set medical contition GPIO
        GPIO.setup(self.MEDICAL_CONTITION_GPIO, GPIO.OUT)
        GPIO.output(self.MEDICAL_CONTITION_GPIO, GPIO.HIGH)

		# Set buzzer GPIO
        GPIO.setup(self.FAULT_BUZZER_GPIO, GPIO.OUT)
        GPIO.output(self.FAULT_BUZZER_GPIO, GPIO.HIGH)

    def system_fault_led_on(self):
        GPIO.output(self.SYSTEM_FAULT_GPIO, GPIO.HIGH)

    def system_fault_led_off(self):
        GPIO.output(self.SYSTEM_FAULT_GPIO, GPIO.LOW)

    def medical_condition_led_on(self):
		GPIO.output(self.MEDICAL_CONTITION_GPIO, GPIO.HIGH)

    def medical_condition_led_off(self):
		GPIO.output(self.MEDICAL_CONTITION_GPIO, GPIO.LOW)

    def buzzer_off(self):
		GPIO.output(self.FAULT_BUZZER_GPIO, GPIO.LOW)

	def buzzer_on(self):
		GPIO.output(self.FAULT_BUZZER_GPIO, GPIO.LOW)
