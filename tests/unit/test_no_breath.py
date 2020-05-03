import pytest

from algo import VentilationStateMachine
from data import alerts
from configuration.thresholds import PressureRange
from drivers.driver_factory import DriverFactory

SIMULATION_SAMPLES = 1000
NO_BREATH_TIME = VentilationStateMachine.NO_BREATH_ALERT_TIME_SECONDS + 1


@pytest.fixture
def config(default_config):
    c = default_config
    # Adapt the threshold for the sinus simulation.
    c.thresholds.pressure = PressureRange(min=0, max=30)
    c.thresholds.volume.min = 0
    return c


@pytest.mark.usefixtures("config")
@pytest.mark.parametrize("data", ["sinus"])
def test_sinus_does_not_trigger_alert(sim_sampler, events, data):
    """Test that synthesized breath signal does not trigger the alert."""
    for _ in range(SIMULATION_SAMPLES):
        sim_sampler.sampling_iteration()

    assert len(events.alerts_queue) == 0,\
        f"Unexpected alerts: {events.alerts_queue.active_alerts}"


@pytest.mark.parametrize("data", ["dead", "noise"])
@pytest.mark.usefixtures("config")
def test_dead_man_alerts_when_no_breath(sim_sampler, events, data):
    """Test that no-breath alert is sent after time without breathing"""
    time_intervals = 1 / DriverFactory.MOCK_SAMPLE_RATE_HZ
    num_of_samples = int(NO_BREATH_TIME / time_intervals)
    for i in range(num_of_samples):
        sim_sampler.sampling_iteration()

    assert len(events.alerts_queue) > 0

    all_alerts = list(events.alerts_queue.active_alerts)
    assert any(a.code == alerts.AlertCodes.NO_BREATH for a in all_alerts),\
        f"NO_BREATH is not in {all_alerts}"
