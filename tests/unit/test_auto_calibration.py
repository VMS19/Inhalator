import os

import pytest

from drivers.driver_factory import DriverFactory
from drivers.mocks.sensor import DifferentialPressureMockSensor
from drivers.mocks.timer import MockTimer
from logic.auto_calibration import TailDetector
from tests.data.files import path_to_file

SIMULATION_FOLDER = "simulation"


@pytest.mark.parametrize("data", [path_to_file("single_step_cycle.csv")])
@pytest.mark.parametrize("offset", range(-7, 7))
def test_single_cycle_tail_detection(offset, data, driver_factory):
    dp_driver: DifferentialPressureMockSensor = driver_factory.flow
    timer: MockTimer = driver_factory.timer
    detector = TailDetector(dp_driver,
                            sample_threshold=5,
                            slope_threshold=10,
                            min_tail_length=6,
                            grace_length=5)

    dp_driver.offset_drift = offset
    for _ in dp_driver.seq:
        ts = timer.get_time()
        flow_slm = dp_driver.read()

        detector.add_sample(flow_slm, ts)

    result = detector.process()
    assert result == pytest.approx(offset, rel=0.001)


@pytest.mark.parametrize("data", [path_to_file("single_cycle_good.csv")])
def test_single_cycle_tail_ts(data, driver_factory):
    dp_driver: DifferentialPressureMockSensor = driver_factory.flow
    timer: MockTimer = driver_factory.timer
    detector = TailDetector(dp_driver,
                            sample_threshold=5,
                            slope_threshold=10,
                            min_tail_length=6,
                            grace_length=5)

    for _ in dp_driver.seq:
        ts = timer.get_time()
        flow_slm = dp_driver.read()

        detector.add_sample(flow_slm, ts)

    detector.process()
    assert len(detector.start_tails_ts) == len(detector.end_tails_ts) == 1, \
        "only one tail should be found"

    tail = detector.start_tails_ts[0], detector.end_tails_ts[0]
    assert tail == (27.562, 27.863)
