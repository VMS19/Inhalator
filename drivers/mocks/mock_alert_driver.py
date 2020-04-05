class MockAlertDriver(object):

    def __init__(self):
        pass

    def alert_system_fault_on(self):
        pass

    def alert_system_fault_off(self):
        pass

    def alert_medical_condition_on(self):
        print("medical_condition led on")
        self.alert_buzzer_on()
        pass

    def alert_medical_condition_off(self):
        print("medical_condition led off")
        self.alert_buzzer_off()
        pass

    def alert_buzzer_off(self):
        print("buzzer off")
        pass

    def alert_buzzer_on(self):
        print("buzzer on")
        pass

