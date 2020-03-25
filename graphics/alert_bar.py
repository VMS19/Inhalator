# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from data import alerts
from data.data_store import AlertsQueue, DataStore


class IndicatorAlertBar(object):
    error_dict = {
        alerts.AlertCodes.PRESSURE_LOW: "LOW PIP",
        alerts.AlertCodes.PRESSURE_HIGH: "HIGH PIP",
        alerts.AlertCodes.BREATHING_VOLUME_LOW: "LOW Ve",
        alerts.AlertCodes.BREATHING_VOLUME_HIGH: "HIGH Ve"
    }

    def __init__(self, parent, store):
        self.parent = parent
        self.store = store  # type: DataStore
        self.root = parent.element

        self.height = self.parent.height
        self.width = self.parent.width

        self.bar = Frame(self.root, bg='green', height=self.height, width=self.width)
        self.message_label = Label(master=self.bar, font=("Courrier", 40),
                                   text="OK", bg='green', fg='black')

    @property
    def element(self):
        return self.bar

    def render(self):
        self.bar.place(relx=0, rely=0)
        self.message_label.place(anchor="nw", relx=0.03, rely=0.2)

    def update(self):
        last_alert_code = self.store.alerts_queue.last_alert.code
        if last_alert_code == alerts.AlertCodes.OK:
            self.set_no_alert()

        else:
            self.set_alert(self.error_dict[last_alert_code])

    def set_no_alert(self):
        self.bar.config(bg="green")
        self.message_label.config(bg="green", fg="black", text="OK")

    def set_alert(self, message):
        self.bar.config(bg="red")
        self.message_label.config(bg="red", fg="black", text=message)
