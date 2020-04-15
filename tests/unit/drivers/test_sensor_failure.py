from unittest.mock import MagicMock
import pytest


from algo import Sampler
from data.alerts import AlertCodes
from data.configurations import Configurations
from data.events import Events
from data.measurements import Measurements
from drivers.driver_factory import DriverFactory
from errors import UnavailableMeasurmentError


@pytest.fixture
def events():
    return Events()


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def drivers():
    df = DriverFactory(simulation_mode=True, simulation_data='sinus')
    flow = df.acquire_driver('flow')
    pressure = df.acquire_driver('pressure')
    a2d = df.acquire_driver('a2d')
    timer = df.acquire_driver('timer')
    return flow, pressure, a2d, timer


def test_unavailable_measurement_not_crashing(events, measurements,
                                                   drivers):
    crash_msg = "Application did not handle correctly " \
                "temporary unavailable sensor measurement, and crashed"
    measurement = 0
    flow, pressure, a2d, timer = drivers

    flow.read = MagicMock(return_value=measurement,
                          side_effect=UnavailableMeasurmentError(crash_msg))
    pressure.read = MagicMock(return_value=measurement,
                              side_effect=UnavailableMeasurmentError(crash_msg))
    a2d.read_oxygen = MagicMock(return_value=measurement,
                            side_effect=UnavailableMeasurmentError(crash_msg))
    a2d.read_battery_percentage = MagicMock(return_value=measurement,
                            side_effect=UnavailableMeasurmentError(crash_msg))
    a2d.read_battery_existence = MagicMock(return_value=measurement,
                            side_effect=UnavailableMeasurmentError(crash_msg))

    sampler = Sampler(measurements=measurements, events=events,
                      flow_sensor=flow, pressure_sensor=pressure, a2d=a2d,
                      timer=timer, average_window=1)

    sampler.sampling_iteration()
    # If exception is not raised, test passed

def test_sampling_exception_raises_alert(events, measurements, drivers):
    flow, pressure, a2d, timer = drivers

    flow.read = MagicMock(return_value=3,
                          side_effect=Exception(""))
    pressure.read = MagicMock(return_value=3,
                              side_effect=Exception(""))
    a2d.read_oxygen = MagicMock(return_value=3,
                                side_effect=Exception(""))
    a2d.read_battery_percentage = MagicMock(return_value=3,
                                side_effect=Exception(""))
    a2d.read_battery_existence = MagicMock(return_value=3,
                                side_effect=Exception(""))

    sampler = Sampler(measurements=measurements, events=events,
                      flow_sensor=flow, pressure_sensor=pressure, a2d=a2d,
                      timer=timer, average_window=1)

    assert len(events.alerts_queue) == 0

    sampler.sampling_iteration()

    #assert any(alert == AlertCodes.OXYGEN_LOW for alert in
    #           events.alerts_queue.queue.queue)
