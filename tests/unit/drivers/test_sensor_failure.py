from unittest.mock import MagicMock
import pytest


from algo import Sampler
from data.alerts import AlertCodes
from data.events import Events
from data.measurements import Measurements
from drivers.driver_factory import DriverFactory
from errors import UnavailableMeasurmentError


df = DriverFactory(simulation_mode=True, simulation_data='sinus')
flow = df.acquire_driver('flow')
pressure = df.acquire_driver('pressure')
a2d = df.acquire_driver('a2d')
timer = df.acquire_driver('timer')

flow.read = MagicMock(return_value=0)
pressure.read = MagicMock(return_value=0)
a2d.read_oxygen = MagicMock(return_value=0)
a2d.read_battery_percentage = MagicMock(return_value=0)
a2d.read_battery_existence = MagicMock(return_value=0)


@pytest.fixture
def events():
    return Events()


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def drivers():
    yield "setup"

    flow.read = MagicMock(return_value=0)
    pressure.read = MagicMock(return_value=0)
    a2d.read_oxygen = MagicMock(return_value=0)
    a2d.read_battery_percentage = MagicMock(return_value=0)
    a2d.read_battery_existence = MagicMock(return_value=0)


@pytest.mark.parametrize('read_method',
                         [flow.read,
                          pressure.read,
                          a2d.read_oxygen,
                          a2d.read_battery_percentage,
                          a2d.read_battery_existence])
def test_unavailable_measurement_not_crashing(events, measurements,
                                              drivers, read_method):
    print(f"running {drivers}")
    crash_msg = "Application did not handle correctly " \
                "temporary unavailable sensor measurement, and crashed"
    measurement = 0

    read_method.configure_mock(return_value=measurement,
                            side_effect=UnavailableMeasurmentError(crash_msg))

    sampler = Sampler(measurements=measurements, events=events,
                      flow_sensor=flow, pressure_sensor=pressure, a2d=a2d,
                      timer=timer, average_window=1)

    sampler.sampling_iteration()
    # If exception is not raised, test passed


@pytest.mark.skip(reason="fuck")
@pytest.mark.parametrize('read_method,expected_alert',
                         [(flow.read, AlertCodes.FLOW_SENSOR_ERROR),
                          (pressure.read, AlertCodes.PRESSURE_SENSOR_ERROR),
                          (a2d.read_oxygen, AlertCodes.OXYGEN_SENSOR_ERROR),
                          (a2d.read_battery_percentage, AlertCodes.NO_BATTERY),
                          (a2d.read_battery_existence, AlertCodes.NO_BATTERY)])
def test_sampling_error_raises_alert(events, measurements, read_method,
                                         expected_alert):
    crash_msg = "Application did not handle correctly " \
                "sensor read failure, and crashed"
    measurement = 0

    read_method = MagicMock(return_value=measurement,
                            side_effect=Exception(crash_msg))

    sampler = Sampler(measurements=measurements, events=events,
                      flow_sensor=flow, pressure_sensor=pressure, a2d=a2d,
                      timer=timer, average_window=1)

    assert len(events.alerts_queue) == 0

    sampler.sampling_iteration()

    assert any(alert == expected_alert for alert in
               events.alerts_queue.queue.queue), \
        "Sensor error did not raise correct alert"
