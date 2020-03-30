# Tkinter stuff
import os
import platform

import time
from graphics.configure_alerts_screen import ConfigureAlarmsScreen
from graphics.imagebutton import ImageButton
import drivers.abp_pressure_sensor

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from graphics.themes import Theme

THIS_DIRECTORY = os.path.dirname(__file__)
RESOURCES_DIRECTORY = os.path.join(os.path.dirname(THIS_DIRECTORY), "resources")


THIS_DIRECTORY = os.path.dirname(__file__)
RESOURCES_DIRECTORY = os.path.join(os.path.dirname(THIS_DIRECTORY), "resources")


class ClearAlertsButton(object):

    PATH_TO_IMAGE = os.path.join(RESOURCES_DIRECTORY,
                                 "baseline_delete_forever_white_24dp.png")

    def __init__(self, parent, events):
        self.parent = parent
        self.root = parent.element
        self.events = events
        self.button = ImageButton(master=self.root,
                             command=self.on_click,
                             font=("Roboto", 10),
                             relief="flat",
                             bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
                             fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
                             activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
                             activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE,
                             image_path=self.PATH_TO_IMAGE)

    def on_click(self):
        self.events.alerts_queue.clear_alerts()

    def render(self):
        self.button.place(relx=0, rely=0.01, relwidth=0.8, relheight=0.2)

    def update(self):
        pass


class MuteAlertsButton(object):

    PATH_TO_MUTED = os.path.join(RESOURCES_DIRECTORY,
                                 "baseline_volume_off_white_24dp.png")
    PATH_TO_UNMUTED = os.path.join(RESOURCES_DIRECTORY,
                                   "baseline_volume_up_white_24dp.png")

    def __init__(self, parent, events):
        self.parent = parent
        self.root = parent.element
        self.events = events
        self.muted = False

        self.button = ImageButton(master=self.root,
                                  command=self.on_click,
                                  font=("Roboto", 10),
                                  image_path=self.PATH_TO_UNMUTED,
                                  relief="flat",
                                  bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
                                  fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
                                  activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
                                  activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE,)

    def on_click(self):
        self.events.mute_alerts = not self.events.mute_alerts
        if self.events.mute_alerts:
            self.events.mute_time = time.time()

        self.update()

    def render(self):
        self.button.place(relx=0, rely=0.27, relwidth=0.8, relheight=0.2)

    def update(self):
        if self.events.mute_alerts:
            self.button.set_image(self.PATH_TO_MUTED)

        else:
            self.button.set_image(self.PATH_TO_UNMUTED)


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
                             bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
                             fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
                             activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
                             activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE,
        )

    def on_click(self):
        master_frame = self.parent.parent.element
        screen = ConfigureAlarmsScreen(master_frame)
        screen.show()

    def render(self):
        self.button.place(relx=0, rely=0.79, relwidth=0.8, relheight=0.2)

    def update(self):
        pass


class StuckButton(object):
    def __init__(self, parent):
        self.parent = parent
        self.root = parent.element

        self.button = Button(master=self.root,
                             text="STUCK",
                             command=self.on_click,
                             font=("Roboto", 10),
                             relief="flat",
                             bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
                             fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
                             activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
                             activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE,
        )

    def on_click(self):
        drivers.abp_pressure_sensor.STUCK = True

    def render(self):
        self.button.place(relx=0, rely=0.99, relwidth=0.8, relheight=0.2)

    def update(self):
        pass

