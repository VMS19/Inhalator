import os
import json
import logging
from enum import Enum

from errors import ConfigurationFileError
from data.thresholds import (RespiratoryRateRange, PressureRange,
                             VolumeRange, FlowRange)

THIS_DIRECTORY = os.path.dirname(__file__)
log = logging.getLogger(__name__)


class ConfigurationState(Enum):
    VALID_CONFIG = 0
    CONFIG_CORRUPTED = 1
    DEFAULT_CORRUPTED = 2


class Configurations(object):
    """Configurations for the entire project.

    Note that this class is implemented with the 'Singleton' design pattern,
    since access to it is needed all across the application and only a single
    instance of it would make sense.
    """
    CONFIG_FILE = os.path.abspath(os.path.join(THIS_DIRECTORY, "..", "config.json"))
    DEFAULT_CONFIG_FILE = os.path.abspath(os.path.join(THIS_DIRECTORY, "..", "default_config.json"))

    __instance = None

    def __init__(self, flow_range, volume_range, pressure_range, resp_rate_range,
                 flow_y_scale, pressure_y_scale, graph_seconds,
                 breathing_threshold, log_enabled=True, debug_port=7777,
                 mute_time_limit=120):
        self.flow_range = flow_range
        self.volume_range = volume_range
        self.pressure_range = pressure_range
        self.resp_rate_range = resp_rate_range
        self.graph_seconds = graph_seconds
        self.breathing_threshold = breathing_threshold
        self.log_enabled = log_enabled
        self.debug_port = debug_port
        self.mute_time_limit = mute_time_limit
        self.flow_y_scale = flow_y_scale
        self.pressure_y_scale = pressure_y_scale

    @classmethod
    def instance(cls):
        if cls.__instance is not None:
            return cls.__instance

        cls.__instance = cls._load()
        return cls.__instance

    @classmethod
    def configuration_state(cls):
        try:
            cls._parse_config_file(cls.CONFIG_FILE)
            return ConfigurationState.VALID_CONFIG

        except ConfigurationFileError:
            try:
                cls._parse_config_file(cls.DEFAULT_CONFIG_FILE)
                return ConfigurationState.CONFIG_CORRUPTED

            except ConfigurationFileError:
                return ConfigurationState.DEFAULT_CORRUPTED

    @classmethod
    def _load(cls):
        if not os.path.isfile(cls.CONFIG_FILE):
            # No config.json. Just load defaults. This is not an error.
            default_config = cls._parse_config_file(cls.DEFAULT_CONFIG_FILE)
            default_config.save_to_file(cls.CONFIG_FILE)  # Create non-default config file.
            return default_config

        try:
            return cls._parse_config_file(cls.CONFIG_FILE)
        except ConfigurationFileError as e:
            # The second call to _parse_config_file might fail,
            # we will however let the exception propagate upwards
            log.exception("Failed to load configuration file %s, "
                          "defauting to %s",
                          cls.CONFIG_FILE,
                          cls.DEFAULT_CONFIG_FILE)
            return cls._parse_config_file(cls.DEFAULT_CONFIG_FILE)

    @classmethod
    def _parse_config_file(cls, config_file):
        try:
            with open(config_file) as f:
                config = json.load(f)

            flow = FlowRange(min=config["threshold"]["flow"]["min"],
                             max=config["threshold"]["flow"]["max"],
                             step=config["threshold"]["flow"]["step"])
            volume = VolumeRange(min=config["threshold"]["volume"]["min"],
                                 max=config["threshold"]["volume"]["max"],
                                 step=config["threshold"]["volume"]["step"])
            pressure = PressureRange(min=config["threshold"]["pressure"]["min"],
                                     max=config["threshold"]["pressure"]["max"],
                                     step=config["threshold"]["pressure"]["step"])
            resp_rate = RespiratoryRateRange(min=config["threshold"]["bpm"]["min"],
                                             max=config["threshold"]["bpm"]["max"],
                                             step=config["threshold"]["bpm"]["step"])

            flow_y_scale = (config["graph_y_scale"]["flow"]["min"],
                            config["graph_y_scale"]["flow"]["max"])
            pressure_y_scale = (config["graph_y_scale"]["pressure"]["min"],
                                config["graph_y_scale"]["pressure"]["max"])

            graph_seconds = config["graph_seconds"]
            breathing_threshold = config["threshold"]["breathing_threshold"]
            log_enabled = config["log_enabled"]
            debug_port = config["debug_port"]
            mute_time_limit = config["mute_time_limit"]

            return cls(flow_range=flow,
                       volume_range=volume,
                       pressure_range=pressure,
                       resp_rate_range=resp_rate,
                       graph_seconds=graph_seconds,
                       breathing_threshold=breathing_threshold,
                       log_enabled=log_enabled,
                       debug_port=debug_port,
                       mute_time_limit=mute_time_limit,
                       flow_y_scale=flow_y_scale,
                       pressure_y_scale=pressure_y_scale)

        except Exception as e:
            raise ConfigurationFileError(f"Could not load "
                                         f"config file {config_file}") from e

    def save_to_file(self, config_path=CONFIG_FILE):
        log.info("Saving threshold values to database")
        config = {
            "threshold": {
                "flow": {
                    "min": self.flow_range.min,
                    "max": self.flow_range.max,
                    "step": self.flow_range.step
                },
                "volume": {
                    "min": self.volume_range.min,
                    "max": self.volume_range.max,
                    "step": self.volume_range.step
                },
                "pressure": {
                    "min": self.pressure_range.min,
                    "max": self.pressure_range.max,
                    "step": self.pressure_range.step
                },
                "bpm": {
                    "min": self.resp_rate_range.min,
                    "max": self.resp_rate_range.max,
                    "step": self.resp_rate_range.step
                },
                "breathing_threshold": self.breathing_threshold
            },
            "graph_y_scale": {
                "flow": {
                    "min": self.flow_y_scale[0],
                    "max": self.flow_y_scale[1]
                },
                "pressure": {
                    "min": self.pressure_y_scale[0],
                    "max": self.pressure_y_scale[1]
                }
            },
            "log_enabled": self.log_enabled,
            "graph_seconds": self.graph_seconds,
            "debug_port": self.debug_port,
            "mute_time_limit": self.mute_time_limit,
        }

        with open(config_path, "w") as config_file:
            json.dump(config, config_file, indent=4)
