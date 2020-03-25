import os
import json
import logging
from threading import Lock
from queue import Queue

from data.thresholds import (RespiratoryRateThreshold, PresThreshold,
                             MViThreshold, VtiThreshold)
from data.alerts import AlertsQueue

THIS_DIRECTORY = os.path.dirname(__file__)

log = logging.getLogger(__name__)


class DataStore(object):
    CONFIG_FILE = os.path.abspath(os.path.join(THIS_DIRECTORY, "..", "config.json"))
    SYSTEM_SAMPLE_INTERVAL = 22 #KHZ

    MS_TO_SEC = 1000

    def __init__(self, vti_threshold, mvi_threshold,
                 pressure_threshold, resp_rate_threshold,
                 graph_seconds, breathing_threshold, log_enabled=True):
        self.vti_threshold = vti_threshold
        self.mvi_threshold = mvi_threshold
        self.pressure_threshold = pressure_threshold
        self.resp_rate_threshold = resp_rate_threshold
        self.graph_seconds = graph_seconds
        self.breathing_threshold = breathing_threshold
        self.log_enabled = log_enabled

        self.samples_in_graph_amount = \
            int((self.graph_seconds * self.MS_TO_SEC) /
                self.SYSTEM_SAMPLE_INTERVAL)

        self.mvi = 0
        self.vti_measurements = Queue(maxsize=40)
        self.pressure_measurements = Queue(maxsize=40)
        self.x_axis = range(0, self.samples_in_graph_amount)

        self.alerts_queue = AlertsQueue()
        self.lock = Lock()

    def __del__(self):
        self.save_to_file()

    @classmethod
    def load_from_config(cls):
        try:
            with open(cls.CONFIG_FILE) as f:
                config = json.load(f)

            vti = VtiThreshold(min=config["threshold"]["vti"]["min"],
                               max=config["threshold"]["vti"]["max"],
                               step=config["threshold"]["vti"]["step"])
            mvi = MViThreshold(min=config["threshold"]["mvi"]["min"],
                               max=config["threshold"]["mvi"]["max"],
                               step=config["threshold"]["mvi"]["step"])
            pressure = PresThreshold(min=config["threshold"]["pressure"]["min"],
                                     max=config["threshold"]["pressure"]["max"],
                                     step=config["threshold"]["pressure"]["step"])
            resp_rate = RespiratoryRateThreshold(min=config["threshold"]["bpm"]["min"],
                                                 max=config["threshold"]["bpm"]["max"],
                                                 step=config["threshold"]["bpm"]["step"])

            graph_seconds = config["graph_seconds"]
            breathing_threshold = config["threshold"]["breathing_threshold"]

            return cls(vti_threshold=vti,
                       mvi_threshold=mvi,
                       pressure_threshold=pressure,
                       resp_rate_threshold=resp_rate,
                       graph_seconds=graph_seconds,
                       breathing_threshold=breathing_threshold)

        except Exception as e:
            log.exception("Could not read log file, using default values", e)
            return cls(vti_threshold=VtiThreshold(),
                       mvi_threshold=MViThreshold(),
                       pressure_threshold=PresThreshold(),
                       resp_rate_threshold=RespiratoryRateThreshold(),
                       graph_seconds=12,
                       breathing_threshold=3.5)

    def save_to_file(self):
        log.info("Saving threshold values to database")
        config = {
            "threshold": {
                "vti": {
                    "min": self.vti_threshold.min,
                    "max": self.vti_threshold.max,
                    "step": self.vti_threshold.step
                },
                "mvi": {
                    "min": self.mvi_threshold.min,
                    "max": self.mvi_threshold.max,
                    "step": self.mvi_threshold.step
                },
                "pressure": {
                    "min": self.pressure_threshold.min,
                    "max": self.pressure_threshold.max,
                    "step": self.pressure_threshold.step
                },
                "bpm": {
                    "min": self.breathing_threshold.min,
                    "max": self.breathing_threshold.max,
                    "step": self.breathing_threshold.step
                },
                "breathing_threshold": self.breathing_threshold
            },
            "log_enabled": self.log_enabled,
            "graph_seconds": self.graph_seconds
        }

        with open(self.CONFIG_FILE, "w") as config_file:
            json.dump(config, config_file, indent=4)


    def set_vti_value(self, new_value):
        with self.lock:
            # pop last item if queue is full
            if self.vti_measurements.full():
                self.vti_measurements.get()
            self.vti_measurements.put(new_value)

    def set_pressure_value(self, new_value):
        with self.lock:
            # pop last item if queue is full
            if self.pressure_measurements.full():
                self.pressure_measurements.get()
            self.pressure_measurements.put(new_value)

    def get_vti_value(self, new_value):
        with self.lock:
            self.vti_measurements.get(new_value)

    def get_pressure_value(self, new_value):
        with self.lock:
            self.pressure_measurements.get(new_value)

    def set_mvi_value(self, new_value):
        self.mvi = new_value
