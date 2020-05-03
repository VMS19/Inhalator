import pytest
from pytest import approx

from data.alerts import AlertCodes
from configuration.thresholds import O2Range, PressureRange, VolumeRange
from drivers.driver_factory import DriverFactory
from tests.data.files import path_to_file


LOW_THRESHOLD = -50000
HIGH_THRESHOLD = 50000

SECONDS_IN_CYCLE = 60 / DriverFactory.MOCK_BPM
SAMPLES_IN_CYCLE = int(DriverFactory.MOCK_SAMPLE_RATE_HZ * SECONDS_IN_CYCLE)


@pytest.fixture
def config(default_config):
    c = default_config
    c.thresholds.o2 = O2Range(min=0, max=100)
    c.thresholds.pressure = PressureRange(min=-1, max=30)
    c.thresholds.volume = VolumeRange(min=100, max=600)
    c.calibration.auto_calibration.enable = False
    return c


@pytest.mark.parametrize("data", [path_to_file("single_cycle_good.csv")])
@pytest.mark.usefixtures("config")
def test_volume_calculation(sim_sampler, measurements, events, data):
    """Test volume calculation working correctly.

    Flow:
        * Run pig simulation which contain one breath cycle.
        * Simulate constant flow of 1.
        * Validate expected volume.
    """
    test_samples = 90  # in single_cycle_good.csv
    for _ in range(test_samples):
        sim_sampler.sampling_iteration()

    expected_volume = 842
    msg = f"Expected volume of {expected_volume}, received {measurements.inspiration_volume}"
    assert measurements.inspiration_volume == approx(expected_volume, rel=0.1), msg

    expected_exp_volume = 501
    msg = f"Expected volume of {expected_exp_volume}, received {measurements.expiration_volume}"
    assert measurements.expiration_volume == approx(expected_exp_volume, rel=0.1), msg


@pytest.mark.parametrize(
    ["data", "threshold", "alert_code"],
    [("sinus", HIGH_THRESHOLD, AlertCodes.VOLUME_LOW),
     ("sinus", LOW_THRESHOLD, AlertCodes.VOLUME_HIGH)])
def test_thresholds(sim_sampler, events, config, data, threshold, alert_code):
    """Verify that alert is raised if we exceed a threshold"""
    config.thresholds.volume = VolumeRange(threshold, threshold)
    for _ in range(SAMPLES_IN_CYCLE * 2):
        sim_sampler.sampling_iteration()

    assert len(events.alerts_queue) > 0
    all_alerts = list(events.alerts_queue.active_alerts)
    assert all(alert.code == alert_code for alert in all_alerts)
