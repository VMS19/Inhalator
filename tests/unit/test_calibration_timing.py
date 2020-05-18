import pytest
from unittest.mock import patch

from drivers.driver_factory import DriverFactory
from drivers.mocks.sensor import DifferentialPressureMockSensor
from logic.auto_calibration import TailDetector


@pytest.fixture
def driver_factory():
    return DriverFactory(simulation_mode=True, simulation_data="sinus")


@patch("logic.auto_calibration.TailDetector.process")
@patch("drivers.mocks.sensor.DifferentialPressureMockSensor.get_calibration_offset")
@pytest.mark.parametrize("interval, iteration_len, get_offset_count, process_count",
                         [(100, 4, 10, 40), (1800, 4, 1, 4), (50, 2, 20, 80)])
def test_calibration_timing(mock_pressure, mock_tail, interval, iteration_len,
                            get_offset_count, process_count, sim_sampler):
    calibrator = sim_sampler.auto_calibrator

    calibrator.interval_length = interval
    calibrator.iteration_length = iteration_len

    for i in range(1000):
        calibrator.get_offset(None, i)

    assert mock_pressure.call_count == get_offset_count
    assert mock_tail.call_count == process_count
    
