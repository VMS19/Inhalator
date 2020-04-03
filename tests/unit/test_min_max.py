import csv
import logging
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

SAMPLES_AMOUNT = 118
SIMULATION_FOLDER = "simulation"


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
    """Test dead simulation results with min & max equal 0

    Flow:
        * Run dead simulation for SIMULATION_LENGTH
        * check min & max pressure = 0
        * check max flow = 0
    """
    driver_factory = DriverFactory(simulation_mode=True, simulation_data="dead")
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    oxygen_a2d = driver_factory.acquire_driver("oxygen_a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      oxygen_a2d, timer)

    for _ in range(SAMPLES_AMOUNT):
        sampler.sampling_iteration()

    min_pressure_msg = f"Expected min pressure of 0, received {measurements.peep_min_pressure}"
    assert measurements.peep_min_pressure == 0, min_pressure_msg

    max_pressure_msg = f"Expected max pressure of 0, received {measurements.intake_peak_pressure}"
    assert measurements.intake_peak_pressure == 0, max_pressure_msg

    max_flow_msg = f"Expected max flow of 0, received {measurements.intake_peak_flow}"
    assert measurements.intake_peak_flow == 0, max_flow_msg


def test_sampler_sinus_min_max(events, measurements, config):
    """Test sinus sim results in min & max approx the amplitude

    Flow:
        * start sinus simulation
        * check min pressure ~ 0
        * check max pressure ~ PRESSURE_AMPLITUDE
        * check max flow ~ FLOW_AMPLITUDE
    """
    driver_factory = DriverFactory(simulation_mode=True, simulation_data="noiseless_sinus")
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    oxygen_a2d = driver_factory.acquire_driver("oxygen_a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      oxygen_a2d, timer)

    for _ in range(SAMPLES_AMOUNT):
        sampler.sampling_iteration()

    expected_min_pressure = driver_factory.MOCK_PEEP
    min_pressure_msg = f"Expected min pressure be {expected_min_pressure}, " \
                       f"received {measurements.peep_min_pressure}"
    assert measurements.peep_min_pressure == expected_min_pressure, min_pressure_msg

    expected_pressure = driver_factory.MOCK_PRESSURE_AMPLITUDE
    max_pressure_msg = f"Expected max pressure be {expected_pressure}, " \
                       f"received {measurements.intake_peak_pressure}"
    assert measurements.intake_peak_pressure == expected_pressure, max_pressure_msg

    expected_flow = driver_factory.MOCK_AIRFLOW_AMPLITUDE
    max_flow_msg = f"Expected max flow be {expected_flow}, " \
                       f"received {measurements.intake_peak_flow}"
    assert measurements.intake_peak_flow == expected_flow, max_flow_msg


def test_sampler_pig_min_max(events, measurements, config):
    """Test volume calculation working correctly.
    Flow:
        * Run pig simulation with sinus flow in range (0,40) i.e:
            Using pressure graph from pig simulation and creating a sinus
            graph for flow with minimum value of 0 and maximum of 40.
        * Validate min & max for pressure and flow.

    Note:
        Min values are read at the first peep exit at timestamp 4.455 (including)
        Max values are read at the first hold exit at timestamp 6.075 (including)

    Simulation graph:
                                        Pig simulation pressure graph

                                              XXXXXXXXXXXXXX    read maximum value
                                          XXXXX            XXX<------------+
                                        XXX                   XX
                                      XX                       X
         read minimum pressure      XXX                        XX
                      +            XX                           X
                      |          XX                             XX
                      |        XX                                X
                      |      XXX                                  X
                      |   XXX                                     X
                      vXXXX                                        X
        XXXXXXXXXXXXXXXX                                            XXXXXXXXXXXX

    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             "pig_sim_sin_flow.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)

    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    oxygen_a2d = driver_factory.acquire_driver("oxygen_a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      oxygen_a2d, timer)

    for _ in range(SAMPLES_AMOUNT):
        sampler.sampling_iteration()

    expected_min_pressure = approx(0.240899428, rel=0.01)
    min_pressure_msg = f"Expected min pressure of {expected_min_pressure}, " \
                       f"received {measurements.peep_min_pressure}"
    assert measurements.peep_min_pressure == expected_min_pressure, min_pressure_msg

    expected_max_pressure = approx(20.40648936, rel=0.1)
    max_pressure_msg = f"Expected max pressure of {expected_max_pressure}, " \
                       f"received {measurements.intake_peak_pressure}"
    assert measurements.intake_peak_pressure == expected_max_pressure, max_pressure_msg

    expected_max_flow = approx(36.90266823, rel=0.1)
    max_flow_msg = f"Expected max flow of {expected_max_flow}, " \
                   f"received {measurements.intake_peak_flow}"
    assert measurements.intake_peak_flow == expected_max_flow, max_flow_msg
