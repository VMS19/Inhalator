from itertools import cycle
from unittest.mock import Mock, patch

import pytest

from algo import Sampler
from data import alerts
from data.measurements import Measurements
from data.events import Events
from data.configurations import Configurations
from data.thresholds import (FlowRange, PressureRange,
                             RespiratoryRateRange, VolumeRange)
from drivers.driver_factory import DriverFactory


MICROSECOND = 10 ** -6
NO_BREATH_TIME = 13  # seconds
SIMULATION_TIMESTAMPS = [0.00045 * i for i in range(1, 7000)]
SIMULATION_NO_BREATH_TIMESTAMP = [SIMULATION_TIMESTAMPS[-1] + NO_BREATH_TIME]
# adding timestamp 0 for inhaleStateHandler init
MOCK_TIME_STAMPS = [0] + SIMULATION_TIMESTAMPS + SIMULATION_NO_BREATH_TIMESTAMP
NOISE_TIMESTAMPS = [0.002 * i for i in range(1, 7000)]


simulation_no_breath_time_mock = Mock()
simulation_no_breath_time_mock.side_effect = MOCK_TIME_STAMPS
dead_no_breath_time_mock = Mock()
dead_no_breath_time_mock.side_effect = MOCK_TIME_STAMPS
noise_no_breath_time_mock = Mock()
noise_no_breath_time_mock.side_effect = NOISE_TIMESTAMPS


@pytest.fixture
def config():
    c = Configurations.instance()
    c.flow_range = FlowRange(min=0, max=30)
    c.pressure_range = PressureRange(min=0, max=30)
    c.resp_rate_range = RespiratoryRateRange(min=0, max=30)
    c.volume_range = VolumeRange(min=0, max=30)
    c.graph_seconds = 12
    c.debug_port = 7777
    c.breathing_threshold = 3.5
    c.log_enabled = False
    return c


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def events():
    return Events()


@pytest.mark.xfail(reason="Receiving alerts on negative volume")
@patch('time.time', simulation_no_breath_time_mock)
def test_sinus_alerts_when_no_breath(events, measurements, config):
    """Test that no-breath alert is sent after time without breathing

    Flow:
        * Run sinus simulation for a few cycles and make sure no alert was sent.
        * Don't simulate sensors for time required to sent no-breath alert.
        * Make sure a single no-breath alert was sent.
    """
    driver_factory = DriverFactory(simulation_mode=True, simulation_data="sinus")
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor, oxygen_a2d)

    for _ in range(len(SIMULATION_TIMESTAMPS)):
        sampler.sampling_iteration()

    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()  # mock time simulates no breath time

    assert len(events.alerts_queue) == 1

    alert = events.alerts_queue.queue.get()
    assert alert == alerts.AlertCodes.NO_BREATH


@patch('time.time', dead_no_breath_time_mock)
def test_dead_man_alerts_when_no_breath(events, measurements, config):
    """Test that no-breath alert is sent after time without breathing

    Flow:
        * Run deadman simulation for no-breath time.
        * Make sure at least one no-breath alert was sent.
    """
    driver_factory = DriverFactory(simulation_mode=True, simulation_data="dead")
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor, oxygen_a2d)

    for _ in range(len(SIMULATION_TIMESTAMPS) + 1):
        sampler.sampling_iteration()

    assert len(events.alerts_queue) >= 1

    all_alerts = list(events.alerts_queue.queue.queue)
    assert all(alert == alerts.AlertCodes.NO_BREATH for alert in all_alerts)


@patch('time.time', noise_no_breath_time_mock)
def test_noise_alerts_when_no_breath(events, measurements, config):
    """Test that no-breath alert is sent after time without breathing

    Flow:
        * Run noise simulation for no-breath time.
        * Make sure at least one no-breath alert was sent.
    """
    driver_factory = DriverFactory(simulation_mode=True, simulation_data="dead")
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      oxygen_a2d)

    for _ in range(len(SIMULATION_TIMESTAMPS) - 1):
        sampler.sampling_iteration()

    assert len(events.alerts_queue) >= 1

    all_alerts = list(events.alerts_queue.queue.queue)
    assert all(alert == alerts.AlertCodes.NO_BREATH for alert in all_alerts)