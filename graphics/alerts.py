from alerts import alerts

# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

class IndicatorAlertBar(object):
    def __init__(self, parent):
        self.parent = parent
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
        pass

    def set_no_alert(self):
        pass

    def set_alert(self, alert):
        pass