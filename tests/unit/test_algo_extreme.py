import csv
import logging
import os
from itertools import cycle
from unittest.mock import Mock, patch

import pytest
from pytest import approx
from algo import Sampler, VentilationState
from data.configurations import Configurations
from data.events import Events
from data.measurements import Measurements
from data.thresholds import FlowRange, PressureRange, RespiratoryRateRange, \
    VolumeRange
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


@pytest.mark.xfail(reason="Can't handle extreme errors from sensors in peep")
def test_slope_recognition_with_error_in_peep(events, measurements, config):
    """Test error in peep doesn't cause the state machine change too early.

    Flow:
        * Run pig simulation with two errors in the peep stage
            - One error higher value
            - One error lower value
        * Check The entry time to inhale wasn't changed.

    Simulation graph:
                                        Pig simulation pressure graph

                                              XXXXXXXXXXXXXX
                                          XXXXX            XXX
             Check inhale entry         XXX                   XX
             time wasn't changed      XX                       X
                      |             XXX                        XX
          X           |            XX                           X
                      |          XX                             XX
                      |        XX                                X
                      |      XXX                                  X
                      |   XXX                                     X
                      vXXXX                                        X
        XX XXXXXXX XXXXX                                            XXXXXXXXXXXX


                  X

    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             "pig_sim_extreme_pressure_in_peep.csv")
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

    inhale_entry = sampler.vsm.entry_points_ts[VentilationState.Inhale][0]

    assert inhale_entry == approx(4.41, rel=0.1)


@pytest.mark.parametrize('scenario', ['low_error', 'high_error'])
def test_slope_recognition_with_error_in_inhale(events, measurements, config, scenario):
    """Test error in inhale doesn't cause the state machine change too early.

    Flow:
        * Run pig simulation with two errors in the inhale stage
            - One error higher value
            - One error lower value
        * Check The entry time to hold wasn't changed.

    Simulation graph:
                                Pig simulation pressure graph

                    X                     XXXXXXXXXXXXXX
     Check hold entry      +----------->XXX            XXX
     time wasn't changed            XXX                   XX
                                  XX                       X
                                XXX                        XX
                               XX                           X
                             XX                             XX
                           XX                                X
                         XXX                                  X
                      XXX                                     X
                   X XX                                        X
    XXXXXXXXXXXXXXXX                   X                        XXXXXXXXXXXX

    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             f"pig_sim_extreme_pressure_in_inhale_{scenario}.csv")
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

    hold_entry = sampler.vsm.entry_points_ts[VentilationState.Hold][0]

    assert hold_entry == approx(4.95, rel=0.1)


@pytest.mark.xfail(reason="Can't handle extreme errors from sensors in hold")
def test_slope_recognition_with_error_in_hold(events, measurements, config):
    """Test error in hold doesn't cause the state machine change too early.

    Flow:
        * Run pig simulation with two errors in the hold stage
            - One error higher value
            - One error lower value
        * Check The entry time to exhale wasn't changed.

    Simulation graph:
                                                     X

                                Pig simulation pressure graph
                                                                 Check exhale entry
                                          XXX XXXXXXX XX         time wasn't changed
                                       XXXX            XXX<-----+
                                    XXX                   XX
                                  XX                       X
                                XXX                        XX
                               XX                           X
                             XX                             XX
                           XX                                X
                         XXX                                  X
                      XXX                                     X
                   XXXX                                        X
    XXXXXXXXXXXXXXXX                         X                  XXXXXXXXXXXX

    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             "pig_sim_extreme_pressure_in_hold.csv")
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

    exhale_entry = sampler.vsm.entry_points_ts[VentilationState.Exhale][0]

    assert exhale_entry == approx(6.07, rel=0.1)


@pytest.mark.parametrize('scenario', ['low_error', 'high_error'])
def test_slope_recognition_with_error_in_exhale(events, measurements, config, scenario):
    """Test error in exhale doesn't cause the state machine change too early.

    Flow:
        * Run pig simulation with two errors in the exhale stage
            - One error higher value
            - One error lower value
        * Check The entry time to peep wasn't changed.

    Simulation graph:
                                Pig simulation pressure graph

                                          XXXXXXXXXXXXXX       X
                                       XXXX            XX
                                    XXX                   XX
                                  XX                       X
                                XXX                        XX       Check peep entry
                               XX                           X       time wasn't changed
                             XX                             XX  +-->
                           XX                                X  |
                         XXX                                  X |
                      XXX                                     X |
                   XXXX                                         +
    XXXXXXXXXXXXXXXX                                     X      XXXXXXXXXXXX

    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             f"pig_sim_extreme_pressure_in_exhale_{scenario}.csv")
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

    peep_entry = sampler.vsm.entry_points_ts[VentilationState.PEEP][0]

    assert peep_entry == approx(6.615, rel=0.1)