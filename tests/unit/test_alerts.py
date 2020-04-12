from itertools import product

import pytest

from algo import Sampler
from data import alerts
from data.alerts import Alert
from data.events import Events
from data.measurements import Measurements
from drivers.driver_factory import DriverFactory
from drivers.null_driver import NullDriver

ALERTS = Alert.ALERT_CODE_TO_MESSAGE.keys()


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def events():
    return Events()


@pytest.mark.parametrize("alert1, alert2", product(ALERTS, ALERTS))
def test_alert_contains(alert1, alert2):
    """Check that Alert contains function works correctly.

    For any two types of alert, create Alert object from the first and
    then check if the object contains the second alert (only when the two
    alerts are the same it should return True).
    """
    expected_results = alert1 == alert2
    assert Alert(alert1).contains(alert2) == expected_results


def test_invalid_flow_driver_initialization(events, measurements):
    driver_factory = DriverFactory(simulation_mode=True)
    flow_sensor = NullDriver()
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer)

    sampler.sampling_iteration()

    all_alerts = list(events.alerts_queue.queue.queue)
    assert alerts.AlertCodes.FLOW_SENSOR_ERROR in all_alerts


def test_invalid_pressure_driver_initialization(events, measurements):
    driver_factory = DriverFactory(simulation_mode=True)
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = NullDriver()
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer)

    sampler.sampling_iteration()

    all_alerts = list(events.alerts_queue.queue.queue)
    assert alerts.AlertCodes.PRESSURE_SENSOR_ERROR in all_alerts


@pytest.mark.xfail(reason="Alert queue is too small to contain alert")
def test_invalid_a2d_driver_initialization(events, measurements):
    driver_factory = DriverFactory(simulation_mode=True)
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = NullDriver
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer)

    sampler.sampling_iteration()

    all_alerts = list(events.alerts_queue.queue.queue)
    assert alerts.AlertCodes.OXYGEN_SENSOR_ERROR in all_alerts
    assert alerts.AlertCodes.NO_BATTERY in all_alerts


def test_battery_does_not_exist(events, measurements):
    driver_factory = DriverFactory(simulation_mode=True)
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    a2d.battery_existence = False
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer)

    sampler.sampling_iteration()

    all_alerts = list(events.alerts_queue.queue.queue)
    assert alerts.AlertCodes.NO_BATTERY in all_alerts
