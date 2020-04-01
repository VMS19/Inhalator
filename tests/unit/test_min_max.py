import csv
import os
import time
from itertools import cycle
from unittest.mock import Mock, patch

import pytest
from pytest import approx

from algo import Sampler
from data.measurements import Measurements
from data.events import Events
from data.configurations import Configurations
from data.thresholds import (FlowRange, PressureRange,
                             RespiratoryRateRange, VolumeRange)
from drivers.driver_factory import DriverFactory


MICROSECOND = 10 ** -6
SIMULATION_LENGTH = 2  # seconds


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


def test_sampler_dead_min_max(events, measurements, config):
    driver_factory = DriverFactory(simulation_mode=True, simulation_data="dead")
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor, oxygen_a2d)

    current_time = time.time()
    while time.time() - current_time < SIMULATION_LENGTH:
        time.sleep(MICROSECOND)
        sampler.sampling_iteration()

    min_pressure_msg = f"Expected min pressure of 0, received {measurements.peep_min_pressure}"
    assert measurements.peep_min_pressure == 0, min_pressure_msg

    max_pressure_msg = f"Expected max pressure of 0, received {measurements.intake_peak_pressure}"
    assert measurements.intake_peak_pressure == 0, max_pressure_msg

    max_flow_msg = f"Expected max flow of 0, received {measurements.intake_peak_flow}"
    assert measurements.intake_peak_flow == 0, max_flow_msg


def test_sampler_sinus_min_max(events, measurements, config):
    driver_factory = DriverFactory(simulation_mode=True, simulation_data="dead")
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor, oxygen_a2d)

    current_time = time.time()
    while time.time() - current_time < SIMULATION_LENGTH:
        time.sleep(MICROSECOND)
        sampler.sampling_iteration()

    noise_mistake = 2.0  # the probability for noise bigger then 2 is almost 0

    min_pressure_msg = f"Expected min pressure in range [{-noise_mistake}," \
                       f"{noise_mistake}], received {measurements.peep_min_pressure}"
    assert measurements.peep_min_pressure == approx(0, rel=noise_mistake), min_pressure_msg

    expected_pressure = driver_factory.MOCK_PRESSURE_AMPLITUDE
    max_pressure_msg = f"Expected max pressure in range " \
                       f"[{expected_pressure - noise_mistake}," \
                       f" {expected_pressure + noise_mistake}], " \
                       f"received {measurements.intake_peak_pressure}"
    assert measurements.intake_peak_pressure == approx(expected_pressure,
                                                       rel=noise_mistake), max_pressure_msg

    expected_flow = driver_factory.MOCK_AIRFLOW_AMPLITUDE
    max_flow_msg = f"Expected max flow in range " \
                       f"[{expected_flow - noise_mistake}," \
                       f" {expected_flow + noise_mistake}], " \
                       f"received {measurements.intake_peak_flow}"
    assert measurements.intake_peak_flow == approx(expected_flow,
                                                   rel=noise_mistake), max_flow_msg




this_dir = os.path.dirname(__file__)
with open(os.path.join(this_dir, "pig_sim_sin_flow.csv"), "r") as f:
    data = list(csv.reader(f))
timestamps = [float(d[0]) for d in data[1:]]
timestamps = timestamps[
             :1] + timestamps  # first timestamp for InhaleStateHandler init
DATA_SIZE = len(data) - 1

time_mock = Mock()
time_mock.side_effect = cycle(timestamps)


@patch('time.time', time_mock)
def test_sampler_pig_min_max(events, measurements, config):
    """Test volume calculation working correctly.
    Flow:
        * Run pig simulation with sinus flow in range (0,40).
        * Validate min & max for pressure and flow.

    Note:
        Min values are read at the first peep exit at timestamp 4.455 (not including)
        Max values are read at the first hold exit at timestamp 6.075 (not including)
    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, "pig_sim_sin_flow.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)

    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      oxygen_a2d)

    for i in range(DATA_SIZE):
        sampler.sampling_iteration()

    expected_min_pressure = 0.240899428
    min_pressure_msg = f"Expected min pressure of {expected_min_pressure}, " \
                       f"received {measurements.peep_min_pressure}"
    assert measurements.peep_min_pressure == expected_min_pressure, min_pressure_msg

    expected_max_pressure = 20.40648936
    max_pressure_msg = f"Expected max pressure of {expected_max_pressure}, " \
                       f"received {measurements.intake_peak_pressure}"
    assert measurements.intake_peak_pressure == expected_max_pressure, max_pressure_msg

    expected_max_flow = 36.30099079
    max_flow_msg = f"Expected max flow of {expected_max_flow}, " \
                   f"received {measurements.intake_peak_flow}"
    assert measurements.intake_peak_flow == expected_max_flow, max_flow_msg


