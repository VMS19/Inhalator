import csv
import logging
import os
from itertools import product, cycle
import time
from unittest.mock import patch, Mock

import pytest
from pytest import approx

from algo import Sampler
from data import alerts
from data.measurements import Measurements
from data.events import Events
from data.configurations import Configurations
from data.thresholds import (FlowRange, PressureRange,
                             RespiratoryRateRange, VolumeRange)
from drivers.driver_factory import DriverFactory


MICROSECOND = 10 ** -6
SIMULATION_LENGTH = 1  # seconds
LOW_THRESHOLD = -50000
HIGH_THRESHOLD = 50000

CYCLE_TIME = 5.265
SIMULATION_SAMPLES = 1000


@pytest.fixture
def driver_factory():
    return DriverFactory(simulation_mode=True, simulation_data="sinus")


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


def test_sampler_volume_calculation(events, measurements, config):
    """Test volume calculation working correctly.

    Flow:
        * Run pig simulation which contain one breath cycle.
        * Simulate constant flow of 1.
        * Validate expected volume.
    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, "pig_sim.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)

    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    timer = driver_factory.get_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      oxygen_a2d, timer)

    for _ in range(SIMULATION_SAMPLES):
        sampler.sampling_iteration()

    expected_volume = CYCLE_TIME / 60 * 1000
    msg = f"Expected volume of {expected_volume}, received {measurements.inspiration_volume}"
    assert measurements.inspiration_volume == approx(expected_volume, rel=0.1), msg


def test_sampler_alerts_when_volume_exceeds_minium(events, measurements, config, driver_factory):
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    timer = driver_factory.get_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      oxygen_a2d, timer)
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
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    timer = driver_factory.get_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      oxygen_a2d, timer)
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


def test_volume_similiar_to_monitor(events, measurements, config):
    """Test volume calculation working correctly.
    We compare experiment data to what the monitor showed.
    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, "bad_volume_accumulation_samples.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)

    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    timer = driver_factory.get_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      oxygen_a2d, timer)

    for _ in range(600):
        sampler.sampling_iteration()

    inspiration_according_to_monitor = 333
    expiration_according_to_monitor = 311
    assert measurements.inspiration_volume == approx(inspiration_according_to_monitor,
                                                     rel=10)

    assert measurements.expiration_volume == approx(expiration_according_to_monitor,
                                                    rel=10)
