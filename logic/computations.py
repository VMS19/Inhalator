from statistics import mean
from collections import deque

from numpy import trapz


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
