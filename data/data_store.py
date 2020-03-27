import os
import json
import logging
from threading import Lock
from queue import Queue

from data.thresholds import (RespiratoryRateThreshold, PressureThreshold,
                             VolumeThreshold, FlowThreshold)
from data.alerts import AlertsQueue

THIS_DIRECTORY = os.path.dirname(__file__)

log = logging.getLogger(__name__)


class DataStore(object):
    CONFIG_FILE = os.path.abspath(os.path.join(THIS_DIRECTORY, "..", "config.json"))
    SYSTEM_SAMPLE_INTERVAL = 22 #KHZ
    I2C_BUS = 2
    MS_TO_SEC = 1000

    def __init__(self, flow_threshold, volume_threshold,
                 pressure_threshold, resp_rate_threshold,
                 graph_seconds, breathing_threshold, log_enabled=True,debug_port=7777):
        self.flow_threshold = flow_threshold
        self.volume_threshold = volume_threshold
        self.pressure_threshold = pressure_threshold
        self.resp_rate_threshold = resp_rate_threshold
        self.graph_seconds = graph_seconds
        self.breathing_threshold = breathing_threshold
        self.log_enabled = log_enabled
        self.debug_port = debug_port

        self.samples_in_graph_amount = \
            int((self.graph_seconds * self.MS_TO_SEC) /
                self.SYSTEM_SAMPLE_INTERVAL)

        self.volume = 0
        self.flow_measurements = Queue(maxsize=40)
        self.pressure_measurements = Queue(maxsize=40)
        self.x_axis = range(0, self.samples_in_graph_amount)

        self.intake_peak_flow = 0
        self.intake_peak_pressure = 0

        self.alerts_queue = AlertsQueue()
        self.lock = Lock()

    def __del__(self):
        self.save_to_file()

    @classmethod
    def load_from_config(cls):
        try:
            with open(cls.CONFIG_FILE) as f:
                config = json.load(f)

            flow = FlowThreshold(min=config["threshold"]["flow"]["min"],
                               max=config["threshold"]["flow"]["max"],
                               step=config["threshold"]["flow"]["step"])
            volume = VolumeThreshold(min=config["threshold"]["volume"]["min"],
                               max=config["threshold"]["volume"]["max"],
                               step=config["threshold"]["volume"]["step"])
            pressure = PressureThreshold(min=config["threshold"]["pressure"]["min"],
                                         max=config["threshold"]["pressure"]["max"],
                                         step=config["threshold"]["pressure"]["step"])
            resp_rate = RespiratoryRateThreshold(min=config["threshold"]["bpm"]["min"],
                                                 max=config["threshold"]["bpm"]["max"],
                                                 step=config["threshold"]["bpm"]["step"])

            graph_seconds = config["graph_seconds"]
            breathing_threshold = config["threshold"]["breathing_threshold"]
            log_enabled = config["log_enabled"]
            debug_port = config["debug_port"]

            return cls(flow_threshold=flow,
                       volume_threshold=volume,
                       pressure_threshold=pressure,
                       resp_rate_threshold=resp_rate,
                       graph_seconds=graph_seconds,
                       breathing_threshold=breathing_threshold,
                       log_enabled=log_enabled,
                       debug_port=debug_port)

        except Exception as e:
            log.exception("Could not read log file, using default values", e)
            return cls(flow_threshold=FlowThreshold(),
                       volume_threshold=VolumeThreshold(),
                       pressure_threshold=PressureThreshold(),
                       resp_rate_threshold=RespiratoryRateThreshold(),
                       graph_seconds=12,
                       breathing_threshold=3.5)

    def save_to_file(self):
        log.info("Saving threshold values to database")
        config = {
            "threshold": {
                "flow": {
                    "min": self.flow_threshold.min,
                    "max": self.flow_threshold.max,
                    "step": self.flow_threshold.step
                },
                "volume": {
                    "min": self.volume_threshold.min,
                    "max": self.volume_threshold.max,
                    "step": self.volume_threshold.step
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


    def set_flow_value(self, new_value):
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

    def set_intake_peaks(self, flow, pressure, volume):
        self.intake_peak_flow = flow
        self.intake_peak_pressure = pressure
        self.volume = volume
