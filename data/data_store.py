import os
import json
import logging
from threading import Lock
from queue import Queue

from data.thresholds import AirFlowThreshold, PressureThreshold
from data.alerts import AlertsQueue

THIS_DIRECTORY = os.path.dirname(__file__)

log = logging.getLogger(__name__)


class DataStore(object):
    CONFIG_FILE = os.path.abspath(os.path.join(THIS_DIRECTORY, "..", "config.json"))
    FLOW_MIN_Y, FLOW_MAX_Y = (0, 80)
    PRESSURE_MIN_Y, PRESSURE_MAX_Y = (0, 40)
    SYSTEM_SAMPLE_INTERVAL = 22 #KHZ

    MS_TO_SEC = 1000

    def __init__(self):
        with open(self.CONFIG_FILE) as f:
            config = json.load(f)

        self.pressure_min_threshold = PressureThreshold(name="Pressure Min",
                                                value=config["threshold"]["pressure"]["min"])  # mbar
        self.pressure_max_threshold = PressureThreshold(name="Pressure Max",
                                                value=config["threshold"]["pressure"]["max"])  # mbar
        self.flow_min_threshold = AirFlowThreshold(name="Flow Min",
                                            value=config["threshold"]["flow"]["min"])  # Liter
        self.flow_max_threshold = AirFlowThreshold(name="Flow Max",
                                            value=config["threshold"]["flow"]["max"])

        self.threshold_step_size = config["threshold"]["step_size"]
        self.breathing_threshold = config["threshold"]["breathing"]

        self.graph_seconds = config["graph_seconds"]
        self.samples_in_graph_amount = \
            int((self.graph_seconds * self.MS_TO_SEC) /
                self.SYSTEM_SAMPLE_INTERVAL)

        self.flow_measurements = Queue(maxsize=40)
        self.pressure_measurements = Queue(maxsize=40)

        self.x_axis = range(0, self.samples_in_graph_amount)

        self.volume = 0

        self.log_enabled = config["log_enabled"]

        self.alerts_queue = AlertsQueue()

        self.lock = Lock()

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
            "log_enabled": True,
            "samples_in_graph_amount": self.samples_in_graph_amount,
            "graph_seconds": self.graph_seconds,
        }

        with open(self.CONFIG_FILE, "w") as f:
            json.dump(config, f)

    def get_flow_value(self, new_value):
        with self.lock:
            # pop last item if queue is full
            if self.flow_measurements.full():
                self.flow_measurements.get()
            self.flow_measurements.put(new_value)

    def set_pressure_value(self, new_value):
        with self.lock:
            # pop last item if queue is full
            if self.pressure_measurements.full():
                self.pressure_measurements.get()
            self.pressure_measurements.put(new_value)

    def get_flow_value(self, new_value):
        with self.lock:
            self.flow_measurements.get(new_value)

    def get_pressure_value(self, new_value):
        with self.lock:
            self.pressure_measurements.get(new_value)

    def update_volume_value(self, new_value):
        self.volume = new_value
