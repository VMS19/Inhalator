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
@pytest.mark.parametrize("interval, iteration_len, count",
                         [(100, 4, 2), (1800, 4, 1), (50, 2, 4)])
def test_calibration_timing(mock_pressure, mock_tail, interval, iteration_len,
                            count, sim_sampler):
    sim_sampler.auto_calibrator.interval_length = interval
    sim_sampler.auto_calibrator.iteration_length = iteration_len

    for i in range(10000):
        sim_sampler.sampling_iteration()

    assert mock_pressure.call_count == count
    


