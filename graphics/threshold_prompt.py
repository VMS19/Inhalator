import platform

# Tkinter stuff
if platform.python_version() < '3':
    import tkMessageBox
    messagebox = tkMessageBox
    import Tkinter
    tk = Tkinter
    from Tkinter import *

else:
    from tkinter import messagebox
    import tkinter
    tk = tkinter
    from tkinter import *


class ThresholdPrompt(object):
    def __init__(self, root, store, threshold, exit_handler):
        self.root = root
        self.store = store
        self.threshold = threshold
        self.original_threshold_value = threshold.value
        self.exit_handler = exit_handler
        self.frame = Frame(self.root, bg="yellow")
        self.label = Label(master=self.frame)
        self.update_label()
        self.up_button = Button(master=self.frame, text="+",
                                command=self.increase, height="4", width="6")
        self.down_button = Button(master=self.frame, text="-",
                                  command=self.decrease, height="4", width="6")
        self.save_button = Button(master=self.frame, text="Save",
                                  command=self.save, height="4", width="6")

        self.cancel_button = Button(master=self.frame, text="Cancel",
                                    command=self.cancel, height="4", width="6")

    def update_label(self):
        self.label.config(text="{!r}".format(self.threshold))

    def increase(self):
        self.threshold.value += self.store.threshold_step_size
        self.update_label()

    def decrease(self):
        self.threshold.value -= self.store.threshold_step_size
        self.update_label()

    def show(self):
        self.frame.place(relx=0.65, rely=0, relwidth=0.35, relheight=1)
        self.label.pack()
        self.up_button.pack()
        self.down_button.pack()
        self.save_button.pack()
        self.cancel_button.pack()
        self.save_button.place(relx=0, rely=0.65, relwidth=1, relheight=0.15)
        self.cancel_button.place(relx=0, rely=0.85, relwidth=1, relheight=0.15)

    def save(self):
        self.store.save_to_file()  # Save new value in config.json file
        self.exit()

    def exit(self):
        self.frame.place_forget()
        del self.frame
        self.exit_handler()

    def cancel(self):
        self.threshold.value = self.original_threshold_value
        self.exit()
