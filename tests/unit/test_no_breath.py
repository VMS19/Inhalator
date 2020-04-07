import pytest

from data import alerts
from data.measurements import Measurements
from data.events import Events
from data.configurations import Configurations
from data.thresholds import (O2Range, PressureRange,
                             RespiratoryRateRange, VolumeRange)
from drivers.driver_factory import DriverFactory
from tests.unit.conftest import create_sampler

SIMULATION_SAMPLES = 1000
NO_BREATH_TIME = 13  # seconds


@pytest.fixture
def config():
    c = Configurations.instance()
    c.o2_range = O2Range(min=0, max=100)
    c.pressure_range = PressureRange(min=0, max=30)
    c.resp_rate_range = RespiratoryRateRange(min=0, max=30)
    c.volume_range = VolumeRange(min=0, max=600)
    c.graph_seconds = 12
    c.breathing_threshold = 3.5
    c.log_enabled = False
    return c


@pytest.fixture
def measurements():
    return Measurements()


@pytest.fixture
def events():
    return Events()


def test_sinus_alerts_when_no_breath(events, measurements):
    """Test that no-breath alert is sent after time without breathing

    Flow:
        * Run sinus simulation for a few cycles and make sure no alert was sent.
        * Don't simulate sensors for time required to sent no-breath alert.
        * Make sure a single no-breath alert was sent.
    """
    Configurations.instance().resp_rate_range.min = 0
    sampler = create_sampler("sinus", events, measurements)
    for _ in range(SIMULATION_SAMPLES):
        sampler.sampling_iteration()

    assert len(events.alerts_queue) == 0

    # mocking time continue for no breath time.
    intervals = 1 / DriverFactory.MOCK_SAMPLE_RATE_HZ
    num_of_samples = int(NO_BREATH_TIME / intervals)
    for _ in range(num_of_samples):
        sampler._timer.get_time()
    sampler.sampling_iteration()

    assert len(events.alerts_queue) == 1

    alert = events.alerts_queue.queue.get()
    assert alert == alerts.AlertCodes.NO_BREATH


@pytest.mark.parametrize("data", ["noise", "dead"])
def test_alerts_when_no_breath(events, measurements, data):
    """Test that no-breath alert is sent after time without breathing

    Flow:
        * Run noise simulation for no-breath time.
        * Make sure at least one no-breath alert was sent.
    """
    sampler = create_sampler(data, events, measurements)
    time_intervals = 1 / DriverFactory.MOCK_SAMPLE_RATE_HZ
    num_of_samples = int(NO_BREATH_TIME / time_intervals)
    for _ in range(num_of_samples):
        sampler.sampling_iteration()

    assert len(events.alerts_queue) >= 1

    all_alerts = list(events.alerts_queue.queue.queue)
    for a in all_alerts:
        assert a.code == alerts.AlertCodes.NO_BREATH
