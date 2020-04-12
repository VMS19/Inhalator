import os
import time
from tkinter import Tk

from graphics.panes import MasterFrame
from graphics.themes import Theme
from data.configurations import Configurations, ConfigurationState
from data.alerts import AlertCodes


class Application(object):
    """The Inhalator application"""
    TEXT_SIZE = 10
    HARDWARE_SAMPLE_RATE = 33  # HZ

    __instance = None  # shared instance

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    @classmethod
    def instance(cls):
        return cls.__instance

    def __init__(self, measurements, events, arm_wd_event, drivers, sampler,
                 simulation=False, fps=15, sample_rate=90):
        self.should_run = True
        self.drivers = drivers
        self.arm_wd_event = arm_wd_event
        self.sampler = sampler
        self.simulation = simulation
        self.frame_interval = 1 / fps
        self.sample_interval = 1 / sample_rate
        self.last_sample_update_ts = 0
        self.last_gui_update_ts = 0
        self.root = Tk()
        self.theme = Theme.choose_theme()  # TODO: Make this configurable
        self.root.protocol("WM_DELETE_WINDOW", self.exit)  # Catches Alt-F4
        self.root.title("Inhalator")
        self.root.geometry('800x480')
        self.root.attributes("-fullscreen", True)


        if os.uname()[1] == 'raspberrypi':
            # on production we don't want to see the ugly cursor
            self.root.config(cursor="none")

        # We want to alert that config.json is corrupted
        if Configurations.configuration_state() == ConfigurationState.CONFIG_CORRUPTED:
            events.alerts_queue.enqueue_alert(AlertCodes.NO_CONFIGURATION_FILE)
            Configurations.instance().save_to_file()  # Create config file for future use.

        self.master_frame = MasterFrame(self.root,
                                        measurements=measurements,
                                        events=events,
                                        drivers=drivers)

        differential_pressure_driver = self.drivers.acquire_driver("differential_pressure")
        differential_pressure_driver.set_calibration_offset(Configurations.instance().dp_offset)

    def exit(self):
        self.root.quit()
        self.should_run = False

    def render(self):
        self.master_frame.render()

    def gui_update(self):
        self.root.update()
        self.root.update_idletasks()
        self.master_frame.update()

    def sample(self):
        self.sampler.sampling_iteration()

    def run(self):
        self.render()
        while self.should_run:
            try:
                time_now = time.time()
                if (time_now - self.last_gui_update_ts) >= self.frame_interval:
                    self.gui_update()
                    self.last_gui_update_ts = time_now

                if (time_now - self.last_sample_update_ts) >= self.sample_interval:
                    self.sample()
                    self.last_sample_update_ts = time_now

                self.arm_wd_event.set()
            except KeyboardInterrupt:
                break
        self.exit()
        self.drivers.acquire_driver("aux").stop()

    def run_iterations(self, max_iterations, fast_forward=True, render=True):
        if render:
            self.render()

        for _ in range(max_iterations):
            try:
                if self.next_sample > 0 and not fast_forward:
                    time.sleep(max(self.next_sample, 0))
                self.sample()
                if self.next_render <= 0:
                    self.gui_update()
                self.arm_wd_event.set()
            except KeyboardInterrupt:
                break
