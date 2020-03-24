import alerts

# Tkinter stuff
import platform

if platform.python_version() < '3':
    import Tkinter

else:
    from tkinter import *

from sound import SoundDevice
from graphics.panes import MasterFrame


class GUI(object):
    """GUI class for Inhalator"""
    TEXT_SIZE = 10

    def __init__(self, data_store):
        self.store = data_store
        self.root = Tk()
        self.root.title("Inhalator")
        self.root.geometry('800x480')
        self.root.attributes("-fullscreen", True)
        self.master_frame = MasterFrame(self.root, store=self.store)

        self.error_dict = {
            alerts.alerts.PRESSURE_LOW : ("Pressure ({}mbar) dropped below healthy lungs pressure ({}mbar)", self.store.pressure_min_threshold),
            alerts.alerts.PRESSURE_HIGH : ("Pressure ({}mbar) exceeded healthy lungs pressure ({}mbar)", self.store.pressure_max_threshold),
            alerts.alerts.BREATHING_VOLUME_LOW : ("Breathing Volume ({}ltr) went under minimum threshold ({}ltr)", self.store.flow_min_threshold),
            alerts.alerts.BREATHING_VOLUME_HIGH : ("Breathing Volume ({}ltr) exceeded maximum threshold ({}ltr)", self.store.flow_max_threshold)
        }

    def exitProgram(self, sig, _):
        print("Exit Button pressed")
        self.root.quit()

    #
    # def update_alert(self):
    #     if self.store.alerts.empty():
    #         return
    #
    #     cur_alert = self.store.alerts.get()
    #     alert_format = self.error_dict[cur_alert[0]]
    #     self.alert(alert_format[0].format(cur_alert[1], alert_format[1]))

    # def change_threshold(self, threshold):
    #     prompt = ThresholdPrompt(self.root, self.store, threshold,
    #                              self.on_change_threshold_prompt_exit)
    #     self.flow_max_threshold_change_button.configure(state="disabled")
    #     self.flow_min_threshold_change_button.configure(state="disabled")
    #     self.pressure_max_threshold_change_button.configure(state="disabled")
    #     self.pressure_min_threshold_change_button.configure(state="disabled")
    #     prompt.show()
    #
    # def on_change_threshold_prompt_exit(self):
    #     self.update_thresholds()
    #     self.flow_max_threshold_change_button.configure(state="normal")
    #     self.flow_min_threshold_change_button.configure(state="normal")
    #     self.pressure_max_threshold_change_button.configure(state="normal")
    #     self.pressure_min_threshold_change_button.configure(state="normal")
    #
    def alert(self, msg):
        # TODO: display flashing icon or whatever
        SoundDevice.beep()

    def render(self):
        self.master_frame.render()


    def gui_update(self):
        # self.update_alert()
        self.root.update()
        self.root.update_idletasks()
        self.master_frame.update()