import os
import platform

from cached_property import cached_property

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

class ThresholdButton(Button):
    def __init__(self, parent=NotImplemented, is_min=True, **kw):
        self.parent = parent
        self.is_min = is_min
        super(ThresholdButton, self).__init__(**kw)
        self.configure(bg="#2196F3", activebackground="#42A5F5", command=self.publish)
        self.subscribers = {}

    def toggle(self):
        if self.selected:
            self.deselect()

        else:
            self.select()

    @property
    def selected(self):
        return self["bg"] == "#FF9800"

    def select(self):
        self.configure(bg="#FF9800", activebackground="#FFA726")

    def deselect(self):
        self.configure(bg="#2196F3", activebackground="#42A5F5")

    def subscribe(self, object, callback):
        self.subscribers[object] = callback

    def unsubscribe(self):
        del self.subscribers[object]

    def publish(self):
        for callback in self.subscribers.values():
            callback(self)


class Section(object):
    INDEX = NotImplemented
    BG = NotImplemented

    def __init__(self, parent, root, store):
        self.parent = parent
        self.root = root
        self.store = store

        self.original_threshold = self.threshold.copy()

        self.frame = Frame(self.root, borderwidth=2, bg=self.BG)
        self.name_label = Label(master=self.frame)
        self.unit_label = Label(master=self.frame)
        self.max_button = ThresholdButton(master=self.frame, parent=self, is_min=False)
        self.minmax_divider = Label(master=self.frame, text="---",
                                    anchor="center", bg="#2196F3",
                                    foreground="blue")
        self.min_button = ThresholdButton(master=self.frame, parent=self, is_min=True)

        self.max_button.subscribe(self.parent, self.parent.on_threshold_button_click)
        self.min_button.subscribe(self.parent, self.parent.on_threshold_button_click)

    @property
    def threshold(self):
        raise NotImplementedError()

    def undo(self):
        self.threshold.load_from(self.original_threshold)

    def update(self):
        self.max_button.configure(text=self.threshold.max)
        self.min_button.configure(text=self.threshold.min)

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


class VTISection(Section):
    INDEX = 0
    BG = "indigo"

    @property
    def threshold(self):
        return self.store.vti_threshold

class MVISection(Section):
    INDEX = 1
    BG = "green"

    @property
    def threshold(self):
        return self.store.mvi_threshold

class PressureSection(Section):
    INDEX = 2
    BG = "orange"

    @property
    def threshold(self):
        return self.store.pressure_threshold

class RespRateSection(Section):
    INDEX = 3
    BG = "cyan"

    @property
    def threshold(self):
        return self.store.resp_rate_threshold


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
                                     compound="center",
                                     command=self.parent.on_up_button_click)

        self.down_button = ImageButton(master=self.frame,
                                       image_path=self.DOWN_IMAGE_PATH,
                                       compound="center",
                                       command=self.parent.on_down_button_click)

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
                                          activebackground="#66BB6A",
                                          command = self.parent.confirm)

        self.cancel_button = ImageButton(master=self.frame,
                                         image_path=self.CANCEL_IMAGE_PATH,
                                         compound="center",
                                         bg="#F44336",
                                         activebackground="#EF5350",
                                         command=self.parent.cancel)

    def render(self):
        self.frame.place(relx=0, rely=0.7, relheight=0.3, relwidth=1)
        self.confirm_button.place(relx=0, rely=0, relheight=1, relwidth=0.5)
        self.cancel_button.place(relx=0.5, rely=0, relheight=1, relwidth=0.5)


class ConfigureAlarmsScreen(object):
    def __init__(self, root, store):
        self.root = root
        self.store = store

        # Screen state
        self.selected_threshold = None
        self.is_min = None

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

    def on_threshold_button_click(self, button):
        is_min = button.is_min

        for irrelevant_button in (set(self.threshold_buttons) - {button}):
            irrelevant_button.deselect()

        # Toggle selected threshold
        if (self.selected_threshold, self.is_min) == (button.parent.threshold, is_min):
            self.selected_threshold = None
            self.is_min = False
            button.deselect()

        else:
            self.selected_threshold = button.parent.threshold
            self.is_min = is_min
            button.select()

    def on_up_button_click(self):
        if self.selected_threshold is None:  # Dummy-proof GUI
            return

        if self.is_min:
            self.selected_threshold.increase_min()

        else:
            self.selected_threshold.increase_max()

        for section in self.threshold_sections:
            section.update()


    def on_down_button_click(self):
        if self.selected_threshold is None:  # Dummy-proof GUI
            return

        if self.is_min:
            self.selected_threshold.decrease_min()

        else:
            self.selected_threshold.decrease_max()

        for section in self.threshold_sections:
            section.update()


    @cached_property
    def threshold_buttons(self):
        buttons = []
        for section in self.threshold_sections:
            buttons.append(section.min_button)
            buttons.append(section.max_button)

        return buttons

    @cached_property
    def threshold_sections(self):
        return (self.vti_section, self.mvi_section,
                self.pressure_section, self.resp_rate_section)

    @cached_property
    def sections(self):
        return (self.vti_section, self.mvi_section,
                self.up_or_down_section, self.pressure_section,
                self.resp_rate_section, self.confirm_cancel_section)

    def show(self):
        self.configure_alerts_screen.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)

        for section in self.sections:
            section.render()

    def hide(self):
        self.configure_alerts_screen.place_forget()

    def confirm(self):
        self.hide()

    def cancel(self):
        for section in self.threshold_sections:
            section.undo()

        self.hide()