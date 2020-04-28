import time
from statistics import mean
from collections import deque

from numpy import trapz
from scipy.stats import linregress


class RunningAvg(object):

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


class FirFilter(object):
    """ Finite Impulse Response - Low pass filter
        FIR filter designed with https://www.arc.id.au/FilterDesign.html
        sampling frequency: 22 Hz

        *0.15 Hz - 0.5 Hz
        gain = 1
        desired ripple = 5 dB
        actual ripple = 0 dB
    """
    # FILTER_TAPS = [
    #     -4.4408920985006264e-17,
    #     4.4408920985006264e-17,
    #     1,
    #     4.4408920985006264e-17,
    #     -4.4408920985006264e-17]
    FILTER_TAPS = [-0.000129,
                    -0.002358,
                    -0.003535,
                    0.021576,
                    0.103633,
                    0.217107,
                    0.272727,
                    0.217107,
                    0.103633,
                    0.021576,
                    -0.003535,
                    -0.002358,
                    -0.000129]

    def __init__(self):
        self.samples = deque(maxlen=self.samples_num)

    @property
    def samples_num(self):
        return len(self.FILTER_TAPS)

    def reset(self):
        self.samples.clear()

    def process(self, value):
        if value is not None:
            self.samples.append(value)

        if len(self.samples) < self.samples_num:
            return value

        # dot product of samples and filter taps:
        return sum(x * f for x, f in zip(self.samples, self.FILTER_TAPS))


class Accumulator(object):
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
