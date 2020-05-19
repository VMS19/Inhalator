import pytest
from unittest.mock import patch

from logic.auto_calibration import TailDetector, AutoFlowCalibrator
from drivers.driver_factory import DriverFactory


@pytest.fixture
def calibrator():
    return AutoFlowCalibrator(
        dp_driver=DriverFactory(True).acquire_driver("differential_pressure"),
        interval_length=100,
        iterations=4,
        iteration_length=4,
        sample_threshold=8.0,
        slope_threshold=10.0,
        min_tail_length=12,
        grace_length=5,
    )

@patch("logic.auto_calibration.TailDetector.process")
@patch("drivers.mocks.sensor.DifferentialPressureMockSensor.get_calibration_offset")
def test_calibration_timing_interval(mock_pressure, mock_tail, calibrator):
    for i in range(1000):
        calibrator.get_offset(None, i)

    assert mock_pressure.call_count == 10


@patch("logic.auto_calibration.TailDetector.process")
@patch("drivers.mocks.sensor.DifferentialPressureMockSensor.get_calibration_offset")
def test_calibration_process_timing(mock_pressure, mock_tail, calibrator):
    for i in range(1000):
        calibrator.get_offset(None, i)

    assert mock_tail.call_count == 40
