from typing import Optional

from pydantic import AnyHttpUrl, BaseModel
from pydantic.dataclasses import dataclass

from configuration.thresholds import O2Range, VolumeRange, PressureRange, RespiratoryRateRange


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
    telemetry: TelemetryConfig = TelemetryConfig()
