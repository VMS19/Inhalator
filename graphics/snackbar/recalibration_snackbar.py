import datetime

import timeago
from tkinter import *

from consts import HOURS_TO_SECONDS
from graphics.calibrate.screen import CalibrationScreen, DifferentialPressureCalibration
from graphics.snackbar.base_snackbar import BaseSnackbar


class RecalibrationSnackbar(BaseSnackbar):
    def __init__(self, root, drivers, observer):
        super().__init__(root)

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

        self.drivers = drivers
        self.timer = drivers.acquire_driver("timer")
        self.observer = observer
        self.last_dp_calibration_ts = None
        observer.subscribe(self, self.on_calibration_done)

    def show(self):
        super().show()

        self.log.warning(f"User has not calibrated air-flow sensor for at "
                         f"least {self.config.dp_calibration_timeout_hrs} "
                         f"hours. Flow recalibration notice has been "
                         f"popped-up")

        self.calibrate_button.pack(anchor="e", side="right")
        self.snooze_button.pack(anchor="e", side="right")

    def on_calibration_done(self, timestamp):
        self.last_dp_calibration_ts = timestamp
        self.hide()

    def update(self):
        if not self.config.flow_recalibration_reminder:
            return

        # we don't want to notify about recalibration right away when
        # the program have just been started or when one of the actions
        # in the snackbar has been chosen
        now = self.timer.get_current_time()
        if self.last_dp_calibration_ts is None:
            self.last_dp_calibration_ts = now
            return

        next_calibration_time = (
            self.last_dp_calibration_ts +
            self.config.dp_calibration_timeout_hrs * HOURS_TO_SECONDS)

        if not self.shown and now >= next_calibration_time:
            self.show()

        if self.shown:
            self.update_label()

    def on_snooze(self):
        self.hide()
        self.last_dp_calibration_ts = None

    def on_calibrate(self):
        self.hide()
        self.last_dp_calibration_ts = None
        screen = CalibrationScreen(self.root,
                                   DifferentialPressureCalibration,
                                   self.drivers,
                                   self.observer)
        screen.show()

    def update_label(self):
        last_calibration_dt = datetime.datetime.fromtimestamp(
            self.last_dp_calibration_ts)

        now_dt = datetime.datetime.fromtimestamp(self.timer.get_current_time())

        time_ago = timeago.format(now_dt - last_calibration_dt)

        self.text_label.configure(
            text=f"Last air-flow calibration was {time_ago}.\n"
                 f"You have to perform an air-flow calibration.")
