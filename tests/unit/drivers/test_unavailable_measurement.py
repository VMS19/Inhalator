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
    return DriverFactory(simulation_mode=True,
                         simulation_data='sinus')


def test_flow_unavailable_measurement_not_crashing(events, measurements, drivers):
    flow = drivers.acquire_driver('flow')
    pressure = drivers.acquire_driver('pressure')
    a2d = drivers.acquire_driver('a2d')
    timer = drivers.acquire_driver('timer')

    flow.read = MagicMock(return_value=3, side_effect=UnavailableMeasurmentError(""))
    pressure.read = MagicMock(return_value=3,
                          side_effect=UnavailableMeasurmentError(""))
    a2d.read_oxygen = MagicMock(return_value=3,
                          side_effect=UnavailableMeasurmentError(""))
    a2d.read_battery_percentage = MagicMock(return_value=3,
                                side_effect=UnavailableMeasurmentError(""))
    a2d.read_battery_existence = MagicMock(return_value=3,
                                side_effect=UnavailableMeasurmentError(""))


    sampler = Sampler(measurements=measurements, events=events,
                      flow_sensor=flow, pressure_sensor=pressure, a2d=a2d,
                      timer=timer, average_window=1)

    assert len(events.alerts_queue) == 0

    sampler.sampling_iteration()

    #assert any(alert == AlertCodes.OXYGEN_LOW for alert in
    #           events.alerts_queue.queue.queue)
