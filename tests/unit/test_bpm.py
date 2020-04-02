import csv
import os

import pytest
from pytest import approx

from algo import VentilationStateMachine
from data.events import Events
from data.measurements import Measurements


SIMULATION_FOLDER = "simulation"

SAMPLE_TIME_DIFF = 0.045  # seconds
TIME_FROM_BEAT_TO_SIM_END = 3.69  # seconds
TIME_FROM_SIM_START_TO_INHALE = 1.62  # seconds


@pytest.fixture
def real_data():
    this_dir = os.path.dirname(__file__)
    with open(os.path.join(this_dir, SIMULATION_FOLDER,
                           "pig_sim_cycle.csv"), "r") as f:
        data = list(csv.reader(f))
    timestamps = [float(d[0]) for d in data]
    pressure_values = [float(d[1]) for d in data]
    return timestamps, pressure_values


def test_bpm_calculation_const_rate(real_data):
    """Test BPM calculated correctly with constant BPM simulation

    Flow:
        * Run pig simulation for entire breath cycle
        * Check BPM calculated correctly
    """
    timestamps, pressure_values = real_data
    timestamps += [timestamps[-1] + SAMPLE_TIME_DIFF * (i + 1)
                   for i in range(len(timestamps) * 100)]
    vsm = VentilationStateMachine(Measurements(), Events())
    for timestamp, pressure in zip(timestamps, pressure_values * 2):
        vsm.update(
            pressure_cmh2o=pressure,
            flow_slm=0,
            o2_saturation_percentage=0,
            timestamp=timestamp)

    samples_len = len(vsm.breathes_rate_meter.samples) - 1
    time_span_seconds = vsm.breathes_rate_meter.time_span_seconds
    interval = (TIME_FROM_BEAT_TO_SIM_END + TIME_FROM_SIM_START_TO_INHALE)
    expected_bpm = samples_len * (time_span_seconds / interval)
    assert vsm._measurements.bpm == approx(expected_bpm, rel=0.01)


def test_bpm_calculation_const_rate_long_run(real_data):
    """Test BPM calculated correctly with constant BPM simulation

    Flow:
        * Run pig simulation for 100 breath cycles
        * Check BPM calculated correctly
    """
    timestamps, pressure_values = real_data
    timestamps += [timestamps[-1] + SAMPLE_TIME_DIFF * (i + 1)
                   for i in range(len(timestamps) * 100)]
    vsm = VentilationStateMachine(Measurements(), Events())
    for timestamp, pressure in zip(timestamps, pressure_values * 101):
        vsm.update(
            pressure_cmh2o=pressure,
            flow_slm=0,
            o2_saturation_percentage=0,
            timestamp=timestamp)

    samples_len = len(vsm.breathes_rate_meter.samples) - 1
    time_span_seconds = vsm.breathes_rate_meter.time_span_seconds
    cycle_time = (TIME_FROM_BEAT_TO_SIM_END + TIME_FROM_SIM_START_TO_INHALE)
    cycles_in_time_span = int(time_span_seconds / cycle_time)
    interval = min(cycle_time * cycles_in_time_span, cycle_time * samples_len)
    expected_bpm = samples_len * (time_span_seconds / interval)
    assert vsm._measurements.bpm == approx(expected_bpm, rel=0.01)


@pytest.mark.parametrize('rate', [1 + x * 0.1 for x in range(11)])
def test_bpm_calculation_changing_rate(real_data, rate):
    """Test BPM calculated correctly with changing BPM simulation

    Flow:
        * Run pig simulation for entire breath cycle -  simulation start with
          timestamps with diff of 0.045 seconds between each one, then in the
          middle changed to 0.045 * rate per sample
        * Check BPM calculated correctly
    """
    timestamps, pressure_values = real_data
    timestamps += [timestamps[-1] + rate * SAMPLE_TIME_DIFF * (i + 1)
                   for i in range(len(timestamps))]
    vsm = VentilationStateMachine(Measurements(), Events())
    for timestamp, pressure in zip(timestamps, pressure_values * 2):
        vsm.update(
            pressure_cmh2o=pressure,
            flow_slm=0,
            o2_saturation_percentage=0,
            timestamp=timestamp)

    samples_len = len(vsm.breathes_rate_meter.samples) - 1
    time_span_seconds = vsm.breathes_rate_meter.time_span_seconds
    interval = TIME_FROM_BEAT_TO_SIM_END + rate * TIME_FROM_SIM_START_TO_INHALE
    expected_bpm = samples_len * (time_span_seconds / interval)
    assert vsm._measurements.bpm == approx(expected_bpm, rel=0.1)


@pytest.mark.parametrize('rates', [[1, 2], [1.5, 2], [2, 3]])
def test_bpm_calculation_changing_rate_twice(real_data, rates):
    """Test BPM calculated correctly with changing BPM simulation

    Flow:
        * Run pig simulation for two breath cycle - simulation start with
          timestamps with diff of 0.045 seconds between each one, then in the
          middle changed to 0.045 * rate1 per sample and in the next sample
          change to 0.045 * rate 2 per sample
        * Check BPM calculated correctly
    """
    timestamps, pressure_values = real_data
    timestamps += [timestamps[-1] + rates[0] * SAMPLE_TIME_DIFF * (i + 1)
                   for i in range(len(pressure_values))]
    timestamps += [timestamps[-1] + rates[1] * SAMPLE_TIME_DIFF * (i + 1)
                   for i in range(len(pressure_values))]
    vsm = VentilationStateMachine(Measurements(), Events())
    for timestamp, pressure in zip(timestamps, pressure_values * 3):
        vsm.update(
            pressure_cmh2o=pressure,
            flow_slm=0,
            o2_saturation_percentage=0,
            timestamp=timestamp)

    samples_len = len(vsm.breathes_rate_meter.samples) - 1
    time_span_seconds = vsm.breathes_rate_meter.time_span_seconds
    interval = TIME_FROM_BEAT_TO_SIM_END
    interval += rates[0] * (TIME_FROM_SIM_START_TO_INHALE + TIME_FROM_BEAT_TO_SIM_END)
    interval += rates[1] * TIME_FROM_SIM_START_TO_INHALE
    expected_bpm = samples_len * (time_span_seconds / interval)
    assert vsm._measurements.bpm == approx(expected_bpm, rel=0.1)