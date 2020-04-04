import csv
import os

import pytest
from pytest import approx

from data.events import Events
from data.measurements import Measurements
from drivers.mocks.sinus import add_noise
from logic.state_machine import VentilationStateMachine, VentilationState
from logic.utils import RunningSlope


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


@pytest.fixture
def real_data():
    this_dir = os.path.dirname(__file__)
    with open(os.path.join(this_dir, "pressure_data_pig.csv"), "r") as f:
        data = list(csv.reader(f))
    t = [float(d[0]) for d in data]
    v = [float(d[1]) for d in data]
    return t, v


def test_correct_state_transitions(real_data):
    t, v = real_data
    vsm = VentilationStateMachine(Measurements(), Events())
    for timestamp, pressure in zip(t, v):
        vsm.update(
            pressure_cmh2o=pressure,
            flow_slm=0,
            o2_saturation_percentage=0,
            timestamp=timestamp)

    inhale_entry = vsm.entry_points_ts[VentilationState.Inhale][0]
    hold_entry = vsm.entry_points_ts[VentilationState.Hold][0]
    exhale_entry = vsm.entry_points_ts[VentilationState.Exhale][0]
    peep_entry = vsm.entry_points_ts[VentilationState.PEEP][0]

    assert inhale_entry == approx(4.41, rel=0.1)
    assert hold_entry == approx(4.95, rel=0.1)
    assert exhale_entry == approx(6.07, rel=0.1)
    assert peep_entry == approx(6.615, rel=0.1)
