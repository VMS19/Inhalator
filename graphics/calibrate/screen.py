import math
import statistics
from tkinter import *

from data.configurations import Configurations
from graphics.themes import Theme


class Title(object):
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root
        self.frame = Frame(master=self.root)
        self.label = Label(master=self.frame,
                           text="Flow Calibration",
                           font=("Roboto", 20),
                           bg=Theme.active().BACKGROUND,
                           fg=Theme.active().TXT_ON_BG)

    def render(self):
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=0.25)
        self.label.place(relx=0, rely=0, relheight=1, relwidth=1)


class Calibration(object):
    NUMBER_OF_SAMPLES_TO_TAKE = 100
    SLEEP_IN_BETWEEN = 1 / 20

    def __init__(self, parent, root, drivers):
        self.parent = parent
        self.root = root

        self.dp_driver = drivers.acquire_driver("differential_pressure")
        self.timer = drivers.acquire_driver("timer")
        self.watch_dog = drivers.acquire_driver("wd")

        self.frame = Frame(master=self.root)
        self.label = Label(master=self.frame,
                           text="Please make sure airflow is not connected!",
                           font=("Roboto", 16),
                           bg=Theme.active().BACKGROUND,
                           fg=Theme.active().TXT_ON_BG)

        self.button = Button(master=self.frame,
                             bg=Theme.active().SURFACE,
                             command=self.calibrate,
                             fg=Theme.active().TXT_ON_SURFACE,
                             text="Calibrate")

        # State
        self.average_value_found = None

    @property
    def waiting_time(self):
        return

    def calibrate(self):
        # TODO: Handle watchdog

        values = []

        # Read values from sensor
        for index in range(self.NUMBER_OF_SAMPLES_TO_TAKE):
            # Inform User
            waiting_time_left = ((self.NUMBER_OF_SAMPLES_TO_TAKE - index ) *
                                 self.SLEEP_IN_BETWEEN)

            self.label.configure(
                text=f"Please wait {math.ceil(waiting_time_left)} seconds...")
            self.button.configure(state="disabled")

            self.label.update()  # This is needed so the GUI doesn't freeze

            values.append(self.dp_driver.read_differential_pressure())

            self.timer.sleep(self.SLEEP_IN_BETWEEN)

        self.average_value_found = statistics.mean(values) + -0.026
        self.label.configure(text=f"Offset found: {self.average_value_found}")
        self.button.configure(state="normal")

    def render(self):
        self.frame.place(relx=0, rely=0.25, relwidth=1, relheight=0.5)
        self.label.place(relx=0, rely=0, relheight=0.5, relwidth=1)
        self.button.place(relx=0, rely=0.5, relheight=0.5, relwidth=1)

    def save(self):
        Configurations.instance().dp_offset = self.average_value_found


class OKCancelSection(object):
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root
        self.frame = Frame(master=self.root, bg=Theme.active().BACKGROUND)
        self.ok_button = Button(master=self.frame,
                                command=self.parent.on_ok,
                                bg=Theme.active().SURFACE,
                                fg=Theme.active().TXT_ON_SURFACE,
                                text="OK")
        self.cancel_button = Button(master=self.frame,
                                    bg=Theme.active().SURFACE,
                                    command=self.parent.on_cancel,
                                    fg=Theme.active().TXT_ON_SURFACE,
                                    text="Cancel")

    def render(self):
        self.frame.place(relx=0, rely=0.75, relwidth=1, relheight=0.25)
        self.ok_button.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        self.cancel_button.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)



class FlowCalibrationScreen(object):
    def __init__(self, root, measurements, drivers):
        self.root = root
        self.measurements = measurements

        self.screen = Frame(master=self.root, bg="red")
        self.title = Title(self, self.screen)
        self.calibration = Calibration(self, self.screen, drivers)
        self.ok_cancel_section = OKCancelSection(self, self.screen)

    def show(self):
        self.screen.place(relx=0.1, rely=0.15, relheight=0.7, relwidth=0.8)
        self.title.render()
        self.calibration.render()
        self.ok_cancel_section.render()

    def hide(self):
        self.screen.place_forget()

    def on_ok(self):
        self.calibration.save()
        self.hide()

    def on_cancel(self):
        self.hide()

