from data.alerts import AlertCodes


class AlertPeripheralHandler(object):

    def __init__(self, events, drivers):
        self.events = events
        self.alert_driver = drivers.acquire_driver("alert")

    def subscribe(self):
        self.events.alerts_queue.observer.subscribe(self, self.on_new_alert)
        self.events.mute_alerts.observer.subscribe(self, self.on_mute)

    def on_new_alert(self, alert):
        if alert.is_medical_condition():
            self.alert_driver.set_medical_condition_alert(
                not alert.is_medical_condition(),
                self.events.mute_alerts._alerts_muted)
        elif alert.is_system_alert():
            self.alert_driver.set_system_fault_alert(
                not alert.is_system_alert(),
                self.events.mute_alerts._alerts_muted)
        else:
            self.alert_driver.set_medical_condition_alert(
                not alert.is_medical_condition(),
                self.events.mute_alerts._alerts_muted)
            self.alert_driver.set_system_fault_alert(
                not alert.is_system_alert(),
                self.events.mute_alerts._alerts_muted)

    def on_mute(self, mute):
        self.alert_driver.set_buzzer(
            mute or
            self.events.alerts_queue.last_alert == AlertCodes.OK)
