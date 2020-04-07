import csv
import os
import time

import pytest
from pytest import approx

from algo import VentilationStateMachine, Sampler
from data.events import Events
from data.measurements import Measurements
from data.alerts import AlertCodes
from data.configurations import *
from drivers.driver_factory import DriverFactory


SIMULATION_FOLDER = "simulation"

SAMPLE_TIME_DIFF = 0.045  # seconds
TIME_FROM_BEAT_TO_SIM_END = 3.69  # seconds
TIME_FROM_SIM_START_TO_INHALE = 1.62  # seconds


@pytest.fixture
def events():
    return Events()


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def driver_factory(simulation_data):
    return DriverFactory(simulation_mode=True,
                         simulation_data=simulation_data)


@pytest.fixture
def sampler(measurements, events, driver_factory, bpm):
    driver_factory.MOCK_BPM = bpm
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    return Sampler(measurements, events, flow_sensor, pressure_sensor,
                   a2d, timer)


@pytest.fixture
def config():
    c = Configurations.instance()
    c.o2_range = O2Range(min=0, max=100)
    c.pressure_range = PressureRange(min=-1, max=30)
    c.resp_rate_range = RespiratoryRateRange(min=0, max=30)
    c.volume_range = VolumeRange(min=100, max=10000)
    c.graph_seconds = 12
    c.log_enabled = False
    return c


@pytest.fixture
def real_data():
    this_dir = os.path.dirname(__file__)
    with open(os.path.join(this_dir, SIMULATION_FOLDER,
                           "pig_sim_cycle.csv"), "r") as f:
        reader = csv.DictReader(f)
        timestamps = []
        pressure_values = []
        flow_values = []
        oxygen_values = []
        for row in reader:
            timestamps.append(float(row['time elapsed (seconds)']))
            pressure_values.append(float(row['pressure']))
            flow_values.append(float(row['flow']))
            oxygen_values.append(float(row['oxygen']))

    return timestamps, pressure_values, flow_values, oxygen_values


def test_bpm_calculation_const_rate(real_data):
    """Test BPM calculated correctly with constant BPM simulation

    Flow:
        * Run pig simulation for entire breath cycle
        * Check BPM calculated correctly
    """
    timestamps, pressure_values, flow_values, oxygen_values = real_data
    timestamps += [timestamps[-1] + SAMPLE_TIME_DIFF * (i + 1)
                   for i in range(len(timestamps))]
    vsm = VentilationStateMachine(Measurements(), Events())
    for t, p, f, o in zip(timestamps, pressure_values * 2,
                          flow_values * 2, oxygen_values * 2):
        vsm.update(
            pressure_cmh2o=p,
            flow_slm=f,
            o2_percentage=o,
            timestamp=t,
        )

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
    timestamps, pressure_values, flow_values, oxygen_values = real_data
    timestamps += [timestamps[-1] + SAMPLE_TIME_DIFF * (i + 1)
                   for i in range(len(timestamps) * 100)]
    vsm = VentilationStateMachine(Measurements(), Events())
    for t, p, f, o in zip(timestamps, pressure_values * 101,
                          flow_values * 101, oxygen_values * 101):
        vsm.update(
            pressure_cmh2o=p,
            flow_slm=f,
            o2_percentage=o,
            timestamp=t,
        )

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
    timestamps, pressure_values, flow_values, oxygen_values = real_data
    timestamps += [timestamps[-1] + rate * SAMPLE_TIME_DIFF * (i + 1)
                   for i in range(len(timestamps))]
    vsm = VentilationStateMachine(Measurements(), Events())
    for t, p, f, o in zip(timestamps, pressure_values * 2,
                          flow_values * 2, oxygen_values * 2):
        vsm.update(
            pressure_cmh2o=p,
            flow_slm=f,
            o2_percentage=o,
            timestamp=t,
        )

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
    timestamps, pressure_values, flow_values, oxygen_values = real_data
    timestamps += [timestamps[-1] + rates[0] * SAMPLE_TIME_DIFF * (i + 1)
                   for i in range(len(pressure_values))]
    timestamps += [timestamps[-1] + rates[1] * SAMPLE_TIME_DIFF * (i + 1)
                   for i in range(len(pressure_values))]
    vsm = VentilationStateMachine(Measurements(), Events())
    for t, p, f, o in zip(timestamps, pressure_values * 3,
                          flow_values * 3, oxygen_values * 3):
        vsm.update(
            pressure_cmh2o=p,
            flow_slm=f,
            o2_percentage=o,
            timestamp=t,
        )

    samples_len = len(vsm.breathes_rate_meter.samples) - 1
    time_span_seconds = vsm.breathes_rate_meter.time_span_seconds
    interval = TIME_FROM_BEAT_TO_SIM_END
    interval += rates[0] * (TIME_FROM_SIM_START_TO_INHALE + TIME_FROM_BEAT_TO_SIM_END)
    interval += rates[1] * TIME_FROM_SIM_START_TO_INHALE
    expected_bpm = samples_len * (time_span_seconds / interval)
    assert vsm._measurements.bpm == approx(expected_bpm, rel=0.1)


@pytest.mark.parametrize('simulation_data,bpm,bpm_range,expected_alert',
                         [("sinus", 18, (13, 17), AlertCodes.BPM_HIGH),
                          ("sinus", 12, (13, 17), AlertCodes.BPM_LOW),
                          ("sinus", 15, (13, 17), None)])
def test_bpm_alert(bpm_range, expected_alert, events, config, sampler):
    """Test High and Low BPM alert are raised when bpm above or below range."""
    simulation_length = 2

    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    # Sinus simulation is 15 bpm. set max threshold below it.
    config.resp_rate_range = RespiratoryRateRange(*bpm_range)

    current_time = time.time()
    while time.time() - current_time < simulation_length:
        time.sleep(0.001)
        sampler.sampling_iteration()

    if expected_alert is None:
        assert len(events.alerts_queue) == 0, \
            "BPM alert raised, but bpm is normal"

    else:
        assert len(events.alerts_queue) > 0, "BPM alert not raised"
        all_alerts = list(events.alerts_queue.queue.queue)
        assert all(alert == expected_alert for alert in all_alerts), \
            "wrong alert was raised"


@pytest.mark.parametrize('simulation_data,bpm', [("sinus", 15)])
def test_no_bpm_alert_on_startup(events, config, sampler):
    """Test BPM alert is not false raised on startup - not enough samples."""
    simulation_length = 0.01

    assert len(events.alerts_queue) == 0
    sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    # Sinus simulation is 15 bpm. set min threshold above, to simulate
    # insufficient sampling.
    config.resp_rate_range = RespiratoryRateRange(20, 30)

    current_time = time.time()
    while time.time() - current_time < simulation_length:
        time.sleep(0.001)
        sampler.sampling_iteration()

    assert len(events.alerts_queue) == 0, \
        "BPM alert raised before sufficient breath cycles were sampled"
