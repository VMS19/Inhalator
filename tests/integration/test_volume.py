import os

import pytest
from threading import Event

from pytest import approx

from algo import Sampler
from application import Application
from data.alert import AlertCodes
from data.configurations import Configurations
from data.events import Events
from data.measurements import Measurements
from data.thresholds import O2Range, PressureRange, RespiratoryRateRange, \
    VolumeRange
from drivers.driver_factory import DriverFactory

SIMULATION_FOLDER = "simulation"

FAST_FORWARD = 100
LOW_THRESHOLD = -50000
HIGH_THRESHOLD = 50000
SIMULATION_SAMPLES = 1000


@pytest.fixture
def driver_factory():
    return DriverFactory(simulation_mode=True, simulation_data="sinus")


@pytest.fixture
def config():
    c = Configurations.instance()
    c.o2_range = O2Range(min=0, max=100)
    c.pressure_range = PressureRange(min=-1, max=30)
    c.resp_rate_range = RespiratoryRateRange(min=0, max=30)
    c.volume_range = VolumeRange(min=100, max=600)
    c.graph_seconds = 12
    c.breathing_threshold = 3.5
    c.log_enabled = False
    return c


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def events():
    return Events()


def test_sampler_volume_calculation(events, measurements, config):
    """Test volume calculation working correctly.

    Flow:
        * Run pig simulation which contain one breath cycle.
        * Simulate constant flow of 1.
        * Validate expected volume.
    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, SIMULATION_FOLDER,
                             "pig_sim_cycle.csv")
    driver_factory = DriverFactory(simulation_mode=True,
                                   simulation_data=file_path)

    arm_wd_event = Event()
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer)

    app = Application(measurements=measurements,
                      events=events,
                      arm_wd_event=arm_wd_event,
                      drivers=driver_factory,
                      sampler=sampler,
                      simulation=True)

    app.run_iterations(SIMULATION_SAMPLES)
    app.root.destroy()

    expected_volume = 332
    msg = f"Expected volume of {expected_volume}, received {measurements.inspiration_volume}"
    assert measurements.inspiration_volume == approx(expected_volume, rel=0.1), msg


def test_sampler_alerts_when_volume_exceeds_minium(events, measurements, config, driver_factory):
    arm_wd_event = Event()
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer)

    app = Application(measurements=measurements,
                      events=events,
                      arm_wd_event=arm_wd_event,
                      drivers=driver_factory,
                      sampler=sampler,
                      simulation=True)

    assert len(events.alerts_queue) == 0
    app.run_iterations(1)
    assert len(events.alerts_queue) == 0

    config.volume_range = VolumeRange(HIGH_THRESHOLD, HIGH_THRESHOLD)
    app.run_iterations(SIMULATION_SAMPLES)
    app.root.destroy()

    assert len(events.alerts_queue) > 0

    all_alerts = list(events.alerts_queue)
    assert all(alert == AlertCodes.VOLUME_LOW for alert in all_alerts)


def test_sampler_alerts_when_volume_exceeds_maximum(events, measurements, config, driver_factory):
    arm_wd_event = Event()
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer)

    app = Application(measurements=measurements,
                      events=events,
                      arm_wd_event=arm_wd_event,
                      drivers=driver_factory,
                      sampler=sampler,
                      simulation=True,)

    assert len(events.alerts_queue) == 0
    app.run_iterations(1, fast_forward=True)
    assert len(events.alerts_queue) == 0

    config.volume_range = VolumeRange(LOW_THRESHOLD, LOW_THRESHOLD)
    app.run_iterations(SIMULATION_SAMPLES)
    app.root.destroy()

    assert len(events.alerts_queue) > 0

    all_alerts = list(events.alerts_queue)
    assert all(alert == AlertCodes.VOLUME_HIGH for alert in all_alerts)