from dataclasses import field
from datetime import datetime

import psutil
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from uptime import uptime

from algo import VentilationState
from data.configurations import ConfigurationManager
from graphics.version import __version__


def get_temperatures():
    return {name: [t.current for t in v]
            for name, v in psutil.sensors_temperatures().items()}


def get_config():
    return ConfigurationManager.instance().config.json(indent=2)


@dataclass
class Alert:
    code: int
    message: str
    timestamp: float

    @classmethod
    def from_app_alert(cls, other):
        """
        Converts `data.alerts.Alert` to this plain Alert class.
        Future version will hopefully replace `data.alert.Alert` with this class
        """
        return cls(code=other.code, message=str(other), timestamp=other.timestamp)


@dataclass
class SystemStatus:
    battery_percentage: float = 0
    up_time: float = field(default_factory=uptime)
    cpu_usage: float = field(default_factory=psutil.cpu_percent)
    ram_usage: float = field(default_factory=lambda: psutil.virtual_memory().percent)
    load_avg: tuple = field(default_factory=psutil.getloadavg)
    time: datetime = field(default_factory=datetime.now)
    temperatures: dict = field(default_factory=get_temperatures)
    alerts: list = None


@dataclass
class VentilationStatus:
    timestamp: float = None
    inspiration_volume: float = None
    expiration_volume: float = None
    avg_inspiration_volume: float = None
    avg_expiration_volume: float = None
    peak_flow: float = None
    peak_pressure: float = None
    min_pressure: float = None
    bpm: int = None
    o2_saturation_percentage: float = None
    current_state: VentilationState = VentilationState.Unknown
    alerts: list = None


class StatusReport(BaseModel):
    ventilation_status: VentilationStatus = None
    system_status: SystemStatus = None
    version: str = __version__
