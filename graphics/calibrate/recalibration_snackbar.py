from tkinter import *

from data.configurations import Configurations
from graphics.calibrate.screen import CalibrationScreen, DifferentialPressureCalibration
from graphics.themes import Theme


class RecalibrationSnackbar(object):

    def __init__(self, root, drivers, observer):
        self.text_color = Theme.active().WHITE
        self.background_color = "#6200EE"
        self.primary_color = "#64b5f6"

        self.root = root
        self.drivers = drivers
        self.config = Configurations.instance()
        self.timer = drivers.acquire_driver("timer")
        self.frame = Frame(master=self.root, background=self.background_color)
        self.buttons_frame = Frame(master=self.frame,
                                   background=self.background_color)
        self.calibrate_button = Button(master=self.buttons_frame,
                                       background=self.background_color,
                                       foreground=self.primary_color,
                                       activebackground=self.background_color,
                                       activeforeground=self.primary_color,
                                       font=("Roboto", 14, "bold"),
                                       highlightthickness=0,
                                       bd=0,
                                       command=self.on_calibrate,
                                       text="CALIBRATE")
        self.snooze_button = Button(master=self.buttons_frame,
                                    background=self.background_color,
                                    foreground=self.primary_color,
                                    activebackground=self.background_color,
                                    activeforeground=self.primary_color,
                                    bd=0,
                                    highlightthickness=0,
                                    command=self.on_snooze,
                                    font=("Roboto", 14, "bold"),
                                    text="NOT NOW")
        self.text_frame = Frame(master=self.frame,
                                background=self.background_color)
        self.text_label = Label(master=self.text_frame,
                                background=self.background_color,
                                font=("Roboto", 12),
                                foreground=self.text_color,
                                text="")
        self.observer = observer
        self.last_dp_calibration_ts = 0
        observer.subscribe(self, self.on_calibration_done)

    def show(self):
        self.frame.place(relx=0.25, rely=0.8, relwidth=0.55, relheight=0.2)
        self.text_frame.place(relx=0.05, relwidth=0.9, relheight=0.6, rely=0)
        self.buttons_frame.place(relx=0, rely=0.6, relwidth=1, relheight=0.4)

        self.text_label.pack(anchor=W, fill="both")
        self.calibrate_button.pack(anchor="e", side="right")
        self.snooze_button.pack(anchor="e", side="right")

        self.text_label.configure(
            justify="left",
            text=f"{self.config.dp_calibration_timeout_hrs} hours since last "
                 f"air-flow calibration.\n"
                 f"You are encouraged to recalibrate")

    def on_calibration_done(self, timestamp):
        self.last_dp_calibration_ts = timestamp

    def update(self):
        next_calibration_time = (
            self.last_dp_calibration_ts +
            self.config.dp_calibration_timeout_hrs * self.timer.HOURS_TO_SECONDS)

        if self.timer.get_current_time() >= next_calibration_time:
            self.show()

    def on_snooze(self):
        self.hide()
        self.last_dp_calibration_ts = self.timer.get_current_time()

    def on_calibrate(self):
        self.hide()
        self.last_dp_calibration_ts = self.timer.get_current_time()
        screen = CalibrationScreen(self.root,
                                   DifferentialPressureCalibration,
                                   self.drivers,
                                   self.observer)
        screen.show()

    def hide(self):
        self.frame.place_forget()
