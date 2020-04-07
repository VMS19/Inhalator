import pytest

from data.measurements import Measurements
from data.events import Events
from data.configurations import Configurations
from data.thresholds import (O2Range, PressureRange,
                             RespiratoryRateRange, VolumeRange)
from tests.unit.conftest import create_sampler


@pytest.fixture
def config():
    c = Configurations.instance()
    c.o2_range = O2Range(min=0, max=100)
    c.pressure_range = PressureRange(min=0, max=30)
    c.resp_rate_range = RespiratoryRateRange(min=0, max=30)
    c.volume_range = VolumeRange(min=0, max=30)
    c.graph_seconds = 12
    c.breathing_threshold = 3.5
    c.log_enabled = False
    return c


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def events():
    return Events()


def test_sampler_inserts_pressure_measurement_to_store(events, measurements):
    sampler = create_sampler("sinus", events, measurements)
    assert measurements.pressure_measurements.qsize() == 0
    sampler.sampling_iteration()
    assert measurements.pressure_measurements.qsize() == 1
    sampler.sampling_iteration()
    assert measurements.pressure_measurements.qsize() == 2


def test_sampler_alerts_when_pressure_exceeds_maximum(events, measurements, config):
    sampler = create_sampler("sinus", events, measurements)
    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.pressure_range = PressureRange(0, 0)
    sampler.sampling_iteration()

    assert len(events.alerts_queue) == 1


def test_sampler_alerts_when_pressure_exceeds_minimum(events, measurements, config):
    sampler = create_sampler("sinus", events, measurements)
    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.pressure_range = PressureRange(0, -100)
    sampler.sampling_iteration()

    assert len(events.alerts_queue) == 1
