from tkinter import Button, Frame

from graphics.snackbar.base_snackbar import BaseSnackbar


class DefaultConfigSnackbar(BaseSnackbar):

    def __init__(self, root):
        super().__init__(root)

        self.dismiss_button = Button(
            master=self.buttons_frame,
            background=self.background_color,
            foreground=self.calibrate_button_color,
            activebackground=self.background_color,
            activeforeground=self.calibrate_button_color,
            font=("Roboto", 14, "bold"),
            highlightthickness=0,
            bd=0,
            command=self.hide,
            text="Dismiss")
        
        self.dismiss_button.pack(anchor="e", side="right")
        self.text_label.configure(text="No configuration file was found\n\t"
                                       "Loading from default configuration...")

