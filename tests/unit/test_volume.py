import os
import csv
from itertools import cycle
from unittest.mock import Mock, patch

import pytest

from algo import Sampler
from data.configurations import Configurations
from data.events import Events
from data.measurements import Measurements
from data.thresholds import FlowRange, PressureRange, RespiratoryRateRange, \
    VolumeRange
from drivers.driver_factory import DriverFactory


DATA_SIZE = 118

this_dir = os.path.dirname(__file__)
with open(os.path.join(this_dir, "pig_sim.csv"), "r") as f:
    data = list(csv.reader(f))
timestamps = [float(d[0]) for d in data[1:]]
timestamps = timestamps[:1] + timestamps  # first timestamp for InhaleStateHandler init
time_mock = Mock()
time_mock.side_effect = cycle(timestamps)
t = cycle(timestamps)
# import ipdb;
#
# import inspect
# def f():
#     x = next(t)
#     print(x)
#     curframe = inspect.currentframe()
#     calframe = inspect.getouterframes(curframe, 30)
#     # ipdb.set_trace()
#     # print('caller name:', calframe[1][3])
#     return x
#
# time_mock.side_effect = f


@pytest.fixture
def driver_factory():
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, "pig_sim.csv")
    return DriverFactory(simulation_mode=True, simulation_data=file_path)


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


@pytest.fixture
def real_data():
    this_dir = os.path.dirname(__file__)
    with open(os.path.join(this_dir, "pressure_data_pig.csv"), "r") as f:
        data = list(csv.reader(f))
    timestamps = [float(d[0]) for d in data]
    pressure = [float(d[1]) for d in data]
    return timestamps, pressure


@patch('time.time', time_mock)
def test_sampler_alerts_when_volume_exceeds_maximum(events, measurements, config, driver_factory):
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      oxygen_a2d)

    for _ in range(DATA_SIZE):
        sampler.sampling_iteration()
        # print(measurements.volume)