from tkinter import Button, Frame

from graphics.snackbar.base_snackbar import BaseSnackbar


class DefaultConfigSnackbar(BaseSnackbar):
    
    config_exists = True

    def __init__(self, root):
        super().__init__(root)

        self.ok_button = Button(
            master=self.buttons_frame,
            background=self.background_color,
            foreground=self.calibrate_button_color,
            activebackground=self.background_color,
            activeforeground=self.calibrate_button_color,
            font=("Roboto", 14, "bold"),
            highlightthickness=0,
            bd=0,
            command=self.ok,
            text="OK")
        
        self.text_label.configure(text="No configuration file was found\n\n\t"
                                       "Loading with default configuration..")

    def show(self):
        super().show()
        self.ok_button.pack(anchor="e", side="right")

    def ok(self):
        self.hide()
