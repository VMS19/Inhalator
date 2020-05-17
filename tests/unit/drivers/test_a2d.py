import pytest
from unittest.mock import patch, MagicMock

from drivers.ads7844_a2d import Ads7844A2D


@pytest.mark.parametrize('raw, real', 
    [((15, 18, 200), 21.594641713164346),
     ((15, 18, 192), 21.55871052894943),
     ((15, 18, 184), 21.522779344734516)])
def test_read_oxygen(raw, real, a2d_driver):
    """Test a2d driver oxygen read values"""
    a2d_driver.set_oxygen_calibration(0.0, 58.86965221771791)
    a2d_driver._spi.xfer.return_value = raw

    assert a2d_driver.read_oxygen() == real
   

def test_battery_exists_true(a2d_driver):
    """Test battery existence function when exists"""
    a2d_driver._spi.xfer.return_value = (15, 85, 56)
    assert a2d_driver.read_battery_existence()


def test_battery_existence_false(a2d_driver):
    """Test battery existence function when doesn't exist"""
    a2d_driver._spi.xfer.return_value = (0, 0, 0)
    assert not a2d_driver.read_battery_existence()


@pytest.mark.parametrize('raw, real',
    [((87, 11, 40), 100),
     ((15, 10, 136), 100),
     ((45, 10, 13), 96),
     ((7, 6, 2), 57)])
def test_battery_percentage(raw, real, a2d_driver):
    """Test battery percentage values"""
    a2d_driver._spi.xfer.return_value = raw
    assert real == a2d_driver.read_battery_percentage()
