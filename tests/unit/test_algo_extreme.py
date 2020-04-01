import csv
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

this_dir = os.path.dirname(__file__)
with open(os.path.join(this_dir, "pig_sim_extreme_pressure_in_peep.csv"), "r") as f:
    data = list(csv.reader(f))
timestamps = [float(d[0]) for d in data[1:]]
timestamps = timestamps[
             :1] + timestamps  # first timestamp for InhaleStateHandler init
DATA_SIZE = len(data) - 1

time_mock = Mock()
time_mock.side_effect = cycle(timestamps)


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


@pytest.mark.xfail(reason="Can't handle extreme errors from sensors")
@patch('time.time', time_mock)
def test_slope_recognition_with_error(events, measurements, config):
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir,
                             "pig_sim_extreme_pressure_in_peep.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)

    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      oxygen_a2d)

    for i in range(DATA_SIZE):
        sampler.sampling_iteration()

    inhale_entry = sampler.vsm.entry_points_ts[VentilationState.Inhale][0]

    assert inhale_entry == approx(4.41, rel=0.1)