import pytest

from pytest import approx

from data.alerts import AlertCodes
from data.thresholds import VolumeRange
from tests.data.files import path_to_file

TEST_FILE = path_to_file("2020-04-12-sheba-trial-single-cycle.csv")

FAST_FORWARD = 100
LOW_THRESHOLD = -50000
HIGH_THRESHOLD = 50000
SIMULATION_SAMPLES = 1000


@pytest.mark.parametrize("data", [TEST_FILE])
def test_sampler_volume_calculation(app, measurements, data):
    """Test volume calculation working correctly."""
    app.run_iterations(SIMULATION_SAMPLES)
    expected_volume = 660.280
    msg = f"Expected volume of {expected_volume}, received {measurements.inspiration_volume}"
    assert measurements.inspiration_volume == approx(expected_volume, rel=0.1), msg


@pytest.mark.parametrize("data", [TEST_FILE])
@pytest.mark.parametrize(
    ["threshold", "alert_code"],
    [(HIGH_THRESHOLD, AlertCodes.VOLUME_LOW),
     (LOW_THRESHOLD, AlertCodes.VOLUME_HIGH)]
)
def test_volume_threshold_alerts(app, events, config, data, threshold, alert_code):
    assert len(events.alerts_queue) == 0
    app.run_iterations(1, fast_forward=True)
    assert len(events.alerts_queue) == 0

    config.thresholds.volume = VolumeRange(threshold, threshold)
    app.run_iterations(SIMULATION_SAMPLES)

    assert len(events.alerts_queue) > 0

    all_alerts = list(events.alerts_queue.active_alerts)
    assert all([alert == alert_code for alert in all_alerts])
