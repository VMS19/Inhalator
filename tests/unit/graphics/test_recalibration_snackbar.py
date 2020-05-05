import time
from unittest.mock import MagicMock

import pytest
from tkinter import Frame
from freezegun import freeze_time

from graphics.themes import Theme, DarkTheme
from data.observable import Observable
from drivers.driver_factory import DriverFactory
from graphics.snackbar.recalibration_snackbar import RecalibrationSnackbar


def time_mock():
    """Return original time result, as freezegun mocks it specifically."""
    import time
    return time.time()


@pytest.fixture()
def snackbar(config):
    config.calibration.flow_recalibration_reminder = True
    config.calibration.dp_calibration_timeout_hrs = 5
    Theme.ACTIVE_THEME = DarkTheme
    driver_factory = DriverFactory(simulation_mode=True)
    instance = RecalibrationSnackbar(root=Frame(),
                                     drivers=driver_factory,
                                     observer=Observable())

    instance.timer.get_current_time = time_mock

    return instance


def test_no_prompt_until_timeout_reached(snackbar):
    snackbar.show = MagicMock()
    with freeze_time("12th Feb 2000 00:00:00"):
        snackbar.update()

    with freeze_time("12th Feb 2000 04:59:59"):
        snackbar.update()

    assert not snackbar.shown
    snackbar.show.assert_not_called()


def test_prompt_appears_on_timeout(snackbar):
    snackbar.show = MagicMock(side_effect=snackbar.show)

    with freeze_time("12th Feb 2000 00:00:00"):
        snackbar.update()

    with freeze_time("12th Feb 2000 05:00:00"):
        snackbar.update()

    snackbar.show.assert_called()
    assert snackbar.shown


def test_prompt_stays(snackbar):
    snackbar.show = MagicMock(side_effect=snackbar.show)

    with freeze_time("12th Feb 2000 00:00:00"):
        snackbar.update()

    with freeze_time("12th Feb 2000 05:00:00"):
        snackbar.update()

    snackbar.show.assert_called()
    assert snackbar.shown

    with freeze_time("12th Feb 2001 00:00:00"):
        snackbar.update()

    assert snackbar.shown


def test_prompt_reappears_after_being_snoozed(snackbar):
    snackbar.show = MagicMock(side_effect=snackbar.show)

    with freeze_time("12th Feb 2000 00:00:00"):
        snackbar.update()

    with freeze_time("12th Feb 2000 05:00:00"):
        snackbar.update()
        snackbar.on_snooze()

    with freeze_time("12th Feb 2000 09:59:59"):
        snackbar.update()

    snackbar.show.assert_called_once()
    assert not snackbar.shown


def test_prompt_reappears_after_calibration(snackbar):
    snackbar.show = MagicMock(side_effect=snackbar.show)

    with freeze_time("12th Feb 2000 00:00:00"):
        snackbar.update()

    with freeze_time("12th Feb 2000 05:00:00"):
        snackbar.update()
        snackbar.on_calibrate()
        assert not snackbar.shown

    with freeze_time("12th Feb 2000 09:59:59"):
        snackbar.update()

    snackbar.show.assert_called_once()
    assert not snackbar.shown


def test_time_ago_label_updates(snackbar):
    snackbar.show = MagicMock(side_effect=snackbar.show)

    with freeze_time("12th Feb 2000 00:00:00"):
        snackbar.update()

    with freeze_time("12th Feb 2000 05:00:00"):
        snackbar.update()
        assert "5 hours" in snackbar.text_label.cget("text")

    with freeze_time("12th Feb 2000 06:00:00"):
        snackbar.update()
        assert "6 hours" in snackbar.text_label.cget("text")

    with freeze_time("13th Feb 2000 00:00:00"):
        snackbar.update()
        assert "1 day" in snackbar.text_label.cget("text")


def test_recalibration_snackbar_can_be_disabled(snackbar, config):
    config.calibration.flow_recalibration_reminder = False
    snackbar.show = MagicMock(side_effect=snackbar.show)

    with freeze_time("12th Feb 2000 00:00:00"):
        snackbar.update()

    with freeze_time("12th Feb 2000 05:00:00"):
        snackbar.update()

    snackbar.show.assert_not_called()
    assert not snackbar.shown
