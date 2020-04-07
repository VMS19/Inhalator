import time

import pytest
from pytest import approx

from data import alerts
from data.measurements import Measurements
from data.events import Events
from data.configurations import Configurations
from data.thresholds import (O2Range, PressureRange,
                             RespiratoryRateRange, VolumeRange)
from tests.unit.conftest import create_sampler

SIMULATION_FOLDER = "simulation"

MICROSECOND = 10 ** -6
SIMULATION_LENGTH = 1  # seconds
LOW_THRESHOLD = -50000
HIGH_THRESHOLD = 50000

SIMULATION_SAMPLES = 1000


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


def test_sampler_volume_calculation(events, measurements):
    """Test volume calculation working correctly.

    Flow:
        * Run pig simulation which contain one breath cycle.
        * Simulate constant flow of 1.
        * Validate expected volume.
    """
    sampler = create_sampler("pig_sim_cycle.csv", events, measurements)
    for _ in range(SIMULATION_SAMPLES):
        sampler.sampling_iteration()

    expected_volume = 332
    msg = f"Expected volume of {expected_volume}, received {measurements.inspiration_volume}"
    assert measurements.inspiration_volume == approx(expected_volume, rel=0.1), msg


def test_sampler_alerts_when_volume_exceeds_minium(events, measurements, config):
    sampler = create_sampler("sinus", events, measurements)
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


def test_sampler_alerts_when_volume_exceeds_maximum(events, measurements, config):
    sampler = create_sampler("sinus", events, measurements)
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
