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
    def __init__(self, root, store, threshold_min, threshold_max, exit_handler):
        self.root = root
        self.store = store
        self.threshold_min = threshold_min
        self.original_threshold_min_value = threshold_min.value

        self.threshold_max = threshold_max
        self.original_threshold_max_value = threshold_max.value

        self.exit_handler = exit_handler
        self.frame = Frame(self.root, bg="yellow")

        self.min_frame = Frame(master=self.frame)
        self.max_frame = Frame(master=self.frame)
        self.actions_frame = Frame(master=self.frame)

        self.min_label = Label(master=self.min_frame, font=("Tahoma", 18))
        self.min_up_button = Button(master=self.min_frame, text="+",
                                command=self.increase_min, height="4", width="6")
        self.min_down_button = Button(master=self.min_frame, text="-",
                                  command=self.decrease_min, height="4", width="6")

        self.max_label = Label(master=self.max_frame, font=("Tahoma", 18))
        self.max_up_button = Button(master=self.max_frame, text="+",
                                    command=self.increase_max, height="4", width="6")
        self.max_down_button = Button(master=self.max_frame, text="-",
                                      command=self.decrease_max, height="4", width="6")


        self.save_button = Button(master=self.actions_frame, text="Save",
                                  command=self.save, height="4", width="6")
        self.cancel_button = Button(master=self.actions_frame, text="Cancel",
                                    command=self.cancel, height="4", width="6")

    def update_labels(self):
        self.min_label.config(text="{!r}".format(self.threshold_min))
        self.max_label.config(text="{!r}".format(self.threshold_max))

    def increase_min(self):
        self.threshold_min.value += self.store.threshold_step_size
        self.update_labels()

    def decrease_min(self):
        self.threshold_min.value -= self.store.threshold_step_size
        self.update_labels()

    def increase_max(self):
        self.threshold_max.value += self.store.threshold_step_size
        self.update_labels()

    def decrease_max(self):
        self.threshold_max.value -= self.store.threshold_step_size
        self.update_labels()

    def show(self):
        self.update_labels()
        self.frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.min_frame.place(relx=0, rely=0, relwidth=0.5, relheight=0.7)
        self.max_frame.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.7)
        self.actions_frame.place(relheight=0.3, relwidth=1, relx=0, rely=0.7)

        self.max_label.place(relx=0, rely=0, relheight=0.25, relwidth=0.8)
        self.max_up_button.place(relx=0.075, rely=0.3, relheight=0.6, relwidth=0.45)
        self.max_down_button.place(relx=0.575, rely=0.3, relheight=0.6, relwidth=0.45)

        self.min_label.place(relx=0, rely=0, relheight=0.25, relwidth=0.8)
        self.min_up_button.place(relx=0.075, rely=0.3, relheight=0.6, relwidth=0.45)
        self.min_down_button.place(relx=0.575, rely=0.3, relheight=0.6, relwidth=0.45)

        self.save_button.place(rely=0.2, relheight=0.6, relx=0.525, relwidth=0.1)
        self.cancel_button.place(rely=0.2, relheight=0.6, relx=0.375, relwidth=0.1)

    def save(self):
        self.store.save_to_file()  # Save new value in config.json file
        self.exit()

    def exit(self):
        self.frame.place_forget()
        del self.frame
        self.exit_handler()

    def cancel(self):
        self.threshold_min.value = self.original_threshold_min_value
        self.threshold_max.value = self.original_threshold_max_value
        self.exit()
