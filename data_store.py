from queue import Queue
import os
import json

import numpy as np

THIS_DIRECTORY = os.path.dirname(__file__)


class DataStore(object):
    CONFIG_FILE = os.path.join(THIS_DIRECTORY, "config.json")
    THRESHOLD_STEP_SIZE = 0.5
    BREATHING_THRESHOLD = 3.5  # mbar

    def __init__(self):
        with open(self.CONFIG_FILE) as f:
            config = json.load(f)

        self.pressure_min_threshold = config["threshold"]["pressure"]["min"]  # mbar
        self.pressure_max_threshold = config["threshold"]["pressure"]["max"]  # mbar
        self.flow_min_threshold = config["threshold"]["flow"]["min"]  # Liter
        self.flow_max_threshold = config["threshold"]["flow"]["max"]
        self.log_enabled = config["log_enabled"]
        self.flow_display_values = np.arange(0, 40, 1) * 0
        self.pressure_display_values = np.arange(0, 40, 1)
        self.x_axis = np.arange(0, 40, 1)
        self.alerts = Queue(maxsize=10)

    def __del__(self):
        pass


    def update_flow_values(self, new_value):
        if len(self.flow_display_values) == len(self.x_axis):
            self.flow_display_values = \
                np.append(np.delete(self.flow_display_values, 0), new_value)

        else:
            self.flow_display_values = np.append(self.flow_display_values,
                                                 new_value)

    def update_pressure_values(self, new_value):
        if len(self.pressure_display_values) == len(self.x_axis):
            self.pressure_display_values = \
                np.append(np.delete(self.pressure_display_values, 0), new_value)

        else:
            self.pressure_display_values = np.append(self.pressure_display_values,
                                                     new_value)

    def set_alert(self, alert):
        self.alerts.put(alert)

    def get_alert(self):
        return self.alerts.get()
