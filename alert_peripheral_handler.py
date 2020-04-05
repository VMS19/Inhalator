from drivers.aux_sound import SoundViaAux
from data.alerts import AlertCodes

class AlertPeripheralHandler(object):

    def __init__(self, events, drivers):
        self.events = events
        self.drivers = drivers
        self.events.alerts_queue.observer.subscribe(self, self.on_new_alert)
        self.events.mute_alerts.observer.subscribe(self, self.on_mute)
        self.alert_driver = drivers.acquire_driver("alert")

    def on_new_alert(self, alert):
        self.alert_driver.set_medical_condition_alert(alert != AlertCodes.OK)

    def on_mute(self, mute):
        self.alert_driver.set_system_fault_alert(
            not (mute or self.events.alerts_queue.last_alert != AlertCodes.OK))
