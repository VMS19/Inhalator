from unittest.mock import patch

import pytest

from data import alerts
from configuration.thresholds import PressureRange

GRACE_TIME = 2
EPSILON = GRACE_TIME / 1000

LOW_THRESHOLD = -50000
HIGH_THRESHOLD = 50000


@pytest.fixture
def config(default_config):
    c = default_config
    c.boot_alert_grace_time = GRACE_TIME
    return c


@patch("data.alerts.uptime")
@pytest.mark.parametrize("data", ["sinus"])
def test_grace_time_alerts(mocked_uptime, events, config, sim_sampler, data):
    """Check no alerts in grace time, and alert received after."""
    mocked_uptime.return_value = GRACE_TIME - EPSILON

    config.thresholds.pressure = PressureRange(HIGH_THRESHOLD, HIGH_THRESHOLD)

    sim_sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0, "shouldn't get any alerts during grace time"

    mocked_uptime.return_value = GRACE_TIME + EPSILON
    sim_sampler.sampling_iteration()
    assert len(events.alerts_queue) == 1

    all_alerts = list(events.alerts_queue.queue.queue)
    assert all(alert == alerts.AlertCodes.PRESSURE_LOW for alert in all_alerts)


@patch("data.alerts.uptime")
@patch("time.time")
@pytest.mark.parametrize('current_time', [GRACE_TIME - EPSILON, GRACE_TIME + EPSILON])
@pytest.mark.parametrize("data", ["sinus"])
def test_grace_time_alerts_move_time_forward(
        mocked_time, mocked_uptime, events, config, sim_sampler, current_time, data):
    """Check no alerts in grace time, and alert received after.

    Check that moving time after grace time doesn't cause alert in grace time.
    Check that moving time before grace time doesn't prevent alert after grace time.
    """
    mocked_uptime.return_value = GRACE_TIME - EPSILON
    mocked_time.return_value = current_time

    config.thresholds.pressure = PressureRange(HIGH_THRESHOLD, HIGH_THRESHOLD)

    sim_sampler.sampling_iteration()
    assert len(events.alerts_queue) == 0, "shouldn't get any alerts during grace time"

    mocked_uptime.return_value = GRACE_TIME + EPSILON
    sim_sampler.sampling_iteration()
    assert len(events.alerts_queue) == 1

    all_alerts = list(events.alerts_queue.queue.queue)
    assert all(alert == alerts.AlertCodes.PRESSURE_LOW for alert in all_alerts)
