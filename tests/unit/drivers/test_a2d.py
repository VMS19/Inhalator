import pytest
from unittest.mock import patch, MagicMock

from drivers.ads7844_a2d import Ads7844A2D

OXYGEN_REAL = [(15, 18, 200), (15, 18, 192), (15, 18, 184)]
OXYGEN_ACTUAL = [21.594641713164346, 21.55871052894943, 21.522779344734516]

BATTERY_REAL = [(87, 11, 40), (15, 10, 136), (45, 10, 13), (7, 6, 2)]
BATTERY_ACTUAL = [100, 100, 96, 57]


def test_read_oxygen(a2d_driver):
    """
    Test a2d driver oxygen read values

    Expect:
        The correct values.
    """
    a2d_driver.set_oxygen_calibration(0.0, 58.86965221771791)
    a2d_driver._spi.xfer.side_effect = OXYGEN_REAL

    for actual_oxygen in OXYGEN_ACTUAL:
        assert a2d_driver.read_oxygen() == actual_oxygen
   

def test_battery_exists_true(a2d_driver):
    """
    Test battery existence function when exists
    
    Expect:
    Return True.
    """
    a2d_driver._spi.xfer.return_value = (15, 85, 56)
    assert a2d_driver.read_battery_existence()


def test_battery_existence_false(a2d_driver):
    """
    Test battery existence function when doesn't exist
    
    Expect:
    Return False.
    """
    a2d_driver._spi.xfer.return_value = (0, 0, 0)
    assert not a2d_driver.read_battery_existence()


def test_battery_percentage(a2d_driver):
    """
    Test battery percentage values

    Expect:
    The correct values.
    """
    a2d_driver._spi.xfer.side_effect = BATTERY_REAL

    for actual_battery in BATTERY_ACTUAL:
        assert actual_battery == a2d_driver.read_battery_percentage()
