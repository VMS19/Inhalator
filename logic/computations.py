"""Mathematical, general purpose computations."""
import time
from statistics import mean
from collections import deque

from numpy import trapz
from scipy.stats import linregress
from scipy import signal


class RunningAvg:
    """Average values over a sliding window of samples."""

    def __init__(self, max_samples):
        self.samples = deque(maxlen=max_samples)

    def reset(self):
        self.samples.clear()

    def process(self, value):
        if value is not None:
            self.samples.append(value)

        if len(self.samples) == 0:
            return 0

        return mean(self.samples)


class Accumulator:
    """Accumulate volumes using Trapezoidal numerical integration."""

    def __init__(self):
        self.samples = deque()
        self.timestamps = deque()

    def add_sample(self, timestamp, value):
        self.samples.append(value)
        self.timestamps.append(timestamp)

    def integrate(self):
        return trapz(self.samples, x=self.timestamps)

    def reset(self):
        self.samples.clear()
        self.timestamps.clear()


class RunningSlope:
    """Calculate slope on window of samples."""

    def __init__(self, num_samples=10, period_ms=100):
        self.period_ms = period_ms
        self.max_samples = num_samples
        self.data = deque(maxlen=num_samples)
        self.timestamps = deque(maxlen=num_samples)

    def reset(self):
        self.data.clear()
        self.timestamps.clear()

    def add_sample(self, value, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        self.data.append(value)
        self.timestamps.append(timestamp)
        if len(self.data) < self.max_samples:
            return None  # Not enough data to infer.
        slope, _, _, _, _ = linregress(self.timestamps, self.data)
        return slope


class RunningButterworth:
    """Average values over a sliding window of samples."""

    def __init__(self, max_samples, sps, fc):
        self.fc = fc
        self.sps = sps
        self.samples = deque(maxlen=max_samples)

    def reset(self):
        self.samples.clear()

    def process(self, value):
        if value is not None:
            self.samples.append(value)

        if len(self.samples) < self.samples.maxlen:
            return 0

        w = self.fc / (self.sps / 2)
        b, a = signal.butter(5, w, 'low')
        samples_list = list(self.samples)
        return signal.filtfilt(b, a, samples_list)