import pytest

from algo import Sampler
from data.events import DataStore
from data.thresholds import (FlowThreshold, PressureThreshold,
                             RespiratoryRateThreshold, VolumeThreshold)
from drivers.mocks.sensor import MockSensor
from drivers.driver_factory import DriverFactory


@pytest.fixture
def store():
    store = DataStore(flow_threshold=FlowThreshold(min=0, max=30),
                      pressure_threshold=PressureThreshold(min=0, max=30),
                      resp_rate_threshold=RespiratoryRateThreshold(min=0, max=30),
                      volume_threshold=VolumeThreshold(min=0, max=30),
                      graph_seconds=12,
                      breathing_threshold=3.5,
                      log_enabled=False)

    return store


def test_sampler_inserts_pressure_measurement_to_store(store):
    flow_sensor = MockSensor(DriverFactory.generate_mock_air_flow_data())
    pressure_sensor = MockSensor(DriverFactory.generate_mock_pressure_data())
    sampler = Sampler(store, flow_sensor, pressure_sensor)
    assert store.pressure_measurements.qsize() == 0
    sampler.sampling_iteration()
    assert store.pressure_measurements.qsize() == 1
    sampler.sampling_iteration()
    assert store.pressure_measurements.qsize() == 2


def test_sampler_alerts_when_pressure_exceeds_maximum(store):
    flow_sensor = MockSensor(DriverFactory.generate_mock_air_flow_data())
    pressure_sensor = MockSensor(DriverFactory.generate_mock_pressure_data())
    sampler = Sampler(store, flow_sensor, pressure_sensor)
    assert len(store.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(store.alerts_queue) == 0

    store.pressure_threshold = PressureThreshold(0, 0)
    sampler.sampling_iteration()

    assert len(store.alerts_queue) == 1


def test_sampler_alerts_when_pressure_exceeds_minimum(store):
    flow_sensor = MockSensor(DriverFactory.generate_mock_air_flow_data())
    pressure_sensor = MockSensor(DriverFactory.generate_mock_pressure_data())
    sampler = Sampler(store, flow_sensor, pressure_sensor)
    assert len(store.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(store.alerts_queue) == 0

    store.pressure_threshold = PressureThreshold(0, -100)
    sampler.sampling_iteration()

    assert len(store.alerts_queue) == 1


def test_sampler_alerts_when_flow_exceeds_maximum(store):
    flow_sensor = MockSensor(DriverFactory.generate_mock_air_flow_data())
    pressure_sensor = MockSensor(DriverFactory.generate_mock_pressure_data())
    sampler = Sampler(store, flow_sensor, pressure_sensor)
    assert len(store.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(store.alerts_queue) == 0

    store.pressure_threshold = FlowThreshold(0, 0)
    sampler.sampling_iteration()

    assert len(store.alerts_queue) == 1


def test_sampler_alerts_when_flow_exceeds_minimum(store):
    flow_sensor = MockSensor(DriverFactory.generate_mock_air_flow_data())
    pressure_sensor = MockSensor(DriverFactory.generate_mock_pressure_data())
    sampler = Sampler(store, flow_sensor, pressure_sensor)
    assert len(store.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(store.alerts_queue) == 0

    store.pressure_threshold = FlowThreshold(0, -100)
    sampler.sampling_iteration()

    assert len(store.alerts_queue) == 1
