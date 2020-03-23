from queue import Queue
import os
import json
import logging

THIS_DIRECTORY = os.path.dirname(__file__)

log = logging.getLogger(__name__)


class Threshold(object):
    UNIT = NotImplemented

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "{} = {}{}".format(self.name, self.value, self.UNIT)


class PressureThreshold(Threshold):
    UNIT = "bar"


class AirFlowThreshold(Threshold):
    UNIT = "ltr"



class DataStore(object):
    CONFIG_FILE = os.path.join(THIS_DIRECTORY, "config.json")

    def __init__(self):
        with open(self.CONFIG_FILE) as f:
            config = json.load(f)

        self.pressure_min_threshold = PressureThreshold(name="Pressure MIN",
                                                value=config["threshold"]["pressure"]["min"])  # mbar
        self.pressure_max_threshold = PressureThreshold(name="Pressure MAX",
                                                value=config["threshold"]["pressure"]["max"])  # mbar
        self.flow_min_threshold = AirFlowThreshold(name="Flow MIN",
                                            value=config["threshold"]["flow"]["min"])  # Liter
        self.flow_max_threshold = AirFlowThreshold(name="Flow MAX",
                                            value=config["threshold"]["flow"]["max"])

        self.threshold_step_size = config["threshold"]["step_size"]
        self.breathing_threshold = config["threshold"]["breathing"]

        self.flow_display_values = [0] * 40
        self.pressure_display_values = [0] * 40
        self.x_axis = range(0, 40)

        self.alerts = Queue(maxsize=10)

        self.log_enabled = config["log_enabled"]

    def __del__(self):
        self.save_to_file()

    def save_to_file(self):
        log.info("Saving threshold values to database")
        config = {
            "threshold": {
                "pressure": {
                    "min": self.pressure_min_threshold.value,
                    "max": self.pressure_max_threshold.value,
                },
                "flow": {
                    "min": self.flow_min_threshold.value,
                    "max": self.flow_max_threshold.value,
                },
                "step_size": self.threshold_step_size,
                "breathing": self.breathing_threshold,
                },
            "log_enabled": True
        }

        with open(self.CONFIG_FILE, "w") as f:
            json.dump(config, f)

    def update_flow_values(self, new_value):
        if len(self.flow_display_values) == len(self.x_axis):
            self.flow_display_values.pop(0)
        self.flow_display_values.append(new_value)

    def update_pressure_values(self, new_value):
        if len(self.pressure_display_values) == len(self.x_axis):
            self.pressure_display_values.pop(0)
        self.pressure_display_values.append(new_value)

    def set_alert(self, alert):
        self.alerts.put(alert)

    def get_alert(self):
        return self.alerts.get()
