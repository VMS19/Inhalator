from __future__ import annotations

import logging
import os
from typing import Optional

from pydantic import BaseModel, AnyHttpUrl
from pydantic.dataclasses import dataclass

from data.thresholds import PressureRange, VolumeRange, O2Range, RespiratoryRateRange


@dataclass
class Point:
    x: float
    y: float


@dataclass
class ThresholdsConfig:
    o2: O2Range = O2Range(min=20, max=100, step=1)
    volume: VolumeRange = VolumeRange(min=200, max=800, step=10)
    pressure: PressureRange = PressureRange(min=10, max=50, step=1)
    respiratory_rate: RespiratoryRateRange = RespiratoryRateRange(min=5, max=45, step=1)


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
    slope_threshold: float = 10
    min_tail: int = 12
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
    record_sensors: bool = False
    telemetry: TelemetryConfig = TelemetryConfig()


class ConfigurationManager(object):
    """Manages loading and saving the project's configuration.

    This class has a shared global instance that can be used across the
    application. It is accessible through the `instance()` method
    """
    __instance: ConfigurationManager = None
    THIS_DIRECTORY = os.path.dirname(__file__)
    PROJECT_DIRECTORY = os.path.dirname(THIS_DIRECTORY)
    CONFIG_FILE = os.path.abspath(os.path.join(PROJECT_DIRECTORY, "config.json"))
    config_exists = True

    @classmethod
    def instance(cls):
        return cls.__instance

    @classmethod
    def config(cls):
        return cls.__instance.config

    @classmethod
    def initialize(cls, events, path=CONFIG_FILE):
        log = logging.getLogger(cls.__name__)
        cls.__instance = ConfigurationManager(path)
        try:
            cls.__instance.load()
        except FileNotFoundError:
            # Not considered an error we should alert on.
            log.info("No config file. Using defaults")
            cls.config_exists = False
        except Exception as e:
            log.error("Error loading config file: %s. Using defaults", e)
            from data.alerts import AlertCodes
            events.alerts_queue.enqueue_alert(AlertCodes.INVALID_CONFIGURATION_FILE)
        finally:
            # We want to save even on successful load because the existing file
            # might be valid JSON but incomplete, E.g in case of version upgrade.
            cls.__instance.save()
        return cls.__instance

    def __init__(self, path):
        self._path = path
        self._log = logging.getLogger(self.__class__.__name__)
        self.config = Config()

    def load(self):
        self.config = Config.parse_file(self._path)
        self._log.info("Configuration loaded from %s", self._path)

    def save(self):
        try:
            with open(self._path, "w") as f:
                f.write(self.config.json(indent=2))
                f.flush()
                os.fsync(f.fileno())
            self._log.info("Configuration saved to %s", self._path)
        except Exception as e:
            # There's nothing more we can do about it.
            self._log.error("Error saving configuration: %s", e)
