from drivers.aux_sound import SoundViaAux
from data.alerts import AlertCodes

class AlertPeripheralHandler(object):

    def __init__(self, events, drivers):
        self.events = events
        self.drivers = drivers
        self.events.alerts_queue.pubsub.subscribe(self, self.on_new_alert)
        self.events.mute_alerts.pubsub.subscribe(self, self.on_mute)
        self.alert_driver = drivers.acquire_driver("alert")
        self.sound_device = drivers.acquire_driver("aux")

    def on_new_alert(self, alert):
        if alert != AlertCodes.OK:
            self.alert_driver.alert_medical_condition_on()
        else:
            self.alert_driver.alert_medical_condition_off()
            self.sound_device.stop()

    def on_mute(self, mute):
        if mute:
            self.alert_driver.alert_buzzer_off()
            self.sound_device.stop()
        elif self.events.alerts_queue.last_alert != AlertCodes.OK :
            self.alert_driver.alert_buzzer_on()
            self.sound_device.start()
