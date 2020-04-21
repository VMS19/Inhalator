import os
import logging
import datetime

import timeago
from tkinter import *

from data.configurations import Configurations


THIS_FILE = __file__
THIS_DIRECTORY = os.path.dirname(THIS_FILE)
RESOURCES_DIRECTORY = os.path.join(
    os.path.dirname(THIS_DIRECTORY), "resources")


class BaseSnackbar(object):
    WARNING_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY,
                                      "baseline_warning_white_24dp.png")

    def __init__(self, root):
        self.background_color = "lightgray"
        self.text_color = "black"
        self.calibrate_button_color = "#77216F"
        self.snooze_button_color = "#333333"
        self.title_background = "orange"
        self.title_foreground = "white"

        self.root = root
        self.config = Configurations.instance()
 
        self.log = logging.getLogger(__name__)

        self.frame = Frame(master=self.root,
                           background=self.background_color)
        self.buttons_frame = Frame(master=self.frame,
                                   background=self.background_color)
 
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
       

    def hide(self):
        self.frame.place_forget()
        self.shown = False

class LockSnackbar(BaseSnackbar):
    def __init__(self, root):

        BaseSnackbar.__init__(self, root)

        self.snooze_button = Button(master=self.buttons_frame,
                            background=self.background_color,
                            foreground=self.snooze_button_color,
                            activebackground=self.background_color,
                            activeforeground=self.snooze_button_color,
                            bd=0,
                            highlightthickness=0,
                            command=self.on_hide,
                            font=("Roboto", 14, "bold"),
                            text="Hide")
        
        self.text_label = Label(master=self.text_frame,
                                background=self.background_color,
                                font=("Arial", 14),
                                anchor="w",
                                padx=20,
                                width=80,
                                justify="left",
                                foreground=self.text_color,
                                text="Lock screen is on")

    def on_hide(self):
        self.hide()

    def show(self):
        super().show()
        self.snooze_button.pack(anchor="e", side="right")
