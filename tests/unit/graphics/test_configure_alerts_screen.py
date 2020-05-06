from tkinter import Frame

import pytest

from data.observable import Observable
from graphics.configure_alerts_screen import ConfigureAlarmsScreen
from graphics.themes import Theme, DarkTheme


@pytest.fixture
def data():
    return "sinus"  # Applies for all test in this file.


@pytest.fixture
def screen(configuration_manager, driver_factory) -> ConfigureAlarmsScreen:
    Theme.ACTIVE_THEME = DarkTheme()
    return ConfigureAlarmsScreen(
        root=Frame(),
        drivers=driver_factory,
        observer=Observable())


def test_changing_threshold_using_max_button(screen: ConfigureAlarmsScreen):
    screen.pressure_section.max_button.invoke()
    assert screen.pressure_section.max_button.selected


def test_changing_threshold_using_min_button(screen: ConfigureAlarmsScreen):
    screen.pressure_section.min_button.invoke()
    assert screen.pressure_section.min_button.selected


@pytest.mark.parametrize("threshold", ["min", "max"])
def test_up_down_buttons(threshold, screen: ConfigureAlarmsScreen, config):
    """
    Test that pressing the up/down buttons updates the text on the corresponding
    button to reflect the changes
    """
    pressure = getattr(config.thresholds.pressure, threshold)
    step = config.thresholds.pressure.step
    button = getattr(screen.pressure_section, f"{threshold}_button")
    button.invoke()
    screen.up_or_down_section.up_button.invoke()
    assert f"{pressure + step}" in button["text"]
    screen.up_or_down_section.down_button.invoke()
    assert f"{pressure}" in button["text"]


def test_min_changes_only_when_confirmed(screen: ConfigureAlarmsScreen, config):
    min_pressure = config.thresholds.pressure.min
    step = config.thresholds.pressure.step

    screen.pressure_section.min_button.invoke()
    screen.on_up_button_click()
    assert config.thresholds.pressure.min == min_pressure
    screen.confirm()
    assert config.thresholds.pressure.min == min_pressure + step


def test_pressing_cancel_undoes_everything(screen: ConfigureAlarmsScreen, config):
    max_pressure = config.thresholds.pressure.max

    screen.pressure_section.max_button.invoke()
    screen.on_up_button_click()
    screen.on_up_button_click()
    screen.on_up_button_click()
    screen.cancel()
    assert config.thresholds.pressure.max == max_pressure


def test_pressing_the_same_range_makes_nothing_selected(screen: ConfigureAlarmsScreen):
    screen.pressure_section.max_button.invoke()
    screen.pressure_section.max_button.invoke()
    assert not screen.pressure_section.max_button.selected


def test_minimum_cant_go_over_maximum(screen: ConfigureAlarmsScreen, config):
    config.thresholds.pressure.min = 0
    config.thresholds.pressure.max = 0
    screen.pressure_section.min_button.invoke()  # Click the min button
    screen.on_up_button_click()  # Raise it
    screen.confirm()
    assert config.thresholds.pressure.min == 0


def test_maximum_cant_go_under_minimum(screen: ConfigureAlarmsScreen, config):
    config.thresholds.pressure.min = 0
    config.thresholds.pressure.max = 0
    screen.pressure_section.max_button.invoke()  # Click the min button
    screen.on_down_button_click()  # Lower it
    screen.confirm()
    assert config.thresholds.pressure.max == 0
