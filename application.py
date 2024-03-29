import os
import time
from uptime import uptime
from tkinter import Tk

from data.configurations import ConfigurationManager
from graphics.panes import MasterFrame
from graphics.themes import Theme
from graphics.calibrate.screen import calc_calibration_line
from graphics.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from graphics.snackbar.default_config_snackbar import DefaultConfigSnackbar


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
                 simulation=False, fps=10, sample_rate=70, record_sensors=False):
        self.should_run = True
        self.drivers = drivers
        self.arm_wd_event = arm_wd_event
        self.sampler = sampler
        self.simulation = simulation
        self.events = events
        self.frame_interval = 1 / fps
        self.sample_interval = 1 / sample_rate
        self.last_sample_update_ts = 0
        self.last_gui_update_ts = 0
        self.root = Tk()
        self.theme = Theme.choose_theme()  # TODO: Make this configurable
        self.root.protocol("WM_DELETE_WINDOW", self.exit)  # Catches Alt-F4
        self.root.title("Inhalator")
        self.root.geometry(f'{SCREEN_WIDTH}x{SCREEN_HEIGHT}')

        if os.uname()[1] == 'raspberrypi':
            # on production we don't want to see the ugly cursor
            self.root.config(cursor="none")

            # We want fullscreen only for the raspberry-pi
            self.root.attributes("-fullscreen", True)

        self.master_frame = MasterFrame(self.root,
                                        measurements=measurements,
                                        events=events,
                                        drivers=drivers,
                                        record_sensors=record_sensors)
        self.config = ConfigurationManager.config()

        if ConfigurationManager.loaded_from_defaults:
            DefaultConfigSnackbar(self.root).show()

        # Load sensors calibrations
        differential_pressure_driver = self.drivers.differential_pressure
        differential_pressure_driver.set_calibration_offset(self.config.calibration.dp_offset)
        oxygen_driver = self.drivers.a2d
        oxygen_driver.set_oxygen_calibration(
            *calc_calibration_line(
                self.config.calibration.oxygen_point1,
                self.config.calibration.oxygen_point2))

    def exit(self):
        self.root.quit()
        self.should_run = False

    def render(self):
        self.master_frame.render()
        self.events.alerts_queue.initial_uptime = uptime()

    def gui_update(self):
        self.root.update()
        self.root.update_idletasks()
        self.master_frame.update()

    def sample(self):
        self.sampler.sampling_iteration()

    @property
    def next_render(self):
        return self.frame_interval - (time.time() - self.last_gui_update_ts)

    @property
    def next_sample(self):
        return self.sample_interval - (time.time() - self.last_sample_update_ts)

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

    def run_iterations(self, max_iterations, fast_forward=True, render=True):
        if render:
            self.render()

        for _ in range(max_iterations):
            try:
                if self.next_sample > 0 and not fast_forward:
                    time.sleep(max(self.next_sample, 0))
                self.sample()
                self.last_sample_update_ts = time.time()
                if self.next_render <= 0:
                    self.gui_update()
                    self.last_gui_update_ts = time.time()

                self.arm_wd_event.set()
            except KeyboardInterrupt:
                break
