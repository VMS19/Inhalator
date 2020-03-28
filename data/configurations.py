import os
import json
import logging

from errors import ConfigurationFileError
from data.thresholds import (RespiratoryRateThreshold, PressureThreshold,
                             VolumeThreshold, FlowThreshold)


THIS_DIRECTORY = os.path.dirname(__file__)
log = logging.getLogger(__name__)


class Configurations(object):
    """Configurations for the entire project.

    Note that this class is implemented with the 'Singleton' design pattern,
    since access to it is needed all across the application and only a single
    instance of it would make sense.
    """
    CONFIG_FILE = os.path.abspath(os.path.join(THIS_DIRECTORY, "..", "config.json"))
    DEFAULT_CONFIG_FILE = os.path.abspath(os.path.join(THIS_DIRECTORY, "..", "default_config.json"))

    __configurations_instance = None

    def __init__(self, flow_threshold, volume_threshold,
                 pressure_threshold, resp_rate_threshold,
                 graph_seconds, breathing_threshold, log_enabled=True, debug_port=7777):
        self.flow_threshold = flow_threshold
        self.volume_threshold = volume_threshold
        self.pressure_threshold = pressure_threshold
        self.resp_rate_threshold = resp_rate_threshold
        self.graph_seconds = graph_seconds
        self.breathing_threshold = breathing_threshold
        self.log_enabled = log_enabled
        self.debug_port = debug_port

    def __del__(self):
        self.save_to_file(self.CONFIG_FILE)

    @classmethod
    def instance(cls):
        if cls.__configurations_instance is not None:
            return cls.__configurations_instance

        instance = cls._load()
        cls.__configurations_instance = instance
        return instance

    @classmethod
    def _load(cls):
        try:
            return cls._parse_config_file(cls.CONFIG_FILE)

        except ConfigurationFileError:
            # The second call to _parse_config_file might fail,
            # we will however let the exception propagate upwards
            return cls._parse_config_file(cls.DEFAULT_CONFIG_FILE)


    @classmethod
    def _parse_config_file(cls, config_file):
        try:
            with open(config_file) as f:
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
            raise ConfigurationFileError("Could not load config file %s"
                                         % config_file) from e

    def save_to_file(self, config_path=CONFIG_FILE):
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
                    "min": self.volume_threshold.min,
                    "max": self.volume_threshold.max,
                    "step": self.volume_threshold.step
                },
                "breathing_threshold": self.breathing_threshold
            },
            "log_enabled": self.log_enabled,
            "graph_seconds": self.graph_seconds,
            "debug_port": self.debug_port,
        }

        with open(config_path, "w") as config_file:
            json.dump(config, config_file, indent=4)