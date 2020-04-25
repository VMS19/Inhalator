from unittest.mock import MagicMock
import pytest

from algo import Sampler
from data.alerts import AlertCodes
from drivers.driver_factory import DriverFactory
from errors import UnavailableMeasurmentError


@pytest.fixture
def mock_drivers(fault_sensors, error, read_val=0):
    df = DriverFactory(simulation_mode=True, simulation_data='sinus')
    flow = df.acquire_driver('flow')
    pressure = df.acquire_driver('pressure')
    a2d = df.acquire_driver('a2d')
    timer = df.acquire_driver('timer')

    flow.read = MagicMock(return_value=read_val)
    pressure.read = MagicMock(return_value=read_val)
    a2d.read_oxygen = MagicMock(return_value=read_val)
    a2d.read_battery_percentage = MagicMock(return_value=read_val)
    a2d.read_battery_existence = MagicMock(return_value=read_val)

    error_read_methods = []
    if "flow" in fault_sensors:
        error_read_methods.append(flow.read)
    if "pressure" in fault_sensors:
        error_read_methods.append(pressure.read)
    if "oxygen" in fault_sensors:
        error_read_methods.append(a2d.read_oxygen)
    if "battery" in fault_sensors:
        error_read_methods.append(a2d.read_battery_percentage)
        error_read_methods.append(a2d.read_battery_existence)

    for method in error_read_methods:
        method.configure_mock(return_value=read_val,
                              side_effect=error("sensor fault test failed!"))

    return flow, pressure, a2d, timer


@pytest.fixture
def config(default_config):
    c = default_config
    # Suppress unwanted alerts.
    c.thresholds.pressure.min = 0
    c.thresholds.o2.min = 0
    return c


@pytest.mark.parametrize('fault_sensors,error',
                         [(["flow"], UnavailableMeasurmentError),
                          (["pressure"], UnavailableMeasurmentError),
                          (["oxygen"], UnavailableMeasurmentError),
                          (["battery"], UnavailableMeasurmentError)])
def test_unavailable_measurement_not_crashing(config, events, measurements,
                                              mock_drivers):
    """Tests that application handle temporary unavailable sensor read."""
    flow, pressure, a2d, timer = mock_drivers

    sampler = Sampler(config, measurements=measurements, events=events,
                      flow_sensor=flow, pressure_sensor=pressure, a2d=a2d,
                      timer=timer)

    sampler.sampling_iteration()
    # If no crashing occurred - test passed


@pytest.mark.parametrize('fault_sensors,error,expected_alert',
                         [(["flow"], Exception, AlertCodes.FLOW_SENSOR_ERROR),
                          (["pressure"], Exception, AlertCodes.PRESSURE_SENSOR_ERROR),
                          (["oxygen"], Exception, AlertCodes.OXYGEN_SENSOR_ERROR),
                          (["battery"], Exception, AlertCodes.NO_BATTERY)])
def test_sampling_error_raises_alert(config, events, measurements, mock_drivers,
                                     expected_alert):
    """Tests that application handle sensor read error, and notify alert."""
    flow, pressure, a2d, timer = mock_drivers

    sampler = Sampler(config, measurements=measurements, events=events,
                      flow_sensor=flow, pressure_sensor=pressure, a2d=a2d,
                      timer=timer)

    assert len(events.alerts_queue) == 0

    sampler.sampling_iteration()

    assert len(events.alerts_queue) > 0, "Sensor error did not raise any alert"
    assert expected_alert in events.alerts_queue.queue.queue, \
        "Sensor error did not raise the correct alert"
