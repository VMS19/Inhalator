import os

import pytest
from threading import Event

from pytest import approx

from algo import Sampler
from application import Application
from data import alerts
from data.configurations import Configurations
from data.events import Events
from data.measurements import Measurements
from data.thresholds import O2Range, PressureRange, RespiratoryRateRange, \
    VolumeRange
from drivers.driver_factory import DriverFactory

SIMULATION_FOLDER = "simulation"

OFFSET = 3
SIMULATION_SAMPLES = 660


@pytest.fixture
def driver_factory():
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             "sampling.csv")
    return DriverFactory(simulation_mode=True, simulation_data=file_path)


@pytest.fixture
def config():
    c = Configurations.instance()
    c.o2_range = O2Range(min=0, max=100)
    c.pressure_range = PressureRange(min=-1, max=30)
    c.resp_rate_range = RespiratoryRateRange(min=0, max=30)
    c.volume_range = VolumeRange(min=100, max=600)
    c.graph_seconds = 12
    c.breathing_threshold = 3.5
    c.min_exp_volume_for_exhale = 0
    c.log_enabled = False
    c.boot_alert_grace_time = 0
    return c


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def events():
    return Events()


@pytest.fixture
def sampler(events, measurements, driver_factory):
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    return Sampler(measurements, events, flow_sensor, pressure_sensor, a2d, timer)


@pytest.fixture
def app(measurements, events, driver_factory, sampler):
    app = Application(
        measurements=measurements,
        events=events,
        arm_wd_event=Event(),
        drivers=driver_factory,
        sampler=sampler,
        simulation=True)
    yield app
    app.root.destroy()


def test_auto_calibration(measurements, app):
    app.run_iterations(SIMULATION_SAMPLES * 2)

    volume_diff = abs(measurements.inspiration_volume - measurements.expiration_volume)
    msg = f"Expected volumes diff to be close to 0, received {volume_diff}"
    assert volume_diff < DIFF_THRESHOLD, msg
