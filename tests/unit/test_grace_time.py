import time

import pytest

from algo import Sampler
from data import alerts
from data.measurements import Measurements
from data.events import Events
from data.configurations import Configurations
from data.thresholds import (O2Range, PressureRange,
                             RespiratoryRateRange, VolumeRange)
from drivers.driver_factory import DriverFactory

GRACE_TIME = 2
LOW_THRESHOLD = -50000
HIGH_THRESHOLD = 50000


@pytest.fixture
def driver_factory():
    return DriverFactory(simulation_mode=True, simulation_data="sinus")


@pytest.fixture
def config():
    c = Configurations.instance()
    c.o2_range = O2Range(min=0, max=100)
    c.pressure_range = PressureRange(min=-1, max=30)
    c.resp_rate_range = RespiratoryRateRange(min=0, max=30)
    c.volume_range = VolumeRange(min=100, max=600)
    c.graph_seconds = 12
    c.breathing_threshold = 3.5
    c.log_enabled = False
    c.boot_alert_grace_time = GRACE_TIME
    return c


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def events():
    return Events()


def test_grace_time_alerts(events, measurements, config, driver_factory):
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer, average_window=1)

    config.volume_range = VolumeRange(HIGH_THRESHOLD, HIGH_THRESHOLD)

    current_time = time.time()
    while time.time() - current_time < GRACE_TIME:
        sampler.sampling_iteration()

    assert len(events.alerts_queue) == 0, "shouldn't get any alerts during grace time"

    current_time = time.time()
    while time.time() - current_time < GRACE_TIME:
        sampler.sampling_iteration()

    assert len(events.alerts_queue) > 0

    all_alerts = list(events.alerts_queue.queue.queue)
    assert all(alert == alerts.AlertCodes.VOLUME_LOW for alert in all_alerts)