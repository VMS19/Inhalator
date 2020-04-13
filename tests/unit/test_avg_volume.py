import os
from statistics import mean

import pytest
from pytest import approx

from algo import Sampler
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
SAMPLES_IN_TEST = 118
NO_BREATH_TIME = 13  # seconds


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
    c.min_exp_volume_for_exhale = 0
    return c


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def events():
    return Events()


def test_sampler_avg_volume_calculation(events, measurements, config):
    """Test average volume calculation working correctly.

    Flow:
        * Run pig simulation which contain one breath cycle.
        * Simulate constant flow of 1.
        * Validate expected average  volume.
    """
    samples_in_file = 90
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             "single_cycle_good.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)

    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer, average_window=1)

    for _ in range(samples_in_file):
        sampler.sampling_iteration()

    expected_volume = 842

    msg = f"Expected volume of {expected_volume}, received {measurements.avg_insp_volume}"
    assert measurements.inspiration_volume == approx(expected_volume, rel=0.1), msg

    expected_exp_volume = 501
    msg = f"Expected volume of {expected_exp_volume}, received {measurements.avg_exp_volume}"
    assert measurements.expiration_volume == approx(expected_exp_volume, rel=0.1), msg


def test_sampler_avg_volume_calculation_multi_cycles(events, measurements, config):
    """Test average volume calculation working correctly.

    Flow:
        * Run pig simulation which contain one breath cycle.
        * Simulate constant flow of 1.
        * Validate expected average  volume.
    """
    samples_in_file = 556
    values_to_integrate = 4  # The number of integrals that should be averaged.
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             "several_cycles_good.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)

    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer, average_window=1)

    for _ in range(samples_in_file):
        sampler.sampling_iteration()

    volumes = [e[1] for e in sampler.vsm.insp_volumes]
    volumes = volumes[-values_to_integrate:]
    expected_avg = mean(volumes)
    msg = f"Expected average volume of {expected_avg}, received {measurements.avg_insp_volume}"
    assert measurements.inspiration_volume == approx(expected_avg, rel=0.1), msg

    volumes = [e[1] for e in sampler.vsm.exp_volumes]
    volumes = volumes[-values_to_integrate:]
    expected_avg = mean(volumes)
    msg = f"Expected volume of {expected_avg}, received {measurements.avg_exp_volume}"
    assert measurements.expiration_volume == approx(expected_avg, rel=0.1), msg


def test_no_breath(events, measurements, config):
    """Test that average volumes reset after time without breathing

    Flow:
        * Run noise simulation for no-breath time.
        * Make sure expected average volumes are zero
    """
    driver_factory = DriverFactory(simulation_mode=True, simulation_data="noise")
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer, average_window=1)

    time_intervals = 1 / driver_factory.MOCK_SAMPLE_RATE_HZ
    num_of_samples = int(NO_BREATH_TIME / time_intervals)
    for _ in range(num_of_samples):
        sampler.sampling_iteration()

    expected_exp_volume = 0
    msg = f"Expected volume of {expected_exp_volume}, received {measurements.avg_exp_volume}"
    assert measurements.expiration_volume == approx(expected_exp_volume, rel=0.1), msg

    expected_insp_volume = 0
    msg = f"Expected volume of {expected_insp_volume}, received {measurements.avg_insp_volume}"
    assert measurements.inspiration_volume == approx(expected_insp_volume, rel=0.1), msg
