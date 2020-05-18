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
        Pass Band: 0 Hz - 3 Hz
        Transition Band: 4.5 Hz
        desired ripple: 80 dB
    """
    FILTER_TAPS =[-0.000002,
0.000005,
0.000007,
-0.000019,
-0.000009,
0.000048,
-0.000000,
-0.000094,
0.000036,
0.000154,
-0.000120,
-0.000215,
0.000273,
0.000245,
-0.000512,
-0.000195,
0.000836,
-0.000000,
-0.001215,
0.000413,
0.001581,
-0.001109,
-0.001818,
0.002123,
0.001765,
-0.003438,
-0.001227,
0.004955,
-0.000000,
-0.006479,
0.002101,
0.007709,
-0.005199,
-0.008234,
0.009322,
0.007547,
-0.014375,
-0.005045,
0.020125,
-0.000000,
-0.026215,
0.008588,
0.032188,
-0.022476,
-0.037541,
0.045966,
0.041785,
-0.094945,
-0.044514,
0.314497,
0.545455,
0.314497,
-0.044514,
-0.094945,
0.041785,
0.045966,
-0.037541,
-0.022476,
0.032188,
0.008588,
-0.026215,
-0.000000,
0.020125,
-0.005045,
-0.014375,
0.007547,
0.009322,
-0.008234,
-0.005199,
0.007709,
0.002101,
-0.006479,
-0.000000,
0.004955,
-0.001227,
-0.003438,
0.001765,
0.002123,
-0.001818,
-0.001109,
0.001581,
0.000413,
-0.001215,
-0.000000,
0.000836,
-0.000195,
-0.000512,
0.000245,
0.000273,
-0.000215,
-0.000120,
0.000154,
0.000036,
-0.000094,
-0.000000,
0.000048,
-0.000009,
-0.000019,
0.000007,
0.000005,
-0.000002]

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
