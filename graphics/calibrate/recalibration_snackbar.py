from tkinter import *

from data.configurations import Configurations
from graphics.calibrate.screen import CalibrationScreen, DifferentialPressureCalibration

BLACK = "#000000"
WHITE = "#ffffff"
PRIMARY = "#3700b3"


class RecalibrationSnackbar(object):  #
    def __init__(self, root, drivers):
        self.root = root
        self.drivers = drivers
        self.config = Configurations.instance()

        self.frame = Frame(master=self.root, background=WHITE)
        self.buttons_frame = Frame(master=self.frame, background=WHITE)
        self.calibrate_button = Button(master=self.buttons_frame,
                                       background=WHITE,
                                       foreground=PRIMARY,
                                       activebackground=WHITE,
                                       activeforeground=PRIMARY,
                                       font=("Roboto", 20, "bold"),
                                       highlightthickness=0,
                                       bd=0,
                                       command=self.on_calibrate,
                                       text="CALIBRATE")
        self.snooze_button = Button(master=self.buttons_frame,
                                    background=WHITE,
                                    foreground=PRIMARY,
                                    activebackground=WHITE,
                                    activeforeground=PRIMARY,
                                    bd=0,
                                    highlightthickness=0,
                                    command=self.on_snooze,
                                    font=("Roboto", 20, "bold"),
                                    text="NOT NOW")
        self.text_frame = Frame(master=self.frame,
                                background=WHITE)
        self.text_label = Label(master=self.text_frame,
                                background=WHITE,
                                font=("Roboto", 16),
                                foreground=BLACK,
                                text="")

    def show(self):
        self.frame.place(relx=0.1, rely=0.8, relwidth=0.8, relheight=0.2)
        self.text_frame.place(relx=0.05, relwidth=0.9, relheight=0.6, rely=0)
        self.buttons_frame.place(relx=0, rely=0.6, relwidth=1, relheight=0.4)

        self.text_label.pack(anchor="w", side="left", fill="both")
        self.calibrate_button.pack(anchor="e", side="right")
        self.snooze_button.pack(anchor="e", side="right")

        self.text_label.configure(text="%d hours have passed since the last time the "
                                  "Air-Flow sensor was calibrated, please re-calibrate it." %
                                  self.config.flow_calibration_timeout_hrs)

    def on_snooze(self):
        self.hide()

    def on_calibrate(self):
        self.hide()
        screen = CalibrationScreen(self.root, DifferentialPressureCalibration, self.drivers)
        screen.show()

    def hide(self):
        self.frame.place_forget()
