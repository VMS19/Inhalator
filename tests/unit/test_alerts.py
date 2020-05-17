from itertools import product

import pytest

from algo import Sampler
from data import alerts
from data.alerts import Alert, AlertCodes
from drivers.null_driver import NullDriver

ALERTS = Alert.ALERT_CODE_TO_MESSAGE.keys()


@pytest.mark.parametrize("alert1, alert2", product(ALERTS, ALERTS))
def test_alert_contains(alert1, alert2):
    """Check that Alert contains function works correctly.

    For any two types of alert, create Alert object from the first and
    then check if the object contains the second alert (only when the two
    alerts are the same it should return True).
    """
    expected_results = alert1 == alert2
    assert Alert(alert1).contains(alert2) == expected_results


@pytest.fixture
def data():
    return "sinus"


@pytest.fixture
def config(default_config):
    default_config.thresholds.pressure.min = 0  # Fits sinus
    return default_config


@pytest.fixture
def sampler(config, driver_factory, measurements, events, null_driver):
    driver_names = {"flow_sensor", "pressure_sensor", "a2d", "timer"}
    drivers = {name: getattr(driver_factory, name.replace("_sensor", ""))
               for name in driver_names}
    if null_driver in driver_names:
        drivers[null_driver] = NullDriver()
    sampler = Sampler(measurements=measurements, events=events, **drivers)
    return sampler


@pytest.mark.parametrize(
    ["null_driver", "expected_alerts"],
    [("flow_sensor", {AlertCodes.FLOW_SENSOR_ERROR}),
     ("pressure_sensor", {AlertCodes.PRESSURE_SENSOR_ERROR}),
     ("a2d", {AlertCodes.OXYGEN_SENSOR_ERROR, AlertCodes.NO_BATTERY})])
def test_invalid_flow_driver_initialization(events, sampler, null_driver, expected_alerts):
    sampler.sampling_iteration()
    assert expected_alerts.issubset(events.alerts_queue.active_alert_set)


@pytest.mark.parametrize("null_driver", [None])
def test_battery_does_not_exist(events, sampler, null_driver):
    sampler._a2d.battery_existence = False
    sampler.sampling_iteration()
    assert alerts.AlertCodes.NO_BATTERY in events.alerts_queue.active_alerts
