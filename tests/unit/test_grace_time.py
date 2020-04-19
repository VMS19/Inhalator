from unittest.mock import patch

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
EPSILON = GRACE_TIME / 1000

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
    e = Events()
    e.alerts_queue.initial_uptime = 0
    return e


@pytest.fixture
def sampler(events, measurements, driver_factory):
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    return Sampler(measurements, events, flow_sensor, pressure_sensor,
                   a2d, timer, average_window=1)


@patch("data.alerts.uptime")
def test_grace_time_alerts(mocked_uptime, events, config, sampler):
    """Check no alerts in grace time, and alert received after."""
    mocked_uptime.return_value = GRACE_TIME - EPSILON

    config.pressure_range = PressureRange(HIGH_THRESHOLD, HIGH_THRESHOLD)

    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0, "shouldn't get any alerts during grace time"

    mocked_uptime.return_value = GRACE_TIME + EPSILON
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 1

    all_alerts = list(events.alerts_queue.queue.queue)
    assert all(alert == alerts.AlertCodes.PRESSURE_LOW for alert in all_alerts)


@patch("data.alerts.uptime")
@patch("time.time")
@pytest.mark.parametrize('current_time', [GRACE_TIME - EPSILON, GRACE_TIME + EPSILON])
def test_grace_time_alerts_move_time_forward(
        mocked_time, mocked_uptime, events, config, sampler, current_time):
    """Check no alerts in grace time, and alert received after.

    Check that moving time after grace time doesn't cause alert in grace time.
    Check that moving time before grace time doesn't prevent alert after grace time.
    """
    mocked_uptime.return_value = GRACE_TIME - EPSILON
    mocked_time.return_value = current_time

    config.pressure_range = PressureRange(HIGH_THRESHOLD, HIGH_THRESHOLD)

    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0, "shouldn't get any alerts during grace time"

    mocked_uptime.return_value = GRACE_TIME + EPSILON
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 1

    all_alerts = list(events.alerts_queue.queue.queue)
    assert all(alert == alerts.AlertCodes.PRESSURE_LOW for alert in all_alerts)
