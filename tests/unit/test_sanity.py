import pytest

from data.thresholds import O2Range, PressureRange, VolumeRange
from drivers.driver_factory import DriverFactory


@pytest.fixture
def driver_factory():
    return DriverFactory(simulation_mode=True, simulation_data="sinus")


@pytest.fixture
def config(default_config):
    c = default_config
    c.thresholds.o2 = O2Range(min=0, max=100)
    c.thresholds.pressure = PressureRange(min=0, max=30)
    c.thresholds.volume = VolumeRange(min=0, max=30)
    return c


@pytest.mark.usefixtures("config")
def test_sampler_inserts_pressure_measurement_to_store(sim_sampler, events, measurements):
    assert measurements.pressure_measurements.qsize() == 0
    sim_sampler.sampling_iteration()
    assert measurements.pressure_measurements.qsize() == 1
    sim_sampler.sampling_iteration()
    assert measurements.pressure_measurements.qsize() == 2


def test_sampler_alerts_when_pressure_exceeds_maximum(sim_sampler, events, config):
    assert len(events.alerts_queue) == 0
    sim_sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.thresholds.pressure = PressureRange(0, 0)
    sim_sampler.sampling_iteration()

    assert len(events.alerts_queue) == 1


def test_sampler_alerts_when_pressure_exceeds_minimum(sim_sampler, events, config):
    assert len(events.alerts_queue) == 0
    sim_sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.thresholds.pressure = PressureRange(0, -100)
    sim_sampler.sampling_iteration()

    assert len(events.alerts_queue) == 1
