from data.alerts import AlertCodes


class AlertPeripheralHandler(object):

    def __init__(self, events, drivers):
        self.events = events
        self.alert_driver = drivers.acquire_driver("alert")

    def subscribe(self):
        self.events.alerts_queue.observer.subscribe(self, self.on_new_alert)
        self.events.mute_alerts.observer.subscribe(self, self.on_mute)

    def on_new_alert(self, alert):
        self.alert_driver.set_medical_condition_alert(
            alert == AlertCodes.OK or alert >= AlertCodes.SYSTEM_ALERT_OFFSET,
            self.events.mute_alerts._alerts_muted)

    def on_mute(self, mute):
        self.alert_driver.set_buzzer(
            mute or
            self.events.alerts_queue.last_alert == AlertCodes.OK or
            self.events.alerts_queue.last_alert >= AlertCodes.SYSTEM_ALERT_OFFSET)
