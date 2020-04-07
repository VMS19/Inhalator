import pytest
from pytest import approx

from data.measurements import Measurements
from data.events import Events
from data.configurations import Configurations
from data.thresholds import (O2Range, PressureRange,
                             RespiratoryRateRange, VolumeRange)
from drivers.driver_factory import DriverFactory
from tests.unit.conftest import create_sampler

SAMPLES_AMOUNT = 118


@pytest.fixture
def config():
    c = Configurations.instance()
    c.o2_range = O2Range(min=0, max=100)
    c.pressure_range = PressureRange(min=0, max=30)
    c.resp_rate_range = RespiratoryRateRange(min=0, max=30)
    c.volume_range = VolumeRange(min=0, max=30)
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


def test_sampler_dead_min_max(events, measurements):
    """Test dead simulation results with min & max equal 0

    Flow:
        * Run dead simulation for SIMULATION_LENGTH
        * check min & max pressure = 0
        * check max flow = 0
    """
    sampler = create_sampler("dead", events, measurements)
    for _ in range(SAMPLES_AMOUNT):
        sampler.sampling_iteration()

    min_pressure_msg = f"Expected min pressure of 0, received {measurements.peep_min_pressure}"
    assert measurements.peep_min_pressure == 0, min_pressure_msg

    max_pressure_msg = f"Expected max pressure of 0, received {measurements.intake_peak_pressure}"
    assert measurements.intake_peak_pressure == 0, max_pressure_msg

    max_flow_msg = f"Expected max flow of 0, received {measurements.intake_peak_flow}"
    assert measurements.intake_peak_flow == 0, max_flow_msg


def test_sampler_sinus_min_max(events, measurements):
    """Test sinus sim results in min & max approx the amplitude

    Flow:
        * start sinus simulation
        * check min pressure ~ 0
        * check max pressure ~ PRESSURE_AMPLITUDE
        * check max flow ~ FLOW_AMPLITUDE
    """
    sampler = create_sampler("noiseless_sinus", events, measurements)
    for _ in range(SAMPLES_AMOUNT):
        sampler.sampling_iteration()

    expected_min_pressure = DriverFactory.MOCK_PEEP
    min_pressure_msg = f"Expected min pressure be {expected_min_pressure}, " \
                       f"received {measurements.peep_min_pressure}"
    assert measurements.peep_min_pressure == expected_min_pressure, min_pressure_msg

    expected_pressure = DriverFactory.MOCK_PRESSURE_AMPLITUDE
    max_pressure_msg = f"Expected max pressure be {expected_pressure}, " \
                       f"received {measurements.intake_peak_pressure}"
    assert measurements.intake_peak_pressure == expected_pressure, max_pressure_msg

    expected_flow = DriverFactory.MOCK_AIRFLOW_AMPLITUDE
    max_flow_msg = f"Expected max flow be {expected_flow}, " \
                   f"received {measurements.intake_peak_flow}"
    assert measurements.intake_peak_flow == expected_flow, max_flow_msg


def test_sampler_pig_min_max(events, measurements):
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
    sampler = create_sampler("pig_sim_cycle.csv", events, measurements)

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

    expected_max_flow = approx(31.7, rel=0.1)
    max_flow_msg = f"Expected max flow of {expected_max_flow}, " \
                   f"received {measurements.intake_peak_flow}"
    assert measurements.intake_peak_flow == expected_max_flow, max_flow_msg
