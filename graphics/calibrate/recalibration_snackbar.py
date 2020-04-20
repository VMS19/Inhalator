import time
import timeago
import datetime
import os

from tkinter import *

from data.configurations import Configurations
from graphics.calibrate.screen import CalibrationScreen, DifferentialPressureCalibration


THIS_FILE = __file__
THIS_DIRECTORY = os.path.dirname(THIS_FILE)
RESOURCES_DIRECTORY = os.path.join(os.path.dirname(
    os.path.dirname(THIS_DIRECTORY)),
    "resources")


class RecalibrationSnackbar(object):
    WARNING_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY,
                                      "baseline_warning_white_24dp.png")

    def __init__(self, root, drivers, observer):
        self.background_color = "lightgray"
        self.text_color = "black"
        self.calibrate_button_color = "#77216F"
        self.snooze_button_color = "#333333"
        self.title_background = "orange"
        self.title_foreground = "white"

        self.root = root
        self.drivers = drivers
        self.config = Configurations.instance()
        self.timer = drivers.acquire_driver("timer")
        self.frame = Frame(master=self.root,
                           background=self.background_color)
        self.buttons_frame = Frame(master=self.frame,
                                   background=self.background_color)

        self.calibrate_button = Button(master=self.buttons_frame,
                                       background=self.background_color,
                                       foreground=self.calibrate_button_color,
                                       activebackground=self.background_color,
                                       activeforeground=self.calibrate_button_color,
                                       font=("Roboto", 14, "bold"),
                                       highlightthickness=0,
                                       bd=0,
                                       command=self.on_calibrate,
                                       text="CALIBRATE")

        self.snooze_button = Button(master=self.buttons_frame,
                                    background=self.background_color,
                                    foreground=self.snooze_button_color,
                                    activebackground=self.background_color,
                                    activeforeground=self.snooze_button_color,
                                    bd=0,
                                    highlightthickness=0,
                                    command=self.on_snooze,
                                    font=("Roboto", 14, "bold"),
                                    text="NOT NOW")

        self.text_frame = Frame(master=self.frame,
                                background=self.background_color)

        self.text_label = Label(master=self.text_frame,
                                background=self.background_color,
                                font=("Arial", 14),
                                anchor="w",
                                padx=20,
                                width=80,
                                justify="left",
                                foreground=self.text_color,
                                text="")

        self.title_frame = Frame(master=self.frame,
                                 background=self.title_background)

        self.title_label = Label(master=self.title_frame,
                                 background=self.title_background,
                                 font=("Roboto", 22),
                                 anchor="w",
                                 padx=20,
                                 foreground=self.title_foreground,
                                 text="WARNING!")

        self.title_image = PhotoImage(file=self.WARNING_IMAGE_PATH)
        self.title_image_container = Label(master=self.title_frame,
                                           background=self.title_background,
                                           padx=20,
                                           anchor="e",
                                           image=self.title_image)

        self.observer = observer
        self.last_dp_calibration_ts = None
        observer.subscribe(self, self.on_calibration_done)

        self.shown = False

    def show(self):
        self.shown = True
        self.frame.place(relx=0.075, rely=0.655, relwidth=0.85, relheight=0.3)
        self.title_frame.place(relx=0, relwidth=1, relheight=(1/3), rely=0)
        self.text_frame.place(relx=0, relwidth=1, relheight=(1/3), rely=(1/3))
        self.buttons_frame.place(relx=0, rely=(2/3), relwidth=1, relheight=(1/3))

        self.title_image_container.pack(anchor=W,
                                        fill="y", padx=(20, 0),
                                        side="left")
        self.title_label.pack(anchor=W, fill="both", side="left")

        self.text_label.pack(anchor=W, fill="both")
        self.calibrate_button.pack(anchor="e", side="right")
        self.snooze_button.pack(anchor="e", side="right")

    def on_calibration_done(self, timestamp):
        self.last_dp_calibration_ts = timestamp

    def update(self):
        # we don't want to notify about recalibration right away
        now = time.time()
        if self.last_dp_calibration_ts is None:
            self.last_dp_calibration_ts = now
            return

        next_calibration_time = (
            self.last_dp_calibration_ts +
            self.config.dp_calibration_timeout_hrs * self.timer.HOURS_TO_SECONDS)

        if not self.shown and now >= next_calibration_time:
            self.show()

        if self.shown:
            self.update_label()

    def on_snooze(self):
        self.hide()
        self.last_dp_calibration_ts = time.time()

    def on_calibrate(self):
        self.hide()
        self.last_dp_calibration_ts = time.time()
        screen = CalibrationScreen(self.root,
                                   DifferentialPressureCalibration,
                                   self.drivers,
                                   self.observer)
        screen.show()

    def hide(self):
        self.frame.place_forget()
        self.shown = False

    def update_label(self):
        last_calibration_dt = datetime.datetime.fromtimestamp(
            self.last_dp_calibration_ts)

        now_dt = datetime.datetime.fromtimestamp(time.time())

        time_ago = timeago.format(now_dt - last_calibration_dt)

        self.text_label.configure(
            text=f"Last air-flow calibration was {time_ago}.\n"
                 f"You have to perform an air-flow calibration.")
