class MockAlertDriver(object):

    def set_system_fault_alert(self, value: bool):
        self.set_buzzer(value)

    def set_medical_condition_alert(self, value: bool):
        self.set_buzzer(value)

    def set_buzzer(self, value: bool):
        pass