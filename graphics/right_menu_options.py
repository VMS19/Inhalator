# Tkinter stuff
import platform

from graphics.configure_alerts_screen import ConfigureAlarmsScreen

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from graphics.themes import Theme


class ClearAlertsButton(object):
    def __init__(self, parent, events):
        self.parent = parent
        self.root = parent.element
        self.events = events

        self.button = Button(master=self.root,
                             command=self.on_click,
                             font=("Roboto", 10),
                             relief="flat",
                             bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
                             fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
                             activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
                             activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE,
                             text="Clear")

    def on_click(self):
        self.events.alerts_queue.clear_alerts()

    def render(self):
        self.button.place(relx=0, rely=0.01, relwidth=0.8, relheight=0.2)

    def update(self):
        pass


class MuteAlertsButton(object):
    def __init__(self, parent, events):
        self.parent = parent
        self.root = parent.element
        self.events = events

        self.button = Button(master=self.root,
                             command=self.on_click,
                             font=("Roboto", 10),
                             text="Mute",
                             relief="flat",
                             bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
                             fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
                             activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
                             activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE,)

    def on_click(self):
        print("Not Implemented Yet")

    def render(self):
        self.button.place(relx=0, rely=0.27, relwidth=0.8, relheight=0.2)

    def update(self):
        pass


class LockThresholdsButton(object):
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.element

        self.button = Button(master=self.root,
                             command=self.on_click,
                             text="Lock",relief="flat",
                             font=("Roboto", 10),
                             bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
                             fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
                             activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
                             activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE,)

    def on_click(self):
        print("Not Implemented Yet")

    def render(self):
        self.button.place(relx=0, rely=0.53, relwidth=0.8, relheight=0.2)

    def update(self):
        pass


class OpenConfigureAlertsScreenButton(object):
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.element

        self.button = Button(master=self.root,
                             text="Alerts",
                             command=self.on_click,
                             font=("Roboto", 10),
                             relief="flat",
                             bg="#3c3149", fg="#d7b1f9",
                             activebackground="#433850",
                             activeforeground="#e3e1e5",
                             )

    def on_click(self):
        master_frame = self.parent.parent.element
        screen = ConfigureAlarmsScreen(master_frame)
        screen.show()

    def render(self):
        self.button.place(relx=0, rely=0.79, relwidth=0.8, relheight=0.2)

    def update(self):
        pass
