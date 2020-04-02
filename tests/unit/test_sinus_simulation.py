import csv
import os
import time

import pytest

from algo import Sampler, VentilationStateMachine
from data.measurements import Measurements
from data.events import Events
from data.configurations import Configurations
from data.thresholds import (FlowRange, PressureRange,
                             RespiratoryRateRange, VolumeRange)
from drivers.driver_factory import DriverFactory
from drivers.mocks.sensor import MockSensor


@pytest.fixture
def driver_factory():
    return DriverFactory(simulation_mode=True, simulation_data="sinus")


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


def test_sampler_alerts_when_pressure_exceeds_maximum(events, measurements, config, driver_factory):
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor, oxygen_a2d)

    for _ in range(1000):
        time.sleep(0.001)
        sampler.sampling_iteration()
        print("pressure:", list(measurements.pressure_measurements.queue)[0])
        print("\tCurrent state:", sampler.vsm.current_state)


@pytest.fixture
def real_data():
    this_dir = os.path.dirname(__file__)
    with open(os.path.join(this_dir, "a.csv"), "r") as f:
        reader = csv.DictReader(f)
        t = [float(row['timestamp']) for row in reader]

    with open(os.path.join(this_dir, "a.csv"), "r") as f:
        reader = csv.DictReader(f)
        v = [float(row['pressure']) for row in reader]
    return t, v


def test_correct_state_transitions(real_data):
    t, v = real_data
    vsm = VentilationStateMachine(Measurements(), Events())
    for timestamp, pressure in zip(t, v):
        vsm.update(
            pressure_cmh2o=pressure,
            flow_slm=0,
            o2_saturation_percentage=0,
            timestamp=timestamp)
        print("pressure:", list(vsm._measurements.pressure_measurements.queue)[0])
        print("\tCurrent state:", vsm.current_state)