import time
from tkinter import Frame

import freezegun
import pytest
from unittest.mock import MagicMock

from data.alerts import Alert, AlertCodes, AlertsQueue
from drivers.driver_factory import DriverFactory
from graphics.alert_bar import IndicatorAlertBar
from graphics.themes import Theme, DarkTheme


@pytest.fixture
def alert_bar() -> IndicatorAlertBar:
    Theme.ACTIVE_THEME = DarkTheme()
    parent = MagicMock()
    parent.element = Frame()
    events = MagicMock()
    drivers = MagicMock()
    events.mute_alerts = False

    return IndicatorAlertBar(parent=parent, events=events, drivers=drivers)


def test_starts_with_ok(alert_bar: IndicatorAlertBar):
    assert alert_bar.message_label["text"] == "OK"


def test_on_alert(alert_bar: IndicatorAlertBar):
    alert_bar.set_alert(Alert(AlertCodes.VOLUME_LOW))
    assert alert_bar.message_label["text"] == "Low Volume"


def test_sound_on_alert(alert_bar: IndicatorAlertBar):
    alert_bar.set_alert(Alert(AlertCodes.VOLUME_LOW))
    assert alert_bar.sound_device.start.called


def test_no_sound_on_alert_when_muted(alert_bar: IndicatorAlertBar):
    alert_bar.events.mute_alerts = True
    alert_bar.set_alert(Alert(AlertCodes.VOLUME_LOW))
    assert not alert_bar.sound_device.start.called


def test_alert_then_no_alert(alert_bar: IndicatorAlertBar):
    alert_bar.set_alert(Alert(AlertCodes.VOLUME_LOW))
    alert_bar.set_no_alert()
    assert alert_bar.message_label["text"] == "OK"
    assert alert_bar.sound_device.stop.called


def test_mute_disappears_after_some_time(alert_bar: IndicatorAlertBar):
    alert_bar.events.mute_alerts = True
    with freezegun.freeze_time("12 February 2000 00:00:00"):
        alert_bar.events.mute_time = time.time()

    with freezegun.freeze_time("12 February 2001 00:00:00"):
        alert_bar.update()

    assert alert_bar.events.mute_alerts == False


def test_mute_does_not_disappear_immediately(alert_bar: IndicatorAlertBar):
    alert_bar.events.mute_alerts = True
    with freezegun.freeze_time("12 February 2000 00:00:00"):
        alert_bar.events.mute_time = time.time()

    with freezegun.freeze_time("12 February 2000 00:00:00"):
        alert_bar.update()

    assert alert_bar.events.mute_alerts == True


def test_alert_on_screen_is_the_first_one(alert_bar: IndicatorAlertBar):
    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.VOLUME_LOW)
    alert_bar.update()
    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.VOLUME_HIGH)
    alert_bar.update()
    assert alert_bar.message_label["text"] == "Low Volume"


def test_alert_on_screen_changes_after_an_ok(alert_bar: IndicatorAlertBar):
    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.VOLUME_LOW)
    alert_bar.update()
    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.VOLUME_HIGH)
    alert_bar.update()
    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.OK)
    alert_bar.update()
    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.VOLUME_HIGH)
    alert_bar.update()

    assert alert_bar.message_label["text"] == "High Volume"

def test_timestamp_label_is_empty_when_there_is_no_alert(alert_bar: IndicatorAlertBar):
    alert_bar.events.alerts_queue = AlertsQueue()
    alert_bar.update()

    assert alert_bar.timestamp_label["text"] == ""

def test_timestamp_label_is_empty_when_there_is_an_ok_alert(alert_bar: IndicatorAlertBar):
    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.OK)

    alert_bar.update()

    assert alert_bar.timestamp_label["text"] == ""


def test_timestamp_label_is_empty_when_alert_changes_to_ok(alert_bar: IndicatorAlertBar):
    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.NO_BREATH)
    alert_bar.update()
    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.OK)
    alert_bar.update()

    assert alert_bar.timestamp_label["text"] == ""

def test_timestamp_label_on_alert(alert_bar: IndicatorAlertBar):
    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.NO_BREATH,
                                                     alert_bar.drivers.acquire_driver("timer").get_time())
    alert_bar.update()

    assert alert_bar.timestamp_label["text"] == "just now"


def test_timestamp_label_on_alert_changes_with_time(alert_bar: IndicatorAlertBar):
    drivers_factory = MagicMock()
    alert_bar.drivers = drivers_factory

    drivers_factory.acquire_driver("timer").get_time = MagicMock(return_value=0)

    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.NO_BREATH, 0)
    alert_bar.update()
    assert alert_bar.timestamp_label["text"] == "just now"

    drivers_factory.acquire_driver("timer").get_time = MagicMock(return_value=60*60)
    alert_bar.update()
    assert alert_bar.timestamp_label["text"] == "1 hour ago"


def test_timestamp_label_resets_on_new_alert(alert_bar: IndicatorAlertBar):
    drivers_factory = MagicMock()
    alert_bar.drivers = drivers_factory

    drivers_factory.acquire_driver("timer").get_time = MagicMock(return_value=0)

    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.NO_BREATH, 0)
    alert_bar.update()
    assert alert_bar.timestamp_label["text"] == "just now"

    drivers_factory.acquire_driver("timer").get_time = MagicMock(return_value=60*60)
    alert_bar.update()
    assert alert_bar.timestamp_label["text"] == "1 hour ago"

    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.OK)
    alert_bar.update()

    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.VOLUME_HIGH, 60*60)
    alert_bar.update()
    assert alert_bar.timestamp_label["text"] == "just now"


def test_version_label(alert_bar: IndicatorAlertBar):
    from graphics.version import __version__
    assert __version__ in alert_bar.version_label["text"]


def test_alert_on_high_oxygen(alert_bar: IndicatorAlertBar):
    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.OXYGEN_HIGH,
                                                     alert_bar.drivers.acquire_driver("timer").get_time())
    alert_bar.update()

    assert alert_bar.message_label["text"] == "Oxygen Too High"


def test_alert_on_low_oxygen(alert_bar: IndicatorAlertBar):
    alert_bar.events.alerts_queue.last_alert = Alert(AlertCodes.OXYGEN_LOW,
                                                     alert_bar.drivers.acquire_driver("timer").get_time())
    alert_bar.update()

    assert alert_bar.message_label["text"] == "Oxygen Too Low"
