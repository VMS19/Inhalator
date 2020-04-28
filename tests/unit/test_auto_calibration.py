import os

import pytest

from data.configurations import Configurations
from drivers.driver_factory import DriverFactory
from drivers.mocks.sensor import DifferentialPressureMockSensor
from drivers.mocks.timer import MockTimer
from logic.auto_calibration import TailDetector

SIMULATION_FOLDER = "simulation"


@pytest.mark.parametrize('offset', range(-7, 7))
def test_single_cycle_tail_detection(offset):
    c = Configurations.instance()
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             "single_step_cycle.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)
    dp_driver: DifferentialPressureMockSensor = driver_factory.acquire_driver("flow")
    timer: MockTimer = driver_factory.acquire_driver("timer")
    detector = TailDetector(dp_driver,
                            sample_threshold=c.auto_cal_sample_threshold,
                            slope_threshold=c.auto_cal_slope_threshold,
                            min_tail_length=6,
                            grace_length=c.auto_cal_grace_length)

    dp_driver.set_offset_drift(offset)
    for _ in dp_driver.seq:
        ts = timer.get_time()
        flow_slm = dp_driver.read()

        detector.add_sample(flow_slm, ts)

    result = detector.process()
    assert result == pytest.approx(offset, rel=0.001)
