import csv

from os.path import join, dirname
from itertools import cycle
from statistics import mean

import pytest
from pytest import approx

from algo import VentilationStateMachine
from data.alerts import AlertCodes
from data.configurations import *
from drivers.driver_factory import DriverFactory
from tests.data.files import path_to_file

SIMULATION_FOLDER = join(dirname(__file__), "simulation")


@pytest.fixture
def config(default_config):
    c = default_config
    c.thresholds.pressure.min = -1
    c.thresholds.o2.min = 0
    c.thresholds.volume.min = 0
    return c


@pytest.fixture
def driver_factory(data, bpm):
    df = DriverFactory(simulation_mode=True, simulation_data=data)
    df.MOCK_BPM = bpm
    return df


@pytest.fixture
def real_data():
    file_path = path_to_file("2020-04-12-sheba-trial-single-cycle.csv")
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        data = list(reader)
    timestamps = [float(row['time elapsed (seconds)']) for row in data]
    intervals = [j - i for i, j in zip(timestamps[:-1], timestamps[1:])]
    avg_interval = mean(intervals)
    cycle_duration = timestamps[-1] - timestamps[0]
    pressure = [float(row['pressure']) for row in data]
    flow = [float(row['flow']) for row in data]
    oxygen = [float(row['oxygen']) for row in data]

    return cycle_duration, avg_interval, len(data), pressure, flow, oxygen


@pytest.mark.usefixtures("config")
@pytest.mark.parametrize("cycles", [2, 10, 50])
def test_bpm_calculation_const_rate(cycles, real_data, measurements, events):
    """Test BPM calculated correctly with constant BPM simulation

    Flow:
        * Run pig simulation for entire breath cycle
        * Check BPM calculated correctly
    """
    duration, interval, num_samples, pressure, flow, oxygen = real_data
    expected_bpm = round(60 / duration)
    timestamps = [interval * i for i in range(num_samples * cycles)]
    vsm = VentilationStateMachine(measurements, events)
    for t, p, f, o in zip(timestamps, cycle(pressure), cycle(flow), cycle(oxygen)):
        vsm.update(
            pressure_cmh2o=p,
            flow_slm=f,
            o2_percentage=o,
            timestamp=t,
        )
    assert vsm._measurements.bpm == approx(expected_bpm, rel=0.5)


@pytest.mark.parametrize('data,bpm,bpm_range,expected_alert',
                         [("sinus", 18, (13, 17), AlertCodes.BPM_HIGH),
                          ("sinus", 12, (13, 17), AlertCodes.BPM_LOW),
                          ("sinus", 15, (13, 17), None)])
def test_bpm_alert(data, bpm, bpm_range, expected_alert, events, config, sim_sampler):
    """Test High and Low BPM alert are raised when bpm above or below range."""
    breath_duration = 60 / bpm
    samples_in_breath = int(DriverFactory.MOCK_SAMPLE_RATE_HZ * breath_duration)
    config.thresholds.respiratory_rate = RespiratoryRateRange(*bpm_range)
    # Set volume range to prevent volume alerts.
    config.thresholds.volume = VolumeRange(-500000, 500000)

    for _ in range(samples_in_breath * 10):
        # 10 breaths should be enough to calculate rate
        sim_sampler.sampling_iteration()

    assert len(events.alerts_queue.active_alerts) == 0 if expected_alert is None else 1
    if expected_alert is not None:
        assert events.alerts_queue.active_alerts[0] == expected_alert,\
            "wrong alert was raised"


@pytest.mark.parametrize('data,bpm', [("sinus", 15)])
def test_no_bpm_alert_on_startup(data, bpm, events, config, sim_sampler):
    """Test that at least 2 breaths are required to calculate rate"""
    # Intentionally absurd in order to catch any possible rate as an alert.
    config.thresholds.respiratory_rate = RespiratoryRateRange(min=100, max=0)
    # Set volume range to prevent volume alerts.
    config.thresholds.volume = VolumeRange(-500000, 500000)
    breath_duration = 60 / bpm
    samples_in_breath = int(DriverFactory.MOCK_SAMPLE_RATE_HZ * breath_duration)

    assert len(events.alerts_queue) == 0
    sim_sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0

    for _ in range(samples_in_breath):
        sim_sampler.sampling_iteration()

    assert sim_sampler.vsm
    assert len(events.alerts_queue) == 0, \
        "BPM alert raised before sufficient breath cycles were sampled"
