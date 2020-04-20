import os

from data.alerts import AlertCodes
from graphics.alerts_history_screen import AlertsHistoryScreen
from graphics.configure_alerts_screen import ConfigureAlarmsScreen
from graphics.imagebutton import ImageButton

# from tkinter import *

from graphics.themes import Theme

THIS_DIRECTORY = os.path.dirname(__file__)
RESOURCES_DIRECTORY = os.path.join(os.path.dirname(THIS_DIRECTORY), "resources")


class ClearAlertsButton(object):
    IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY,
                              "baseline_history_white_48dp.png")

    def __init__(self, parent, events):
        self.parent = parent
        self.root = parent.element
        self.events = events
        self.button = ImageButton(
            master=self.root,
            image_path=self.IMAGE_PATH,
            command=self.on_click,
            font=("Roboto", 9),
            text="Clear",
            pady=10,
            compound="top",
            state="disabled",
            relief="flat",
            bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
            fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
        )

        self.events.alerts_queue.observer.subscribe(self, self.on_alert)

    def on_alert(self, alert):
        if alert == AlertCodes.OK:
            self.button.configure(
                state="disabled",
            )

        else:
            self.button.configure(
                state="normal",
            )

    def on_click(self):
        self.events.alerts_queue.clear_alerts()

    def render(self):
        self.button.place(relx=0, rely=0.01, relwidth=1, relheight=0.2)

    def update(self):
        pass


class MuteAlertsButton(object):

    PATH_TO_MUTED = os.path.join(
        RESOURCES_DIRECTORY,
        "round_notifications_off_white_48dp.png")
    PATH_TO_UNMUTED = os.path.join(
        RESOURCES_DIRECTORY,
        "baseline_notifications_active_white_48dp.png")

    def __init__(self, parent, events):
        self.parent = parent
        self.root = parent.element
        self.events = events
        self.muted = False

        self.button = ImageButton(
            master=self.root,
            image_path=self.PATH_TO_UNMUTED,
            command=self.on_click,
            font=("Roboto", 9),
            relief="flat",
            text="Mute",
            pady=10,
            compound="top",
            bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
            fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
            activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
            activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE,
        )

    def on_click(self):
        self.events.mute_alerts.mute_alerts()
        self.update()

    def render(self):
        self.button.place(relx=0, rely=0.27, relwidth=1, relheight=0.2)

    def update(self):
        if self.events.mute_alerts._alerts_muted:
            self.button.set_image(self.PATH_TO_MUTED)
            self.button.configure(text="Unmute")

        else:
            self.button.set_image(self.PATH_TO_UNMUTED)
            self.button.configure(text="Mute")


class LockThresholdsButton(object):
    IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY,
                              "baseline_lock_open_white_48dp.png")

    def __init__(self, parent):
        self.parent = parent
        self.root = parent.element

        self.button = ImageButton(
            master=self.root,
            image_path=self.IMAGE_PATH,
            command=self.on_click,
            text="Lock",
            relief="flat",
            font=("Roboto", 9),
            bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
            fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
            activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
            activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE,
            state="disabled"
        )

    def on_click(self):
        raise NotImplementedError

    def render(self):
        self.button.place(relx=0, rely=0.53, relwidth=1, relheight=0.2)

    def update(self):
        pass


class OpenConfigureAlertsScreenButton(object):
    IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY,
                              "baseline_settings_white_48dp.png")

    def __init__(self, parent, drivers, observer):
        self.parent = parent
        self.root = parent.element
        self.drivers = drivers
        self.observer = observer

        self.button = ImageButton(
            master=self.root,
            image_path=self.IMAGE_PATH,
            command=self.on_click,
            font=("Roboto", 9),
            relief="flat",
            text="Settings",
            pady=11,
            compound="top",
            bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
            fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
            activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
            activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE,
        )

    def on_click(self):
        master_frame = self.parent.parent.element
        screen = ConfigureAlarmsScreen(master_frame,
                                       drivers=self.drivers,
                                       observer=self.observer)
        screen.show()

    def render(self):
        self.button.place(relx=0, rely=0.79, relwidth=1, relheight=0.2)

    def update(self):
        pass


class OpenAlertsHistoryScreenButton(object):
    PATH_TO_HISTORY = os.path.join(RESOURCES_DIRECTORY,
                                   "baseline_history_white_24dp.png")

    def __init__(self, parent, events):
        self.parent = parent
        self.root = parent.element
        self.events = events

        self.button = ImageButton(
            master=self.root,
            image_path=self.PATH_TO_HISTORY,
            command=self.on_click,
            font=("Roboto", 9),
            relief="flat",
            bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
            fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
            activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
            activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE,
        )

    def on_click(self):
        master_frame = self.parent.parent.element
        screen = AlertsHistoryScreen(master_frame, events=self.events)
        screen.show()

    def render(self):
        self.button.place(relx=0, rely=0.79, relwidth=1, relheight=0.2)

    def update(self):
        pass
