class MockAlertDriver(object):

    def __init__(self):
        pass

    def set_system_fault_alert(self, value: bool):
        self.set_buzzer(value)

    def set_medical_condition_alert(self, value: bool):
        self.set_buzzer(value)

    def set_buzzer(self, value: bool):
        pass