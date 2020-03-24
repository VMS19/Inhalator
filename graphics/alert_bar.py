from alerts import alerts

# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

import alerts

class IndicatorAlertBar(object):
    error_dict = {
        alerts.alerts.PRESSURE_LOW: "PRESSURE LOW",
        alerts.alerts.PRESSURE_HIGH: "PERSSURE HIGH",
        alerts.alerts.BREATHING_VOLUME_LOW: "BREATHING VOLUME LOW",
        alerts.alerts.BREATHING_VOLUME_HIGH: "BREATHING VOLUME HIGH"
    }

    def __init__(self, parent, store):
        self.parent = parent
        self.store = store
        self.root = parent.element

        self.height = self.parent.height
        self.width = self.parent.width

        self.bar = Frame(self.root, bg='green', height=self.height, width=self.width)
        self.message_label = Label(master=self.bar, font=("Courrier", 40),
                                   text="OK", bg='green', fg='black')
        self.current_alert = alerts.alerts.OK

    @property
    def element(self):
        return self.bar

    def render(self):
        self.bar.place(relx=0, rely=0)
        self.message_label.place(anchor="nw")

    def update(self):
        if self.store.alerts.empty():
            return

        cur_alert = self.store.alerts.get()
        if cur_alert == alerts.alerts.OK:
            self.set_no_alert()

        else:
            self.set_alert(self.error_dict[cur_alert[0]])

    def set_no_alert(self):
        self.bar.config(bg="green")
        self.message_label.config(bg="green", fg="black", text="OK")

    def set_alert(self, message):
        self.bar.config(bg="red")
        self.message_label.config(bg="red", fg="black", text=message)
