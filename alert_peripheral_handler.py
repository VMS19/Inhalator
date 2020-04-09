from data.alert import AlertCodes


class AlertPeripheralHandler(object):

    def __init__(self, events, drivers):
        self.events = events
        self.alert_driver = drivers.acquire_driver("alert")

    def subscribe(self):
        self.events.alert_queue.observable.subscribe(self, self.on_new_alert)
        self.events.mute_controller.observable.subscribe(self, self.on_mute)

    def on_new_alert(self, alert):
        alerts_muted = self.events.mute_controller._alerts_muted

        self.alert_driver.set_medical_condition_alert(
            not alert.is_medical_condition(),
            alerts_muted)

        self.alert_driver.set_system_fault_alert(
            not alert.is_system_alert(),
            alerts_muted)

    def on_mute(self, mute):
        self.alert_driver.set_buzzer(
            mute or
            self.events.alert_queue.last_alert == AlertCodes.OK)
