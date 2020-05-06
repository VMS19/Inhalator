import time

import freezegun
import pytest
from pytest import approx


from algo import VentilationStateMachine, VentilationState
from logic.computations import RunningSlope
from data.alerts import AlertCodes
from data.thresholds import O2Range
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
def test_correct_state_transitions(config, measurements, events):
    config.state_machine.min_exp_volume_for_exhale = 0
    config.boot_alert_grace_time = 0
    parser = SamplesCSVParser()
    vsm = VentilationStateMachine(measurements, events)
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


@pytest.mark.parametrize(
    ["o2_range", "o2_read", "alert_code"],
    [(O2Range(min=20, max=99), 100, AlertCodes.OXYGEN_HIGH),
     (O2Range(min=20, max=99), 19, AlertCodes.OXYGEN_LOW),
     (O2Range(min=20, max=99), 21, None)]
)
def test_o2_alerts(measurements, config, events, o2_range, o2_read, alert_code):
    config.thresholds.o2 = o2_range
    vsm = VentilationStateMachine(measurements=measurements, events=events)
    vsm.update(20, 10, o2_read, 0)
    assert len(events.alerts_queue) == 0 if alert_code is None else 1
    if alert_code is not None:
        assert events.alerts_queue.active_alerts[0] == alert_code
