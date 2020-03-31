import pytest

from algo import Sampler
from data.measurements import Measurements
from data.events import Events
from data.configurations import Configurations
from data.thresholds import (FlowRange, PressureRange,
                             RespiratoryRateRange, VolumeRange)
from drivers.driver_factory import DriverFactory
from drivers.mocks.sensor import MockSensor


@pytest.fixture
def driver_factory():
    return DriverFactory(simulation_mode=True, simulation_data="sinus")


@pytest.fixture
def config():
    c = Configurations.instance()
    c.flow_range = FlowRange(min=0, max=30)
    c.pressure_range = PressureRange(min=0, max=30)
    c.resp_rate_range = RespiratoryRateRange(min=0, max=30)
    c.volume_range = VolumeRange(min=0, max=30)
    c.graph_seconds = 12
    c.debug_port = 7777
    c.breathing_threshold = 3.5
    c.log_enabled = False
    return c


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def events():
    return Events()


def test_sampler_inserts_pressure_measurement_to_store(events, measurements, config, driver_factory):
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor, oxygen_a2d)
    assert measurements.pressure_measurements.qsize() == 0
    sampler.sampling_iteration()
    assert measurements.pressure_measurements.qsize() == 1
    sampler.sampling_iteration()
    assert measurements.pressure_measurements.qsize() == 2


def test_sampler_alerts_when_pressure_exceeds_maximum(events, measurements, config, driver_factory):
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor, oxygen_a2d)
    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.pressure_range = PressureRange(0, 0)
    sampler.sampling_iteration()

    assert len(events.alerts_queue) == 1


def test_sampler_alerts_when_pressure_exceeds_minimum(events, measurements, config, driver_factory):
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor, oxygen_a2d)
    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.pressure_range = PressureRange(0, -100)
    sampler.sampling_iteration()

    assert len(events.alerts_queue) == 1


@pytest.mark.xfail(reason="Flow thresholds are not currently checked as per requirements")
def test_sampler_alerts_when_flow_exceeds_maximum(events, measurements, config, driver_factory):
    flow_sensor = MockSensor([1])
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor, oxygen_a2d)
    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.flow_range = FlowRange(0, 0)
    sampler.sampling_iteration()

    assert len(events.alerts_queue) == 1


@pytest.mark.xfail(reason="Flow thresholds are not currently checked as per requirements")
def test_sampler_alerts_when_flow_exceeds_minimum(events, measurements, config, driver_factory):
    flow_sensor = MockSensor([-1])
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor, oxygen_a2d)
    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.flow_range = FlowRange(0, 100)
    sampler.sampling_iteration()

    assert len(events.alerts_queue) == 1
