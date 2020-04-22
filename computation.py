from statistics import mean
from collections import deque


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
