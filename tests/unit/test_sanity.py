from itertools import product

import pytest

from algo import Sampler
from data import alerts
from data.measurements import Measurements
from data.events import Events
from data.configurations import Configurations
from data.thresholds import (FlowThreshold, PressureThreshold,
                             RespiratoryRateThreshold, VolumeThreshold)
from drivers.mocks.sensor import MockSensor
from drivers.driver_factory import DriverFactory


HIGH_VALUE = 50000
LOW_VALUE = -50000
PRESSURE_VALID = 17.5
FLOW_VALID = 17.5
VOLUME_VALID = 17.5
ERROR_DICT = {
        alerts.AlertCodes.PRESSURE_LOW: "Low Pressure",
        alerts.AlertCodes.PRESSURE_HIGH: "High Pressure",
        alerts.AlertCodes.VOLUME_LOW: "Low Volume",
        alerts.AlertCodes.VOLUME_HIGH: "High Volume",
        alerts.AlertCodes.NO_BREATH: "No Breathing",
        alerts.AlertCodes.NO_CONFIGURATION_FILE: "Cannot Read Configuration"
    }


@pytest.fixture
def driver_factory():
    return DriverFactory(simulation_mode=True, simulation_data="sinus")


@pytest.fixture
def config():
    c = Configurations.instance()
    c.flow_threshold = FlowThreshold(min=0, max=30)
    c.pressure_threshold = PressureThreshold(min=0, max=30)
    c.resp_rate_threshold = RespiratoryRateThreshold(min=0, max=30)
    c.volume_threshold = VolumeThreshold(min=0, max=30)
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

    config.pressure_threshold = PressureThreshold(0, 0)
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

    config.pressure_threshold = PressureThreshold(0, -100)
    sampler.sampling_iteration()

    assert len(events.alerts_queue) == 1


def test_sampler_alerts_when_flow_exceeds_maximum(events, measurements, config, driver_factory):
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor, oxygen_a2d)
    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.pressure_threshold = FlowThreshold(0, 0)
    sampler.sampling_iteration()

    assert len(events.alerts_queue) == 1


def test_sampler_alerts_when_flow_exceeds_minimum(events, measurements, config, driver_factory):
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor, oxygen_a2d)
    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    config.pressure_threshold = FlowThreshold(0, -100)
    sampler.sampling_iteration()

    assert len(events.alerts_queue) == 1


def state_to_message(value, name):
    if value == LOW_VALUE:
        return f"High {name}"

    elif value == HIGH_VALUE:
        return f"Low {name}"

    return ""


def run_scenarios(events, sampler, config):
    pressure_values = [LOW_VALUE, PRESSURE_VALID, HIGH_VALUE]
    flow_values = [LOW_VALUE, FLOW_VALID, HIGH_VALUE]
    volume_values = [LOW_VALUE, VOLUME_VALID, HIGH_VALUE]

    for pressure, flow, volume in product(pressure_values, flow_values,
                                          volume_values):
        config.pressure_threshold = PressureThreshold(pressure, pressure)
        config.flow_threshold = FlowThreshold(flow, flow)
        config.volume_threshold = VolumeThreshold(volume, volume)

        sampler.sampling_iteration()

        sensor_values = [pressure, volume]  # TODo: add flow, when there is an alert for it

        over_th = sum([1 for state in sensor_values if state == LOW_VALUE])
        below_th = sum([True for state in sensor_values if state == HIGH_VALUE])

        expect = f"Expected {state_to_message(pressure, 'Pressure')} " \
                 f"{state_to_message(volume, 'Volume')} "
                 # f"{state_to_message(flow, 'flow')}"  # TODO: return when flow alerts

        alarms = list(events.alerts_queue.queue.queue)
        received = "Received " + ' '.join([ERROR_DICT[alarm] for alarm in alarms])

        error_msg = f"{expect}, {received}"
        assert len(alarms) == below_th + over_th,  error_msg
        events.alerts_queue.clear_alerts()


def test_sampler_alerts_when_sensors_exceeds_threshold(events, measurements, config, driver_factory):
    flow_sensor = driver_factory.get_driver("flow")
    pressure_sensor = driver_factory.get_driver("pressure")
    oxygen_a2d = driver_factory.get_driver("oxygen_a2d")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      oxygen_a2d)
    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    run_scenarios(events, sampler, config)
