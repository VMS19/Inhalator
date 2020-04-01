import time
from tkinter import Frame

import freezegun
import pytest
from unittest.mock import MagicMock

from data.alerts import Alert, AlertCodes
from graphics.alert_bar import IndicatorAlertBar
from graphics.themes import Theme, DarkTheme


@pytest.fixture
def alert_bar() -> IndicatorAlertBar:
    Theme.ACTIVE_THEME = DarkTheme()
    parent = MagicMock()
    parent.element = Frame()
    events = MagicMock()
    drivers = MagicMock()
    return IndicatorAlertBar(parent=parent, events=events, drivers=drivers)


def test_starts_with_ok(alert_bar: IndicatorAlertBar):
    assert alert_bar.message_label["text"] == "OK"


def test_on_alert(alert_bar: IndicatorAlertBar):
    alert_bar.set_alert(Alert(AlertCodes.VOLUME_LOW))
    assert alert_bar.message_label["text"] == "Low Volume"

def test_sound_on_alert(alert_bar: IndicatorAlertBar):
    alert_bar.events.mute_alerts = False
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


def test_mute_does_not_disappear_immidiately(alert_bar: IndicatorAlertBar):
    alert_bar.events.mute_alerts = True
    with freezegun.freeze_time("12 February 2000 00:00:00"):
        alert_bar.events.mute_time = time.time()

    with freezegun.freeze_time("12 February 2000 00:00:00"):
        alert_bar.update()

    assert alert_bar.events.mute_alerts == True
