import math
import statistics
from tkinter import *

from data.configurations import Configurations
from graphics.themes import Theme
from errors import InvalidCalibrationError


class Calibration(object):
    CALIBRATED_DRIVER = NotImplemented
    PRE_CALIBRATE_ALERT_MSG = NotImplemented
    NUMBER_OF_SAMPLES_TO_TAKE = 100
    SAMPLING_TIME = 3  # seconds
    SLEEP_IN_BETWEEN = SAMPLING_TIME / 100

    def __init__(self, parent, root, drivers):
        self.parent = parent
        self.root = root
        self.config = Configurations.instance()

        # State
        self.average_value_found = None

        self.drivers = drivers
        self.sensor_driver = drivers.acquire_driver(self.CALIBRATED_DRIVER)
        self.timer = drivers.acquire_driver("timer")
        self.watch_dog = drivers.acquire_driver("wd")

        self.frame = Frame(master=self.root)
        self.label = Label(master=self.frame,
                           text=self.PRE_CALIBRATE_ALERT_MSG,
                           font=("Roboto", 16),
                           justify="center",
                           bg=Theme.active().BACKGROUND,
                           fg=Theme.active().TXT_ON_BG)

        self.calibration_buttons = []
        self.create_calibration_menu()

    def create_calibration_menu(self):
        button = Button(master=self.frame,
                             bg=Theme.active().SURFACE,
                             command=self.calibrate,
                             fg=Theme.active().TXT_ON_SURFACE,
                             text="Calibrate")
        self.calibration_buttons = [button]

    def read_raw_value(self):
        raise NotImplemented

    def get_difference(self):
        """Get offset drift."""
        raise NotImplemented

    def configure_new_calibration(self):
        raise NotImplemented

    def save(self):
        try:
            self.configure_new_calibration()
        except InvalidCalibrationError as err:
            self.label.config(text=str(err))
            return False
        else:
            self.config.save_to_file()
            return True

    def calibrate(self):
        # TODO: Handle watchdog

        values = []

        # Read values from sensor
        for index in range(self.NUMBER_OF_SAMPLES_TO_TAKE):
            # Inform User
            waiting_time_left = ((self.NUMBER_OF_SAMPLES_TO_TAKE - index) *
                                 self.SLEEP_IN_BETWEEN)

            self.label.configure(
                text=f"Please wait {math.ceil(waiting_time_left)} seconds...")

            for btn in self.calibration_buttons:
                btn.configure(state="disabled")

            self.label.update()  # This is needed so the GUI doesn't freeze

            values.append(self.read_raw_value())

            self.timer.sleep(self.SLEEP_IN_BETWEEN)

        self.average_value_found = statistics.mean(values)
        self.label.configure(
            text=f"Offset change found: {self.get_difference():.2f}")

        self.parent.enable_ok_button()
        for btn in self.calibration_buttons:
            btn.configure(state="normal")

    def render(self):
        self.frame.place(relx=0, rely=0.25, relwidth=1, relheight=0.5)
        self.label.place(relx=0, rely=0, relheight=0.5, relwidth=1)
        calibration_button_width = 1 / len(self.calibration_buttons)
        for i, btn in enumerate(self.calibration_buttons):
            btn.place(relx=i*calibration_button_width,
                      rely=0.5, relheight=0.5,
                      relwidth=calibration_button_width)


class OKCancelSection(object):
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root
        self.frame = Frame(master=self.root, bg=Theme.active().BACKGROUND)
        self.ok_button = Button(master=self.frame,
                                command=self.parent.on_ok,
                                bg=Theme.active().SURFACE,
                                fg=Theme.active().TXT_ON_SURFACE,
                                state="disabled",
                                text="Set")
        self.cancel_button = Button(master=self.frame,
                                    bg=Theme.active().SURFACE,
                                    command=self.parent.on_cancel,
                                    fg=Theme.active().TXT_ON_SURFACE,
                                    text="Cancel")

    def render(self):
        self.frame.place(relx=0, rely=0.75, relwidth=1, relheight=0.25)
        self.ok_button.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        self.cancel_button.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

    def enable_ok_button(self):
        self.ok_button.configure(state="normal")


class Title(object):
    def __init__(self, parent, root, title_str):
        self.parent = parent
        self.root = root
        self.frame = Frame(master=self.root)
        self.label = Label(master=self.frame,
                           text=title_str,
                           font=("Roboto", 20),
                           bg=Theme.active().BACKGROUND,
                           fg=Theme.active().TXT_ON_BG)

    def render(self):
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=0.25)
        self.label.place(relx=0, rely=0, relheight=1, relwidth=1)


class CalibrationScreen(object):
    def __init__(self, root, calibration_class, drivers):
        self.root = root
        self.calibration_class = calibration_class

        self.screen = Frame(master=self.root, bg="red")
        self.calibration = self.calibration_class(self, self.screen, drivers)
        self.title = Title(self, self.screen, self.calibration.NAME)
        self.ok_cancel_section = OKCancelSection(self, self.screen)

    def show(self):
        self.screen.place(relx=0.1, rely=0.15, relheight=0.7, relwidth=0.8)
        self.title.render()
        self.calibration.render()
        self.ok_cancel_section.render()

    def hide(self):
        self.screen.place_forget()

    def enable_ok_button(self):
        self.ok_cancel_section.enable_ok_button()

    def on_ok(self):
        if self.calibration.save():
            self.hide()

    def on_cancel(self):
        self.hide()


class DifferentialPressureCalibration(Calibration):
    NAME = "Flow Calibration"
    CALIBRATED_DRIVER = "differential_pressure"
    PRE_CALIBRATE_ALERT_MSG = (
        "Please make sure\n"
        "tubes are detached from sensor!")

    def read_raw_value(self):
        return self.sensor_driver.read_differential_pressure()

    def get_difference(self):
        """Get offset drift."""
        offset = self.average_value_found - Configurations.instance().dp_offset
        return self.drivers.acquire_driver("differential_pressure").pressure_to_flow(offset)

    def configure_new_calibration(self):
        self.config.dp_offset = self.average_value_found
        self.sensor_driver.set_calibration_offset(self.average_value_found)


class OxygenCalibration(Calibration):
    NAME = "O2 Calibration"
    CALIBRATED_DRIVER = "a2d"
    SAMPLING_TIME = 5  # seconds
    PRE_CALIBRATE_ALERT_MSG = (
        "Please make sure\n"
        "For 21% - detach oxygen tube\n"
        "For 100% - feed 100% oxygen")
    STEP_2_CALIBRATION_PERCENTAGE = 100

    def __init__(self, *args):
        self.calibrated_point = None
        super().__init__(*args)

    def create_calibration_menu(self):
        self.calibrate_point1_button = Button(master=self.frame,
            bg=Theme.active().SURFACE,
            command=self.calibrate_point1,
            fg=Theme.active().TXT_ON_SURFACE,
            text=f"Calibrate {self.config.oxygen_point1['x']}%")

        self.calibrate_point2_button = Button(master=self.frame,
            bg=Theme.active().SURFACE,
            command=self.calibrate_level2_point,
            fg=Theme.active().TXT_ON_SURFACE,
            text=f"Calibrate {self.STEP_2_CALIBRATION_PERCENTAGE}%")

        self.calibration_buttons = [self.calibrate_point1_button,
                                    self.calibrate_point2_button]

    def calibrate_point1(self):
        self.calibrated_point = self.config.oxygen_point1
        self.calibrate()
        self.calibrate_point2_button.configure(state="disabled")

    def calibrate_level2_point(self):
        self.calibrated_point = {"x": self.STEP_2_CALIBRATION_PERCENTAGE,
                                 "y": 0}
        self.calibrate()
        self.calibrate_point1_button.configure(state="disabled")

    def read_raw_value(self):
        return self.sensor_driver.read_oxygen_raw()

    def get_difference(self):
        """Get offset drift."""
        average_percentage_found = \
            self.sensor_driver.convert_voltage_to_oxygen(
                self.average_value_found)
        return average_percentage_found - self.calibrated_point["x"]

    def configure_new_calibration(self):
        new_calibration_point = {"x": self.calibrated_point["x"],
                                 "y": self.average_value_found}

        if self.calibrated_point is self.config.oxygen_point1:
            other_calibration_point = self.config.oxygen_point2
        else:
            other_calibration_point = self.config.oxygen_point1

        offset, scale = calc_calibration_line(new_calibration_point,
                                              other_calibration_point)

        self.sensor_driver.set_oxygen_calibration(offset, scale)

        if self.calibrated_point is self.config.oxygen_point1:
            self.config.oxygen_point1["x"] = new_calibration_point["x"]
            self.config.oxygen_point1["y"] = new_calibration_point["y"]
        else:
            self.config.oxygen_point2["x"] = new_calibration_point["x"]
            self.config.oxygen_point2["y"] = new_calibration_point["y"]

def calc_calibration_line(point1, point2):
    if point1["x"] > point2["x"]:
        left_p = point2
        right_p = point1
    elif point1["x"] < point2["x"]:
        left_p = point1
        right_p = point2

    if point1["x"] == point2["x"] or point1["y"] == point2["y"]:
        raise InvalidCalibrationError(
            "Bad calibration.\n"
            "Two calibration points have same value:\n"
            f"({int(left_p['x'])}% : {left_p['y']:.5f}V),\n"
            f"({int(right_p['x'])}% : {right_p['y']:.5f}V)")

    # We compute the calibration line on the reversed function:
    # O2 percentage as function of voltage. x is now the 'y' and vise versa.
    new_scale = (right_p["x"] - left_p["x"]) / (
        right_p["y"] - left_p["y"])

    # normal slope should be around 50..
    if new_scale <= 0 or new_scale > 100:
        raise InvalidCalibrationError(
            f"Bad calibration.\ntoo small slope."
            f"({int(left_p['x'])}% : {left_p['y']:.5f}V),\n"
            f"({int(right_p['x'])}% : {right_p['y']:.5f}V)")

    new_offset = point1["x"] - point1["y"] * new_scale
    return new_offset, new_scale
