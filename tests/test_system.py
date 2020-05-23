import os
import time
from datetime import datetime
from argparse import Namespace
from unittest.mock import patch

import pytest

from main import start_app
from tests.data.files import path_to_file
from tests.utils import SamplesCSVParser
from drivers.driver_factory import generate_data_from_file


PRESSURE = 1
FLOW = 2

RECORDED_SAMPLES = "inhalator.csv"
TIME_ITERATIONS = 500000
SAMPLES_NAMES = ["pig_sim_extreme_in_exhale_both.csv", 
                 "pig_sim_extreme_in_inhale_below_threshold.csv",
                 "pig_sim_extreme_in_inhale_pass_threshold.csv"]


class ErrorAfter:
    """
    Callable that will raise `KeyboardInterrupt`
    exception after `limit` calls
    """
    def __init__(self, limit):
        self.limit = limit
        self.calls = 0

    def __call__(self, _seconds=None):
        self.calls += 1
        if self.calls > self.limit:
            self.calls = 0
            raise KeyboardInterrupt
        return datetime.timestamp(datetime.now())


class InhalatorCSVParser():
    def __init__(self, sensors):
        self.data = [generate_data_from_file(sensor, RECORDED_SAMPLES)
                     for sensor in sensors]

    def samples(self):
        return [next(sensor) for sensor in self.data]


@pytest.mark.parametrize("csv_name", SAMPLES_NAMES)
@patch("time.time", side_effect=ErrorAfter(TIME_ITERATIONS))
def test_main_loop_values(time_mock, csv_name):
    """Run the main loop and makes sure nothing breaks.
    
    Play a simulation using the app, record the samples and verify them.
    """
    try:
        os.remove(RECORDED_SAMPLES)
    except FileNotFoundError:
        pass

    args = Namespace(error=0, fps=25, memory_usage_output=None,
                     record_sensors=1, sample_rate=22,
                     simulate=path_to_file(csv_name), verbose=30)

    start_app(args)

    sampler_parser = SamplesCSVParser(path_to_file(csv_name))
    inhalator_parser = InhalatorCSVParser(["pressure", "flow"])

    for _time, pressure, flow, _oxygen in sampler_parser.samples(start=0, end=170):
        recorded_pressure, recorded_flow = inhalator_parser.samples()

        assert pressure == pytest.approx(recorded_pressure)
        assert flow == pytest.approx(recorded_flow, abs=1)
