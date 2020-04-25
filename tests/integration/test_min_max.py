import pytest
from pytest import approx

from drivers.driver_factory import DriverFactory

from tests.data.files import path_to_file

SAMPLES_IN_SINUS_CYCLE = DriverFactory.MOCK_SAMPLE_RATE_HZ * int(60 / DriverFactory.MOCK_BPM)
TEST_FILE = path_to_file("2020-04-12-sheba-trial-single-cycle.csv")
SAMPLES_IN_TEST_FILE = 86


@pytest.mark.parametrize(
    ["data", "iterations", "min_pressure", "max_pressure", "max_flow"],
    [("dead", SAMPLES_IN_SINUS_CYCLE, 0, 0, 0),
     ("noiseless_sinus", SAMPLES_IN_SINUS_CYCLE,
      DriverFactory.MOCK_PEEP,
      DriverFactory.MOCK_PRESSURE_AMPLITUDE,
      DriverFactory.MOCK_AIRFLOW_AMPLITUDE),
     (TEST_FILE, SAMPLES_IN_TEST_FILE, 7.873, 20.419, 45.636)])
def test_min_max(app, measurements, data, iterations, min_pressure,
                 max_pressure, max_flow, config):
    """Test dead simulation results with min & max equal 0

    Flow:
        * Run dead simulation for SIMULATION_LENGTH
        * check min & max pressure = 0
        * check max flow = 0
    """
    config.thresholds.pressure.min = min_pressure - 1
    # We run 2 iteration because min values are recorded at Inhale entry.
    # So we need to enter Inhale 2nd time to record the min values of Exhale.
    app.run_iterations(iterations * 2)
    min_pressure_msg = f"Expected min pressure of {min_pressure}," \
                       f" received {measurements.peep_min_pressure}"
    assert measurements.peep_min_pressure == approx(min_pressure, rel=0.01), min_pressure_msg

    max_pressure_msg = f"Expected max pressure of {max_pressure}," \
                       f" received {measurements.intake_peak_pressure}"
    assert measurements.intake_peak_pressure == approx(max_pressure, rel=0.01), max_pressure_msg

    max_flow_msg = f"Expected max flow of {max_flow}," \
                   f" received {measurements.intake_peak_flow}"
    assert measurements.intake_peak_flow == approx(max_flow, rel=0.01), max_flow_msg
