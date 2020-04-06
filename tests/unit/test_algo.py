import time
from unittest.mock import MagicMock

import freezegun
from pytest import approx


from algo import RunningSlope, VentilationStateMachine, VentilationState, \
    Sampler
from data.alert import AlertCodes
from data.configurations import Configurations
from data.events import Events
from data.measurements import Measurements
from drivers.driver_factory import DriverFactory
from drivers.mocks.sinus import add_noise

from tests.utils import SamplesCSVParser


def test_slope_finder_sanity():
    sf = RunningSlope()
    slope = None
    for i in range(10):
        slope = sf.add_sample(i, i)
    assert slope == 1


def test_slope_finder_straight_line():
    sf = RunningSlope()
    slope = None
    samples = [1] * 10
    for i, s in enumerate(samples):
        slope = sf.add_sample(s, i)
    assert slope == 0


def test_slope_straight_line_with_noise():
    sf = RunningSlope()
    sigma = 0.2
    signal = [1] * 100
    signal = add_noise(signal, sigma)
    for i, s in enumerate(signal):
        slope = sf.add_sample(s, i)
        if slope is not None:
            assert (sigma / 2) >= slope >= -(sigma / 2)


@freezegun.freeze_time("2000-02-12")
def test_correct_state_transitions():
    parser = SamplesCSVParser()
    vsm = VentilationStateMachine(Measurements(), Events())
    for t, p, f, o in parser.samples(start=0, end=200):
        vsm.update(
            pressure_cmh2o=p,
            flow_slm=f,
            o2_percentage=o,
            timestamp=t)

    inhale_entry = vsm.entry_points_ts[VentilationState.Inhale][0]
    exhale_entry = vsm.entry_points_ts[VentilationState.Exhale][0]

    assert inhale_entry == approx(time.time() + 0.721782319877363, rel=0.1)
    assert exhale_entry == approx(time.time() + 4.64647368421053, rel=0.1)


def test_alert_is_published_on_high_o2():
    measurements = Measurements()
    events = Events()
    drivers = DriverFactory(simulation_mode=True, simulation_data='sinus')

    flow = drivers.acquire_driver('flow')
    pressure = drivers.acquire_driver('pressure')
    a2d = drivers.acquire_driver('a2d')
    timer = drivers.acquire_driver('timer')

    a2d.read_oxygen = MagicMock(return_value=600)

    Configurations.instance().o2_range.max = 99

    sampler = Sampler(measurements=measurements, events=events,
                      flow_sensor=flow, pressure_sensor=pressure, a2d=a2d,
                      timer=timer)

    assert len(events.alerts_queue) == 0

    sampler.sampling_iteration()

    assert any(alert == AlertCodes.OXYGEN_HIGH for alert in events.alerts_queue.queue.queue)

    measurements = Measurements()
    events = Events()
    drivers = DriverFactory(simulation_mode=True, simulation_data='sinus')

    flow = drivers.acquire_driver('flow')
    pressure = drivers.acquire_driver('pressure')
    a2d = drivers.acquire_driver('a2d')
    timer = drivers.acquire_driver('timer')

    a2d.read_oxygen = MagicMock(return_value=600)

    Configurations.instance().o2_range.max = 99

    sampler = Sampler(measurements=measurements, events=events,
                      flow_sensor=flow, pressure_sensor=pressure, a2d=a2d,
                      timer=timer)

    assert len(events.alerts_queue) == 0

    sampler.sampling_iteration()

    assert any(alert == AlertCodes.OXYGEN_HIGH for alert in
               events.alerts_queue.queue.queue)


def test_alert_is_published_on_low_o2():
    measurements = Measurements()
    events = Events()
    drivers = DriverFactory(simulation_mode=True, simulation_data='sinus')

    flow = drivers.acquire_driver('flow')
    pressure = drivers.acquire_driver('pressure')
    a2d = drivers.acquire_driver('a2d')
    timer = drivers.acquire_driver('timer')

    a2d.read_oxygen = MagicMock(return_value=0)

    Configurations.instance().o2_range.min = 20

    sampler = Sampler(measurements=measurements, events=events,
                      flow_sensor=flow, pressure_sensor=pressure, a2d=a2d,
                      timer=timer)

    assert len(events.alerts_queue) == 0

    sampler.sampling_iteration()

    assert any(alert == AlertCodes.OXYGEN_LOW for alert in
               events.alerts_queue.queue.queue)
