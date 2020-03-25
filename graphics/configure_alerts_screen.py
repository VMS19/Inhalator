import os
import platform

# Tkinter stuff
if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from data.thresholds import (MViThreshold, PresThreshold,
                             RespiratoryRateThreshold, VtiThreshold)

from graphics.imagebutton import ImageButton

THIS_FILE = __file__
THIS_DIRECTORY = os.path.dirname(THIS_FILE)
RESOURCES_DIRECTORY = os.path.join(os.path.dirname(THIS_DIRECTORY), "resources")


class ThresholdAlarmSection(object):
    INDEX = NotImplemented
    BG = NotImplemented
    THRESHOLD = NotImplemented

    def __init__(self, parent, root, store):
        self.parent = parent
        self.root = root
        self.store = store
        self.threshold = self.THRESHOLD  # TODO: Get from store

        self.frame = Frame(self.root, borderwidth=2, bg=self.BG)
        self.name_label = Label(master=self.frame)
        self.unit_label = Label(master=self.frame)
        self.max_button = Button(master=self.frame)
        self.minmax_divider = Label(master=self.frame, text="---", anchor="center")
        self.min_button = Button(master=self.frame)

    def render(self):
        self.frame.place(relx=(0.2) * self.INDEX,
                         rely=0, relwidth=0.2, relheight=0.7)
        self.name_label.place(relx=0, rely=0, relwidth=1, relheight=0.17)
        self.unit_label.place(relx=0, rely=0.17, relwidth=1, relheight=0.08)
        self.max_button.place(relx=0, rely=0.25, relwidth=1, relheight=0.25)
        self.minmax_divider.place(relx=0, rely=0.5, relwidth=1, relheight=0.25)
        self.min_button.place(relx=0, rely=0.75, relwidth=1, relheight=0.25)

        self.name_label.configure(text=self.threshold.NAME)
        self.unit_label.configure(text=self.threshold.UNIT)
        self.max_button.configure(text=self.threshold.max)
        self.min_button.configure(text=self.threshold.min)


class VTISection(ThresholdAlarmSection):
    INDEX = 0
    BG = "indigo"
    THRESHOLD = VtiThreshold(0, 0)


class MVISection(ThresholdAlarmSection):
    INDEX = 1
    BG = "green"
    THRESHOLD = MViThreshold(0, 0)


class PressureSection(ThresholdAlarmSection):
    INDEX = 2
    BG = "orange"
    THRESHOLD = PresThreshold(0, 0)


class RespRateSection(ThresholdAlarmSection):
    INDEX = 3
    BG = "cyan"
    THRESHOLD = RespiratoryRateThreshold(0, 0)


class UpOrDownSection(object):
    DOWN_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_less_black_18dp.png")
    UP_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_more_black_18dp.png")

    def __init__(self, parent, root, store):
        self.parent = parent
        self.root = root
        self.store = store

        self.frame = Frame(master=root, bg="gold")
        self.up_button = ImageButton(master=self.frame,
                                     image_path=self.UP_IMAGE_PATH,
                                     compound="center")

        self.down_button = ImageButton(master=self.frame,
                                       image_path=self.DOWN_IMAGE_PATH,
                                       compound="center")

    def render(self):
        self.frame.place(relx=0.8, rely=0, relwidth=0.2, relheight=0.7)
        self.up_button.place(relx=0, rely=0, relwidth=1, relheight=0.5)
        self.down_button.place(relx=0, rely=0.5, relwidth=1, relheight=0.5)


class ConfirmCancelSection(object):
    CONFIRM_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_done_black_18dp.png")
    CANCEL_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_cancel_black_18dp.png")

    def __init__(self, parent, root, store):
        self.parent = parent
        self.root = root
        self.store = store

        self.frame = Frame(root, bg="gray")
        self.confirm_button = ImageButton(master=self.frame,
                                          image_path=self.CONFIRM_IMAGE_PATH,
                                          compound="center",
                                          bg="#4CAF50",
                                          activebackground="#66BB6A")

        self.cancel_button = ImageButton(master=self.frame,
                                         image_path=self.CANCEL_IMAGE_PATH,
                                         compound="center",
                                         bg="#F44336",
                                         activebackground="#EF5350")

    def render(self):
        self.frame.place(relx=0, rely=0.7, relheight=0.3, relwidth=1)
        self.confirm_button.place(relx=0, rely=0, relheight=1, relwidth=0.5)
        self.cancel_button.place(relx=0.5, rely=0, relheight=1, relwidth=0.5)


class ConfigureAlarmsScreen(object):
    def __init__(self, root, store):
        self.root = root
        self.store = store

        self.configure_alerts_screen = Frame(master=self.root, bg="purple")

        # Sections
        self.vti_section = VTISection(self, self.configure_alerts_screen, self.store)
        self.mvi_section = MVISection(self, self.configure_alerts_screen, self.store)
        self.pressure_section = PressureSection(self, self.configure_alerts_screen,
                                                self.store)
        self.resp_rate_section = RespRateSection(self, self.configure_alerts_screen,
                                                 self.store)

        self.up_or_down_section = UpOrDownSection(self, self.configure_alerts_screen, store)
        self.confirm_cancel_section = ConfirmCancelSection(self, self.configure_alerts_screen, self.store)

    @property
    def sections(self):
        return (self.vti_section, self.mvi_section,
                self.up_or_down_section, self.pressure_section,
                self.resp_rate_section, self.confirm_cancel_section)

    def show(self):
        self.configure_alerts_screen.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)

        for section in self.sections:
            section.render()

    def hide(self):
        pass
