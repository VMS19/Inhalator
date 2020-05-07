from statistics import mean

import pytest
from pytest import approx

from algo import VentilationStateMachine
from drivers.driver_factory import DriverFactory
from tests.data.files import path_to_file

NO_BREATH_TIME = VentilationStateMachine.NO_BREATH_ALERT_TIME_SECONDS + 1


@pytest.fixture
def config(default_config):
    c = default_config
    c.state_machine.min_exp_volume_for_exhale = 0
    c.boot_alert_grace_time = 0
    return c


@pytest.mark.usefixtures("config")
@pytest.mark.parametrize("data", [path_to_file("single_cycle_good.csv")])
def test_sampler_avg_volume_calculation(sim_sampler, measurements, data):
    """
    Test average volume calculation working correctly.
    Flow:
        * Run pig simulation which contain one breath cycle.
        * Simulate constant flow of 1.
        * Validate expected average  volume.
    """
    samples_in_file = 90
    for _ in range(samples_in_file):
        sim_sampler.sampling_iteration()

    expected_volume = 842

    msg = f"Expected volume of {expected_volume}, received {measurements.avg_insp_volume}"
    assert measurements.inspiration_volume == approx(expected_volume, rel=0.1), msg

    expected_exp_volume = 501
    msg = f"Expected volume of {expected_exp_volume}, received {measurements.avg_exp_volume}"
    assert measurements.expiration_volume == approx(expected_exp_volume, rel=0.1), msg


@pytest.mark.usefixtures("config")
@pytest.mark.parametrize("data", [path_to_file("several_cycles_good.csv")])
def test_sampler_avg_volume_calculation_multi_cycles(sim_sampler, measurements, data):
    """Test average volume calculation working correctly.

    Flow:
        * Run pig simulation which contain one breath cycle.
        * Simulate constant flow of 1.
        * Validate expected average  volume.
    """
    samples_in_file = 556
    values_to_integrate = 4  # The number of integrals that should be averaged.
    for _ in range(samples_in_file):
        sim_sampler.sampling_iteration()

    volumes = [e[1] for e in sim_sampler.vsm.insp_volumes]
    volumes = volumes[-values_to_integrate:]
    expected_avg = mean(volumes)
    msg = f"Expected average volume of {expected_avg}, received {measurements.avg_insp_volume}"
    assert measurements.inspiration_volume == approx(expected_avg, rel=0.1), msg

    volumes = [e[1] for e in sim_sampler.vsm.exp_volumes]
    volumes = volumes[-values_to_integrate:]
    expected_avg = mean(volumes)
    msg = f"Expected volume of {expected_avg}, received {measurements.avg_exp_volume}"
    assert measurements.expiration_volume == approx(expected_avg, rel=0.1), msg


@pytest.mark.usefixtures("config")
@pytest.mark.parametrize("data", ["noise"])
def test_no_breath(sim_sampler, measurements, data):
    """Test that average volumes reset after time without breathing

    Flow:
        * Run noise simulation for no-breath time.
        * Make sure expected average volumes are zero
    """
    time_intervals = 1 / DriverFactory.MOCK_SAMPLE_RATE_HZ
    num_of_samples = int(NO_BREATH_TIME / time_intervals)
    for _ in range(num_of_samples):
        sim_sampler.sampling_iteration()

    expected_exp_volume = 0
    msg = f"Expected volume of {expected_exp_volume}, received {measurements.avg_exp_volume}"
    assert measurements.expiration_volume == approx(expected_exp_volume, rel=0.1), msg

    expected_insp_volume = 0
    msg = f"Expected volume of {expected_insp_volume}, received {measurements.avg_insp_volume}"
    assert measurements.inspiration_volume == approx(expected_insp_volume, rel=0.1), msg
