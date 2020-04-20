import logging
import os
from enum import Enum
from typing import Optional

from pydantic import BaseModel, AnyHttpUrl
from pydantic.dataclasses import dataclass

from data.thresholds import PressureRange, VolumeRange, O2Range


class ConfigurationState(Enum):
    VALID_CONFIG = 0
    CONFIG_CORRUPTED = 1
    DEFAULT_CORRUPTED = 2


@dataclass
class Point:
    x: float
    y: float


@dataclass
class ThresholdsConfig:
    o2: O2Range = O2Range(min=20, max=100, step=1)
    volume: VolumeRange = VolumeRange(min=200, max=800, step=10)
    pressure: PressureRange = PressureRange(min=10, max=45, step=1)


@dataclass
class GraphYAxisConfig:
    min: float
    max: float
    autoscale: bool = False


@dataclass
class StateMachineConfig:
    min_insp_volume_for_inhale: float = 100
    min_exp_volume_for_exhale: float = 100
    min_pressure_slope_for_inhale: float = 3
    max_pressure_slope_for_exhale: float = 12


@dataclass
class AutoCalibrationConfig:
    enable: bool = True
    interval: int = 1800
    iterations: int = 4
    iteration_length: int = 30
    sample_threshold: float = 8
    slope_threshold: float = 10,
    min_tail: int = 12,
    grace_length: int = 5


@dataclass
class CalibrationConfig:
    dp_offset: float = 0.026
    oxygen_point1: Point = Point(x=21, y=0.3567203)
    oxygen_point2: Point = Point(x=0, y=0)
    dp_calibration_timeout_hrs: int = 5
    flow_recalibration_reminder: bool = False
    auto_calibration: AutoCalibrationConfig = AutoCalibrationConfig()


@dataclass
class GraphsConfig:
    flow: GraphYAxisConfig = GraphYAxisConfig(min=-40, max=50, autoscale=True)
    pressure: GraphYAxisConfig = GraphYAxisConfig(min=-10, max=50, autoscale=False)


@dataclass
class TelemetryConfig:
    enable: bool = False
    url: Optional[AnyHttpUrl] = None
    api_key: Optional[str] = None


class Config(BaseModel):
    thresholds: ThresholdsConfig = ThresholdsConfig()
    graph_y_scale: GraphsConfig = GraphsConfig()
    state_machine: StateMachineConfig = StateMachineConfig()
    calibration: CalibrationConfig = CalibrationConfig()
    graph_seconds: float = 12.0
    low_battery_percentage: float = 15
    mute_time_limit: float = 120
    boot_alert_grace_time: float = 7
    telemetry: TelemetryConfig = TelemetryConfig()


class ConfigurationManager(object):
    """Manages loading and saving the project's configuration.

    This class has a shared global instance that can be used across the
    application. It is accessible through the `instance()` method
    """
    class Source(Enum):
        ValidFile = 0  # Configuration loaded from a valid config file.
        Default_NoFileFound = 1  # Default loaded: config file did not exist.
        Default_InvalidConfigFile = 2  # Default loaded: invalid config file

    THIS_DIRECTORY = os.path.dirname(__file__)
    CONFIG_FILE = os.path.abspath(os.path.join(THIS_DIRECTORY, "..", "config.json"))

    __instance = None

    def __init__(self, config_path=CONFIG_FILE):
        # First - Initialize the config attribute.
        super(ConfigurationManager, self).__setattr__("_config", None)
        if config_path is None:
            config_path = self.CONFIG_FILE
        self._config_path = config_path

        self._log = logging.getLogger(self.__class__.__name__)
        self.source = self._load()

    def __getattr__(self, item):
        # Behave as a proxy for the underlying config.
        return getattr(
            super(ConfigurationManager, self).__getattribute__("_config"), item)

    def __setattr__(self, key, value):
        # Behave as a proxy for the underlying config.
        if hasattr(self._config, key):
            return setattr(self._config, key, value)
        return super(ConfigurationManager, self).__setattr__(key, value)

    def __eq__(self, other):
        if isinstance(other, Config):
            return self._config == other
        if isinstance(other, ConfigurationManager):
            return self._config == other._config
        return False

    @classmethod
    def instance(cls):
        if cls.__instance is not None:
            return cls.__instance

        cls.__instance = cls()
        return cls.__instance

    def _load(self):
        if not os.path.isfile(self._config_path):
            # Not an error though.
            self._log.warning(
                f"Configuration file %s does not exist.", self._config_path)
            self.use_default()
            return ConfigurationManager.Source.Default_NoFileFound

        try:
            self._config = Config.parse_file(self._config_path)
            return ConfigurationManager.Source.ValidFile
        except Exception as e:
            self._log.error("Failed loading configuration file: %s.", e)
            self.use_default()
            return ConfigurationManager.Source.Default_InvalidConfigFile

    def use_default(self):
        self._log.info(" Using default config")
        self._config = Config()
        # Make sure next time we'll have a valid config
        self.save()

    def save(self):
        try:
            with open(self._config_path, "w") as f:
                f.write(self._config.json(indent=2))
                f.flush()
                os.fsync(f.fileno())
            self._log.info(f"Configuration saved to %s", self._config_path)
        except Exception as e:
            # There's nothing more we can do about it.
            self._log.error("Error saving configuration: %s", e)
