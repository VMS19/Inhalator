# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from graphics.configure_alerts_screen import ConfigureAlarmsScreen


class OpenConfigureAlertsScreenButton(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store
        self.root = parent.element

        self.button = Button(master=self.root,
                             text="Configure Alerts",
                             command=self.on_click,
                             font=("Roboto", 25),
                             relief="flat",
                             bg="#3c3149", fg="#d7b1f9",
                             activebackground="#433850",
                             activeforeground="#e3e1e5",
                             )

    def on_click(self):
        master_frame = self.parent.parent.element
        screen = ConfigureAlarmsScreen(master_frame, self.store)
        screen.show()

    def render(self):
        self.button.place(relwidth=0.55, relheight=0.4, rely=0.1, relx=0.2835)

    def update(self):
        pass
