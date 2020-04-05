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
from data.thresholds import O2Range, PressureRange, RespiratoryRateRange, \
    VolumeRange
from drivers.driver_factory import DriverFactory


SAMPLES_AMOUNT = 118
SIMULATION_FOLDER = "simulation"


@pytest.fixture
def config():
    c = Configurations.instance()
    c.o2_range = O2Range(min=0, max=100)
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


@pytest.mark.parametrize("scenario", ['pressure', 'flow',
                                      pytest.param('both',marks=pytest.mark.xfail(reason="Can't handle simultaneous error in pressure and flow"))])
def test_slope_recognition_with_error_in_exhale(events, measurements, config, scenario):
    """Test error in exhale doesn't cause the state machine change too early.

    Flow:
        * Run pig simulation with two errors in the peep exhale
            - One error higher value (pressure, flow or together)
            - One error lower value (pressure, flow or together)
        * Check The entry time to inhale wasn't changed.

    Simulation graphs:
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

                               Pig simulation flow graph

                                         X
                                       XXXX
               Check inhale entry     XX  X
               time wasn't changed   XX   X
                                    XX     X
                         +         XX      XXX
           X             |       XXX         XX
                         |     XXX            XXX
                         |    XX                XXXXX
                         |   XX                     XXXXXXX
                         | XXX                             XXXXXXX
                         vXX                                     XXXXXX
        XXX XXXXXXXX XXXXX                                            XXXXXXXXXX

                    X
    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             f"pig_sim_extreme_in_exhale_{scenario}.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)

    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer)

    for _ in range(SAMPLES_AMOUNT):
        sampler.sampling_iteration()

    inhale_entry = sampler.vsm.entry_points_ts[VentilationState.Inhale][0]

    assert inhale_entry == approx(4.41, rel=0.1)


# pytest.mark.xfail("Can't handle error of drop in flow below threshold")
@pytest.mark.parametrize("scenario", ['below',
                                      pytest.param('pass', marks=pytest.mark.xfail(reason="Can't handle error of drop in flow below threshold"))])
def test_slope_recognition_with_error_in_inhale(events, measurements, config, scenario):
    """Test error in inhale doesn't cause the state machine change too early.

    Flow:
        * Run pig simulation with two errors in the inhale stage
            - One error low value while increasing
            - One error low value while decreasing
            * Each of the errors once passing -2 threshold, and once not.
        * Check The entry time to peep wasn't changed.

    Simulation graph:
                               Pig simulation flow graph

                                         X
                                       XXXX
                                      XX  X
                                     XX   X                Check exhale entry
                                    XX     X               time wasn't changed
                                   XX      XXX
                                  XX         XX                        +
                               XX             XXX                      |
                              XX                XXX X                  |
                             XX                     XXXXXXX            |
                           XXX                             XXXXXXX     |
                          XX     Xbelow            Xbelow        XXXXXXv
        XXXXXXXXXXXXXXXXXX                                            XXXXXXXXXX

                                 Xpass             Xpass
    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             f"pig_sim_extreme_in_inhale_{scenario}_threshold.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)

    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer)

    for _ in range(SAMPLES_AMOUNT):
        sampler.sampling_iteration()

    peep_entry = sampler.vsm.entry_points_ts[VentilationState.Exhale][0]

    assert peep_entry == approx(6.09, rel=0.1)
