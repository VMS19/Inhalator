import pytest

from data.alerts import AlertCodes
from data.observable import Observable

from graphics.configure_alerts_screen import ConfigureAlarmsScreen
from tests.data.files import path_to_file

SAMPLES_AMOUNT = 604
TEST_FILE = path_to_file("03-04-2020.csv")


@pytest.mark.parametrize("data", [TEST_FILE])
@pytest.mark.parametrize(
    ["sensor", "expected_alert", "threshold"],
    [("pressure", AlertCodes.PRESSURE_HIGH, "max"),
     ("pressure", AlertCodes.PRESSURE_LOW, "min"),
     ("volume", AlertCodes.VOLUME_HIGH, "max"),
     ("volume", AlertCodes.VOLUME_LOW, "min"),
     ("oxygen", AlertCodes.OXYGEN_HIGH, "max"),
     ("oxygen", AlertCodes.OXYGEN_LOW, "min"), ])
def test_sampler_alerts_when_sensor_exceeds_threshold(
        events, app, config, driver_factory, sensor, expected_alert,
        threshold, data):
    """Check that relevant alert is sent when sensor pass the threshold

    The test iterate over the three sensors and for each one run the test.

    Flow:
        * Run lung simulation and check that there aren't any alerts
        * Open configuration screen
        * Increase the relevant sensor minimum threshold to be equal to maximum
        * Run lung simulation and check that there is an alert for passing high threshold
    """
    app.run_iterations(SAMPLES_AMOUNT)
    assert len(events.alerts_queue) == 0

    config_screen = ConfigureAlarmsScreen(
        app.master_frame.element,
        drivers=driver_factory,
        observer=Observable())
    config_screen.show()
    section = getattr(config_screen, f"{sensor}_section")
    button = getattr(section, f"{threshold}_button")
    button.invoke()
    app.gui_update()

    range_name = sensor
    if sensor == "oxygen":
        range_name = 'o2'

    sensor_range = getattr(config.thresholds, range_name)
    steps = int((sensor_range.max - sensor_range.min) / sensor_range.step)

    click = {
        "max": config_screen.on_down_button_click,
        "min": config_screen.on_up_button_click
    }.get(threshold)
    for _ in range(steps):
        click()

    config_screen.confirm()
    app.gui_update()

    app.run_iterations(SAMPLES_AMOUNT, render=False)
    assert len(events.alerts_queue) > 0

    all_alerts = list(events.alerts_queue.active_alerts)
    assert all(alert == expected_alert for alert in all_alerts),\
        f"Unexpected alert {events.alerts_queue.active_alerts}"
