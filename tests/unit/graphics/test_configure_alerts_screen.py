import time
from tkinter import Frame

import pytest
from unittest.mock import MagicMock

from data.alerts import Alert, AlertCodes
from data.configurations import Configurations
from data.measurements import Measurements
from drivers.driver_factory import DriverFactory
from graphics.configure_alerts_screen import ConfigureAlarmsScreen
from graphics.themes import Theme, DarkTheme


@pytest.fixture
def screen() -> ConfigureAlarmsScreen:
    Theme.ACTIVE_THEME = DarkTheme()
    measurements = Measurements()
    drivers = DriverFactory(simulation_mode=True, simulation_data='sinus')

    return ConfigureAlarmsScreen(root=Frame(), drivers=drivers, measurements=measurements)


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
    assert Configurations.instance().pressure_range.temporary_min == min_pressure + step
    screen.on_down_button_click()
    assert Configurations.instance().pressure_range.temporary_min == min_pressure


def test_min_changes_only_when_confirmed(screen: ConfigureAlarmsScreen):
    min_pressure = Configurations.instance().pressure_range.min
    step = Configurations.instance().pressure_range.step

    screen.pressure_section.min_button.publish()
    screen.on_up_button_click()
    assert Configurations.instance().pressure_range.min == min_pressure
    screen.confirm()
    assert Configurations.instance().pressure_range.min == min_pressure + step


def test_up_down_buttons_on_max(screen: ConfigureAlarmsScreen):
    max_pressure = Configurations.instance().pressure_range.max
    step = Configurations.instance().pressure_range.step

    screen.pressure_section.max_button.publish()
    screen.on_up_button_click()
    assert Configurations.instance().pressure_range.temporary_max == max_pressure + step
    screen.on_down_button_click()
    assert Configurations.instance().pressure_range.temporary_max == max_pressure


def test_pressing_cancel_undoes_everything(screen: ConfigureAlarmsScreen):
    max_pressure = Configurations.instance().pressure_range.max

    screen.pressure_section.max_button.publish()
    screen.on_up_button_click()
    screen.on_up_button_click()
    screen.on_up_button_click()
    screen.cancel()

    assert Configurations.instance().pressure_range.max == max_pressure


def test_pressing_the_same_range_makes_nothing_selected(screen: ConfigureAlarmsScreen):
    screen.pressure_section.max_button.publish()
    screen.pressure_section.max_button.publish()
    assert screen.selected_threshold == None

def test_minimum_cant_go_over_maximum(screen: ConfigureAlarmsScreen):
    config = Configurations.instance()
    config.pressure_range.min = 0
    config.pressure_range.max = 0
    screen.pressure_section.min_button.publish()  # Click the min button
    screen.on_up_button_click()  # Raise it

    assert config.pressure_range.temporary_min == 0

    # Revert changes since Configurations is a Singleton and we don't
    # want it to interact with other tests
    screen.cancel()


def test_maxmimum_cant_go_under_minimum(screen: ConfigureAlarmsScreen):
    config = Configurations.instance()
    config.pressure_range.min = 0
    config.pressure_range.max = 0
    screen.pressure_section.max_button.publish()  # Click the min button
    screen.on_down_button_click()  # Lower it

    assert config.pressure_range.temporary_max == 0

    # Revert changes since Configurations is a Singleton and we don't
    # want it to interact with other tests
    screen.cancel()
