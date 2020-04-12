import os
import time

import pytest
from pytest import approx

from algo import Sampler
from data import alerts
from data.measurements import Measurements
from data.events import Events
from data.configurations import Configurations
from data.thresholds import (O2Range, PressureRange,
                             RespiratoryRateRange, VolumeRange)
from drivers.driver_factory import DriverFactory

SIMULATION_FOLDER = "simulation"

MICROSECOND = 10 ** -6
SIMULATION_LENGTH = 1  # seconds
LOW_THRESHOLD = -50000
HIGH_THRESHOLD = 50000

SIMULATION_SAMPLES = 1000


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
    return c


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def events():
    return Events()


def test_sampler_volume_calculation(events, measurements, config):
    """Test volume calculation working correctly.

    Flow:
        * Run pig simulation which contain one breath cycle.
        * Simulate constant flow of 1.
        * Validate expected volume.
    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             "pig_sim_cycle.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)

    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer, average_window=1)

    for _ in range(SIMULATION_SAMPLES):
        sampler.sampling_iteration()

    expected_volume = 332
    msg = f"Expected volume of {expected_volume}, received {measurements.inspiration_volume}"
    assert measurements.inspiration_volume == approx(expected_volume, rel=0.1), msg


def test_alert_on_exhale_volume(events, measurements, config):
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             "pig_sim_cycle.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)

    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer, average_window=1)

    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.volume_range = VolumeRange(0, 50)

    current_time = time.time()
    while time.time() - current_time < SIMULATION_LENGTH:
        time.sleep(MICROSECOND)
        sampler.sampling_iteration()

    expected_insp_volume = 332
    msg = f"Expected volume of {expected_insp_volume}, received {measurements.inspiration_volume}"
    assert measurements.inspiration_volume == approx(expected_insp_volume, rel=0.1), msg

    expected_exp_volume = 28
    msg = f"Expected volume of {expected_exp_volume}, received {measurements.expiration_volume}"
    assert measurements.expiration_volume == approx(expected_exp_volume, rel=0.1), msg

    assert len(events.alerts_queue) == 0


def test_sampler_alerts_when_volume_exceeds_minimum(events, measurements, config, driver_factory):
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer, average_window=1)
    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.volume_range = VolumeRange(HIGH_THRESHOLD, HIGH_THRESHOLD)

    current_time = time.time()
    while time.time() - current_time < SIMULATION_LENGTH:
        time.sleep(MICROSECOND)
        sampler.sampling_iteration()

    assert len(events.alerts_queue) > 0

    all_alerts = list(events.alerts_queue.queue.queue)
    assert all(alert == alerts.AlertCodes.VOLUME_LOW for alert in all_alerts)


def test_sampler_alerts_when_volume_exceeds_maximum(events, measurements, config, driver_factory):
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer, average_window=1)
    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.volume_range = VolumeRange(LOW_THRESHOLD, LOW_THRESHOLD)

    current_time = time.time()
    while time.time() - current_time < SIMULATION_LENGTH:
        time.sleep(MICROSECOND)
        sampler.sampling_iteration()

    assert len(events.alerts_queue) > 0

    all_alerts = list(events.alerts_queue.queue.queue)
    assert all(alert == alerts.AlertCodes.VOLUME_HIGH for alert in all_alerts)

