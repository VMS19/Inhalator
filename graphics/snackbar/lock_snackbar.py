from tkinter import *

from graphics.snackbar.base_snackbar import BaseSnackbar

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
