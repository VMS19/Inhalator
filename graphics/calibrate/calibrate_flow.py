"""NOTE!!!!!!! This screen is for debugging and research ONLY. Hence the low-effort graphics"""

from tkinter import *

class CalibrateFlowScreen(object):
    def __init__(self, root, measurements, on_exit_callback):
        self.root = root
        self.measurements = measurements
        self.on_exit_callback = on_exit_callback

        self.frame = Frame(master=self.root)
        self.current_value_label = Label(master=self.frame,
                                         text="Current Value: 0ml",
                                         font=("Roboto", 12))

        self.hint_label = Label(master=self.frame, text="Enter new flow offset")
        self.offset_entry = Entry(master=self.frame)
        self.ok_button = Button(master=self.frame, text="OK", command=self.confirm)
        self.cancel_button = Button(master=self.frame, text="Cancel", command=self.cancel)

        # State
        self.original_offset = self.measurements.flow_offset

    def show(self):
        self.frame.place(relx=0.25, rely=0.25, relwidth=0.25, relheight=0.25)
        self.current_value_label.place(relx=0.2, rely=0, relwidth=0.5, relheight=0.2)
        self.hint_label.place(relx=0.3, relwidth=0.4, rely=0.2, relheight=0.1)
        self.offset_entry.place(relx=0.3, rely=0.3, relwidth=0.4, relheight=0.3)
        self.ok_button.place(rely=0.8, relheight=0.2, relx=0.3, relwidth=0.2)
        self.cancel_button.place(rely=0.8, relheight=0.2, relx=0.5, relwidth=0.2)

    def update(self):
        self.current_value_label.configure(
            text=f"Current Value: {round(self.measurements.last_flow_measuremnt, ndigits=2)}ml")
    def hide(self):
        self.on_exit_callback()
        self.frame.place_forget()

    def confirm(self):
        entered_value = float(self.offset_entry.get())
        self.measurements.flow_offset.offset = entered_value
        self.hide()

    def cancel(self):
        self.hide()
