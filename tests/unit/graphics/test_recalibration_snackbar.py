from unittest.mock import MagicMock

import pytest
from tkinter import Frame
from freezegun import freeze_time

from graphics.themes import Theme, DarkTheme
from data.configurations import Configurations
from data.observable import Observable
from drivers.driver_factory import DriverFactory
from graphics.calibrate.recalibration_snackbar import RecalibrationSnackbar


@pytest.fixture()
def snackbar():
    Theme.ACTIVE_THEME = DarkTheme
    driver_factory = DriverFactory(simulation_mode=True)
    instance = RecalibrationSnackbar(root=Frame(),
                                     drivers=driver_factory,
                                     observer=Observable())

    instance.config = MagicMock(spec=Configurations)
    return instance


def test_no_prompt_until_timeout_reached(snackbar):
    snackbar.config.dp_calibration_timeout_hrs = 5
    snackbar.show = MagicMock()
    with freeze_time("12th Feb 2000 00:00:00"):
        snackbar.update()

    with freeze_time("12th Feb 2000 04:59:59"):
        snackbar.update()

    assert not snackbar.shown
    snackbar.show.assert_not_called()


def test_prompt_appears_on_timeout(snackbar):
    snackbar.config.dp_calibration_timeout_hrs = 5
    snackbar.show = MagicMock(side_effect=snackbar.show)

    with freeze_time("12th Feb 2000 00:00:00"):
        snackbar.update()

    with freeze_time("12th Feb 2000 05:00:00"):
        snackbar.update()

    snackbar.show.assert_called()
    assert snackbar.shown


def test_prompt_stays(snackbar):
    snackbar.config.dp_calibration_timeout_hrs = 5
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
    snackbar.config.dp_calibration_timeout_hrs = 5
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
    snackbar.config.dp_calibration_timeout_hrs = 5
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
    snackbar.config.dp_calibration_timeout_hrs = 5
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
