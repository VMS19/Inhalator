import os

import pytest
from threading import Event

from algo import Sampler
from application import Application
from data import alerts
from data.configurations import Configurations
from data.events import Events
from data.measurements import Measurements
from data.thresholds import O2Range, PressureRange, RespiratoryRateRange, \
    VolumeRange
from drivers.driver_factory import DriverFactory
from graphics.configure_alerts_screen import ConfigureAlarmsScreen

SAMPLES_AMOUNT = 604

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


@pytest.mark.parametrize("alert_type", ['pressure', 'volume', 'oxygen'])
def test_sampler_alerts_when_sensor_exceeds_maximum(events, measurements, config, driver_factory,
                                                    alert_type):
    """Check that relevant alert is sent when sensor pass the maximum threshold

    The test iterate over the three sensors and for each one run the test.

    Flow:
        * Run lung simulation and check that there aren't any alerts
        * Open configuration screen
        * Increase the relevant sensor minimum threshold to be equal to maximum
        * Run lung simulation and check that there is an alert for passing high threshold
    """
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

    app.run_iterations(SAMPLES_AMOUNT)
    assert len(events.alerts_queue) == 0

    configure_alerts_screen = ConfigureAlarmsScreen(app.master_frame.element,
                                                    measurements=measurements,
                                                    drivers=driver_factory)
    configure_alerts_screen.show()
    getattr(configure_alerts_screen, f"{alert_type}_section").max_button.publish()
    app.gui_update()

    sensor = alert_type
    if alert_type == "oxygen":
        sensor = 'o2'

    max_val = config[f"{sensor}_range"].max
    min_val = config[f"{sensor}_range"].min
    step_size = config.pressure_range.step
    steps = int((max_val - min_val) / step_size)
    for _ in range(steps):
        configure_alerts_screen.on_down_button_click()

    configure_alerts_screen.confirm()
    app.gui_update()

    app.run_iterations(SAMPLES_AMOUNT, render=False)
    app.root.destroy()
    assert len(events.alerts_queue) > 0

    all_alerts = list(events.alerts_queue.queue.queue)
    expected_alert = alerts.AlertCodes[f"{alert_type}_high".upper()]
    assert all(alert == expected_alert for alert in all_alerts)


@pytest.mark.parametrize("alert_type", ['pressure', 'volume', 'oxygen'])
def test_sampler_alerts_when_sensor_exceeds_minimum(events, measurements, config, driver_factory,
                                                    alert_type):
    """Check that relevant alert is sent when sensor pass the minimum threshold

    The test iterate over the three sensors and for each one run the test.

    Flow:
        * Run lung simulation and check that there aren't any alerts
        * Open configuration screen
        * Increase the relevant sensor maximum threshold to be equal to minimum
        * Run lung simulation and check that there is an alert for passing low threshold
    """
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

    app.run_iterations(SAMPLES_AMOUNT)
    assert len(events.alerts_queue) == 0

    configure_alerts_screen = ConfigureAlarmsScreen(app.master_frame.element,
                                                    measurements=measurements,
                                                    drivers=driver_factory)
    configure_alerts_screen.show()
    getattr(configure_alerts_screen, f"{alert_type}_section").min_button.publish()
    app.gui_update()

    sensor = alert_type
    if alert_type == "oxygen":
        sensor = 'o2'

    max_val = config[f"{sensor}_range"].max
    min_val = config[f"{sensor}_range"].min
    step_size = config.pressure_range.step
    steps = int((max_val - min_val) / step_size)
    for _ in range(steps):
        configure_alerts_screen.on_up_button_click()

    configure_alerts_screen.confirm()
    app.gui_update()

    app.run_iterations(SAMPLES_AMOUNT, render=False)
    app.root.destroy()
    assert len(events.alerts_queue) > 0

    all_alerts = list(events.alerts_queue.queue.queue)
    expected_alert = alerts.AlertCodes[f"{alert_type}_low".upper()]
    assert all(alert == expected_alert for alert in all_alerts)


