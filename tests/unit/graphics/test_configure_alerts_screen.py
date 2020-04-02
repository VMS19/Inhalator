import time
from tkinter import Frame

import pytest
from unittest.mock import MagicMock

from data.alerts import Alert, AlertCodes
from data.configurations import Configurations
from graphics.configure_alerts_screen import ConfigureAlarmsScreen
from graphics.themes import Theme, DarkTheme


@pytest.fixture
def screen() -> ConfigureAlarmsScreen:
    Theme.ACTIVE_THEME = DarkTheme()
    return ConfigureAlarmsScreen(root=Frame())

def test_changing_threshold_using_max_button(screen: ConfigureAlarmsScreen):
    screen.pressure_section.max_button.publish()
    assert screen.selected_threshold == Configurations.instance().pressure_range

def test_changing_threshold_using_min_button(screen: ConfigureAlarmsScreen):
    screen.pressure_section.min_button.publish()
    assert screen.selected_threshold == Configurations.instance().pressure_range

def test_up_down_buttons_on_min(screen: ConfigureAlarmsScreen):
    min_pressure = Configurations.instance().pressure_range.min
    step = Configurations.instance().pressure_range.step

    screen.pressure_section.min_button.publish()
    screen.on_up_button_click()
    assert Configurations.instance().pressure_range.min == min_pressure + step
    screen.on_down_button_click()
    assert Configurations.instance().pressure_range.min == min_pressure

def test_up_down_buttons_on_max(screen: ConfigureAlarmsScreen):
    max_pressure = Configurations.instance().pressure_range.max
    step = Configurations.instance().pressure_range.step

    screen.pressure_section.max_button.publish()
    screen.on_up_button_click()
    assert Configurations.instance().pressure_range.max == max_pressure + step
    screen.on_down_button_click()
    assert Configurations.instance().pressure_range.max == max_pressure

def test_pressing_cancel_undoes_everything(screen: ConfigureAlarmsScreen):
    max_pressure = Configurations.instance().pressure_range.max

    screen.pressure_section.max_button.publish()
    screen.on_up_button_click()
    screen.on_up_button_click()
    screen.on_up_button_click()
    screen.cancel()

    assert Configurations.instance().pressure_range.max == max_pressure