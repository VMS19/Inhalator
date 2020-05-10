from statistics import mean

import pytest
from unittest.mock import patch, MagicMock

from errors import UnavailableMeasurmentError
from logic.computations import RunningAvg


ABP_RAW_DATA = [(2, bytearray({8, 160})),
                (2, bytearray({24, 22})),
                (2, bytearray({8, 132}))]
ABP_REAL_FLOW = [3.0572924931339642, 24.286702471772962, 2.9071097039975586]

HSC_RAW_DATA = [(2, bytearray({32, 128})),
                (2, bytearray({32, 37})),
                (2, bytearray({160, 41})),
                (2, bytearray({48, 36})),]
HSC_REAL_FLOW = [12.63439454918927 , 6.792823216517251,
                 7.150581789380773, 71.78432262039246]
HSC_TO_PRESSURE = [0.11949070057476767, 0.03454028063489348,
                   0.03827436502785491, 3.85730917792922]


def test_abp_pressure_sensor_read(abp_driver):
    """
    Test ABPMAND001PG2A3 pressure sensor return values
    
    Expect:
        The correct values
    """
    pigpio_mock = abp_driver._pig

    pigpio_mock.i2c_read_device.side_effect = ABP_RAW_DATA

    for real_data in ABP_REAL_FLOW:
        assert abp_driver.read() == real_data


@patch('logic.computations.RunningAvg.process', side_effect=(lambda x: x))
def test_hsc_pressure_sensor_read(mock_avg, hsc_driver):
    """
    Test hsc differential pressure sensor read return values

    Expect:
        The correct values
    """

    pigpio_mock = hsc_driver._pig

    pigpio_mock.i2c_read_device.side_effect = HSC_RAW_DATA

    for real in HSC_REAL_FLOW:
        assert hsc_driver.read() == real


def test_hsc_pressure_sensor_read_avg(hsc_driver):
    """
    Test hsc differential pressure sensor read values with RunningAvg

    Expect:
        The average values
    """
    pigpio_mock = hsc_driver._pig

    pigpio_mock.i2c_read_device.side_effect = HSC_RAW_DATA

    for index in range(len(HSC_REAL_FLOW)):
        avg = mean(HSC_REAL_FLOW[0:index + 1])
        assert hsc_driver.read() == avg


def test_hsc_flow_to_pressure(hsc_driver):
    """
    Test hsc flow to pressure convertion

    Expect:
        The correct values
    """
    pigpio_mock = hsc_driver._pig

    pigpio_mock.i2c_read_device.side_effect = HSC_RAW_DATA

    for index, flow in enumerate(HSC_REAL_FLOW):
        assert hsc_driver.flow_to_pressure(flow) == HSC_TO_PRESSURE[index]
        assert hsc_driver.pressure_to_flow(hsc_driver.flow_to_pressure(flow)) == flow


def test_honeywell_i2c_error(abp_driver):
    """
    test honeywell driver read function when i2c read error accure (using abp driver).

    Expect:
        UnavailableMeasurmentError
    """
    abp = abp_driver
    pigpio_mock = abp_driver._pig

    pigpio_mock.i2c_read_device.return_value = (-83, '')

    with pytest.raises(UnavailableMeasurmentError):
        abp.read()

