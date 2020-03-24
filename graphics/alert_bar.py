from alerts import alerts

# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from alerts import alerts

class IndicatorAlertBar(object):
    error_dict = {
        alerts.alerts.PRESSURE_LOW: (
        "Pressure ({}mbar) dropped below healthy lungs pressure ({}mbar)", self.store.pressure_min_threshold),
        alerts.alerts.PRESSURE_HIGH: (
        "Pressure ({}mbar) exceeded healthy lungs pressure ({}mbar)", self.store.pressure_max_threshold),
        alerts.alerts.BREATHING_VOLUME_LOW: (
        "Breathing Volume ({}ltr) went under minimum threshold ({}ltr)", self.store.flow_min_threshold),
        alerts.alerts.BREATHING_VOLUME_HIGH: (
        "Breathing Volume ({}ltr) exceeded maximum threshold ({}ltr)", self.store.flow_max_threshold)
    }

    def __init__(self, parent, store):
        self.parent = parent
        self.store = store
        self.root = parent.element

        self.height = self.parent.height
        self.width = self.parent.width

        self.bar = Frame(self.root, bg='green', height=self.height, width=self.width)
        self.current_alert = alerts.OK

    @property
    def element(self):
        return self.bar

    def render(self):
        self.bar.place(relx=0, rely=0)

    def update(self):
        if self.store.alerts.empty():
            return

        cur_alert = self.store.alerts.get()
        alert_format = self.error_dict[cur_alert[0]]
        self.alert(alert_format[0].format(cur_alert[1], alert_format[1]))

    def set_no_alert(self):
        pass

    def set_alert(self, alert):
        pass