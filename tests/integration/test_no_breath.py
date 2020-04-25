import pytest

from data import alerts
from drivers.driver_factory import DriverFactory

SIMULATION_SAMPLES = 1000
NO_BREATH_TIME = 13  # seconds


@pytest.mark.parametrize("data", ["sinus"])
def test_sinus_alerts_when_no_breath(app, events, data, sim_sampler):
    """Test that no-breath alert is sent after time without breathing

    Flow:
        * Run sinus simulation for a few cycles and make sure no alert was sent.
        * Don't simulate sensors for time required to sent no-breath alert.
        * Make sure a single no-breath alert was sent.
    """
    app.run_iterations(SIMULATION_SAMPLES)
    assert len(events.alerts_queue) == 0

    # mocking time continue for no breath time.
    intervals = 1 / DriverFactory.MOCK_SAMPLE_RATE_HZ
    num_of_samples = int(NO_BREATH_TIME / intervals)
    for _ in range(num_of_samples):
        sim_sampler._timer.get_time()

    app.run_iterations(1)
    assert len(events.alerts_queue) == 1
    alert = events.alerts_queue.queue.get()
    assert alert == alerts.AlertCodes.NO_BREATH


@pytest.mark.parametrize("data", ["dead", "noise"])
def test_alerts_when_no_breath(app, events, data):
    """Test that no-breath alert is sent after time without breathing"""
    time_intervals = 1 / DriverFactory.MOCK_SAMPLE_RATE_HZ
    num_of_samples = int(NO_BREATH_TIME / time_intervals)
    app.run_iterations(num_of_samples)
    assert len(events.alerts_queue) == 1, f"Unexpected alerts: {events.alerts_queue}"
    assert events.alerts_queue.active_alerts[0] == alerts.AlertCodes.NO_BREATH,\
        f"Wrong alert: {events.alerts_queue.active_alerts[0]}"
