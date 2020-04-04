import logging
import time
from collections import deque
from statistics import mean

from scipy.stats import linregress

TRACE = logging.DEBUG - 1
logging.addLevelName(TRACE, 'TRACE')


class VolumeAccumulator(object):
    def __init__(self):
        self.air_volume_liter = 0
        self.last_sample_ts = None

    def accumulate(self, timestamp, air_flow):
        if self.last_sample_ts is not None:
            elapsed_time_seconds = timestamp - self.last_sample_ts
            elapsed_time_minutes = elapsed_time_seconds / 60
            # flow is measured in Liter/minute, so we multiply the last read by
            # the time elapsed in minutes to calculate the accumulated volume
            # inhaled in this inhale.
            self.air_volume_liter += air_flow * elapsed_time_minutes
        self.last_sample_ts = timestamp

    def reset(self):
        self.air_volume_liter = 0
        self.last_sample_ts = None


class RunningAvg(object):

    def __init__(self, max_samples):
        self.samples = deque(maxlen=max_samples)

    def reset(self):
        self.samples.clear()

    def process(self, pressure):
        self.samples.append(pressure)
        return mean(self.samples)


class RateMeter(object):

    def __init__(self, time_span_seconds, max_samples):
        """
        :param time_span_seconds: How long (seconds) the sliding window of the
            running average should be
        """
        if time_span_seconds <= 0:
            raise ValueError("Time span must be non-zero and positive")
        self.time_span_seconds = time_span_seconds
        self.samples = deque(maxlen=max_samples)

    def reset(self):
        self.samples.clear()

    def beat(self, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        self.samples.append(timestamp)
        # Discard beats older than `self.time_span_seconds`
        while self.samples[0] < (timestamp - self.time_span_seconds):
            self.samples.popleft()

        # Basically the rate is the number of elements left, since the container
        # represents only the relevant time span.
        # BUT there is a corner-case at the beginning of the process - what if
        # we did not yet passed a single time span? The rate then will be
        # artificially low. For example on the first two beats, even if there
        # are only 10 seconds between them and the time span is 60 seconds, the
        # rate will be 2/min, instead of 6/min (1 beats every 10 seconds).
        # This is why we compute the interval between the oldest and newest beat
        # in the data, and calculate the rate based on it. After we accumulate
        # enough data, this interval will be pretty close to the desired span.
        oldest = self.samples[0]
        interval = timestamp - oldest
        # protect against division by zero
        if interval == 0:
            # Technically rate is infinity, but 0 will be more descriptive
            return 0

        # We subtract 1 because we have both 1st and last sentinels.
        rate = (len(self.samples) - 1) * (self.time_span_seconds / interval)
        return rate


class RunningSlope(object):

    def __init__(self, num_samples=10, period_ms=100):
        self.period_ms = period_ms
        self.max_samples = num_samples
        self.data = deque(maxlen=num_samples)
        self.ts = deque(maxlen=num_samples)

    def reset(self):
        self.data.clear()
        self.ts.clear()

    def add_sample(self, value, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        self.data.append(value)
        self.ts.append(timestamp)
        if len(self.data) < self.max_samples:
            return None  # Not enough data to infer.
        slope, _, _, _, _ = linregress(self.ts, self.data)
        return slope
