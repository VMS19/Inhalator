import os

import pytest
from threading import Event

from pytest import approx

from algo import Sampler, VentilationState
from application import Application
from data.configurations import Configurations
from data.events import Events
from data.measurements import Measurements
from data.thresholds import O2Range, PressureRange, RespiratoryRateRange, \
    VolumeRange
from drivers.driver_factory import DriverFactory
from graphics.configure_alerts_screen import ConfigureAlarmsScreen

SAMPLES_AMOUNT = 604
EXPERIMENT_BPM = [0, 15, 15, 15, 15, 15, 15, 15]
EXPERIMENT_VOLUMES = [101, 288, 304, 292, 306, 295, 305, 290,
                      306, 289, 303, 291, 305, 293, 309]


@pytest.fixture
def driver_factory():
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, "03-04-2020.csv")
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
    c.log_enabled = False
    return c


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def events():
    return Events()


def test_sampler_volume_calculation(events, measurements, config, driver_factory):
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

    app.render()
    current_state = sampler.vsm.current_state
    for expected_volume in EXPERIMENT_VOLUMES:
        while current_state == sampler.vsm.current_state:
            app.run_iterations(1, render=False)

        current_state = sampler.vsm.current_state
        if current_state == VentilationState.Inhale:
            volume = measurements.expiration_volume

        else:
            volume = measurements.inspiration_volume

        msg = f"Received volume of {volume}, expected {expected_volume}"
        assert volume == approx(expected_volume, 0.2), msg

    app.root.destroy()


def test_sampler_bpm_calculation(events, measurements, config, driver_factory):
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

    app.render()
    for expected_bpm in EXPERIMENT_BPM:
        while sampler.vsm.current_state != VentilationState.Inhale:
            app.run_iterations(1, render=False)

        bpm = measurements.bpm
        msg = f"Received bpm of {bpm}, expected {expected_bpm}"
        assert bpm == approx(expected_bpm, 0.1), msg

        while sampler.vsm.current_state == VentilationState.Inhale:
            app.run_iterations(1, render=False)

    app.root.destroy()