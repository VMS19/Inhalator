from statistics import mean

import pytest
from unittest.mock import patch, MagicMock

from errors import I2CReadError
from logic.computations import RunningAvg


HSC_RAW_DATA = [(2, bytearray({32, 128})),
                (2, bytearray({32, 37})),
                (2, bytearray({160, 41})),
                (2, bytearray({48, 36})),]
HSC_REAL_FLOW = [12.63439454918927 , 6.792823216517251,
                 7.150581789380773, 71.78432262039246]
HSC_TO_PRESSURE = [0.11949070057476767, 0.03454028063489348,
                   0.03827436502785491, 3.85730917792922]


@pytest.mark.parametrize('raw, real',
    [((2, bytearray({8, 160})), 3.0572924931339642),
     ((2, bytearray({24, 22})), 24.286702471772962),
     ((2, bytearray({8, 132})), 2.9071097039975586)])
def test_abp_pressure_sensor_read(raw, real, abp_driver):
    """Test ABPMAND001PG2A3 pressure sensor return value"""
    pigpio_mock = abp_driver._pig
    pigpio_mock.i2c_read_device.return_value = raw

    assert abp_driver.read() == real

@pytest.mark.parametrize('raw, real', zip(HSC_RAW_DATA, HSC_REAL_FLOW))
@patch('logic.computations.RunningAvg.process', side_effect=(lambda x: x))
def test_hsc_pressure_sensor_read(mock_avg, raw, real, hsc_driver):
    """Test hsc differential pressure sensor read return values"""
    pigpio_mock = hsc_driver._pig
    pigpio_mock.i2c_read_device.return_value = raw

    assert hsc_driver.read() == real


def test_hsc_pressure_sensor_read_avg(hsc_driver):
    """Test hsc differential pressure sensor read values with RunningAvg"""
    pigpio_mock = hsc_driver._pig

    pigpio_mock.i2c_read_device.side_effect = HSC_RAW_DATA

    for index in range(len(HSC_REAL_FLOW)):
        avg = mean(HSC_REAL_FLOW[0:index + 1])
        assert hsc_driver.read() == avg


@pytest.mark.parametrize('raw, flow, pressure',
    zip(HSC_RAW_DATA, HSC_REAL_FLOW, HSC_TO_PRESSURE))
def test_hsc_flow_to_pressure(raw, flow, pressure, hsc_driver):
    """Test hsc flow to pressure convertion"""
    pigpio_mock = hsc_driver._pig

    pigpio_mock.i2c_read_device.return_value = raw

    assert hsc_driver.flow_to_pressure(flow) == pressure
    assert hsc_driver.pressure_to_flow(hsc_driver.flow_to_pressure(flow)) == pytest.approx(flow)


def test_honeywell_i2c_error(abp_driver):
    """
    test honeywell driver read function when i2c read error accure (using abp driver).

    Expect:
        UnavailableMeasurmentError
    """
    abp = abp_driver
    pigpio_mock = abp_driver._pig

    pigpio_mock.i2c_read_device.return_value = (-83, '')

    with pytest.raises(I2CReadError):
        abp.read()

