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
    FILTER_TAPS = [0.000017,
                    0.000029,
                    0.000042,
                    0.000052,
                    0.000052,
                    0.000037,
                    -0.000000,
                    -0.000064,
                    -0.000156,
                    -0.000273,
                    -0.000409,
                    -0.000546,
                    -0.000664,
                    -0.000735,
                    -0.000731,
                    -0.000620,
                    -0.000381,
                    0.000000,
                    0.000521,
                    0.001160,
                    0.001871,
                    0.002589,
                    0.003225,
                    0.003679,
                    0.003844,
                    0.003619,
                    0.002926,
                    0.001719,
                    -0.000000,
                    -0.002172,
                    -0.004672,
                    -0.007313,
                    -0.009847,
                    -0.011982,
                    -0.013398,
                    -0.013775,
                    -0.012818,
                    -0.010288,
                    -0.006032,
                    0.000000,
                    0.007733,
                    0.016963,
                    0.027359,
                    0.038480,
                    0.049800,
                    0.060738,
                    0.070704,
                    0.079134,
                    0.085542,
                    0.089547,
                    0.090909,
                    0.089547,
                    0.085542,
                    0.079134,
                    0.070704,
                    0.060738,
                    0.049800,
                    0.038480,
                    0.027359,
                    0.016963,
                    0.007733,
                    0.000000,
                    -0.006032,
                    -0.010288,
                    -0.012818,
                    -0.013775,
                    -0.013398,
                    -0.011982,
                    -0.009847,
                    -0.007313,
                    -0.004672,
                    -0.002172,
                    -0.000000,
                    0.001719,
                    0.002926,
                    0.003619,
                    0.003844,
                    0.003679,
                    0.003225,
                    0.002589,
                    0.001871,
                    0.001160,
                    0.000521,
                    0.000000,
                    -0.000381,
                    -0.000620,
                    -0.000731,
                    -0.000735,
                    -0.000664,
                    -0.000546,
                    -0.000409,
                    -0.000273,
                    -0.000156,
                    -0.000064,
                    -0.000000,
                    0.000037,
                    0.000052,
                    0.000052,
                    0.000042,
                    0.000029,
                    0.000017]
d
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
