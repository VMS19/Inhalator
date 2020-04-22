import numpy as np

from converter import flow_to_pressure


class TailDetector:
    # TODO: move to config
    TAIL_THRESHOLD = 5  # absolute flow value
    SLOPE_THRESHOLD = 10  # absolute flow slope
    MIN_TAIL_LENGTH = 12  # samples
    GRACE_LENGTH = 5  # samples

    def __init__(self):
        self.samples = []
        self.timestamps = []
        self.tail_indices = []
        self.candidate_indices = []

        self.grace_count = 0

    def add_sample(self, sample, timestamp):
        self.samples.append(sample)
        self.timestamps.append(timestamp)

    def check_close_up(self, current_index, in_grace=False):
        if len(self.samples) > 0 and (self. grace_count >= self.GRACE_LENGTH or current_index == len(self.samples) - 1):
            if len(self.samples) >= self.MIN_TAIL_LENGTH:
                self.tail_indices += self.candidate_indices[:-self.grace_count]

            self.grace_count = 0
            self.candidate_indices = []

        elif in_grace:
            self.grace_count += 1

    def process(self):
        for index in range(1, len(self.samples)):
            slope = (self.samples[index] - self.samples[index - 1]) / (self.timestamps[index] - self.timestamps[index - 1])
            if abs(self.samples[index]) >= self.TAIL_THRESHOLD:
                self.check_close_up(index)

            elif abs(slope) < self.SLOPE_THRESHOLD:
                self.candidate_indices.append(index)
                self.grace_count = 0

            else:
                self.check_close_up(index, in_grace=True)

        indices = np.array(self.tail_indices)
        dp = np.array([flow_to_pressure(f) for f in self.samples])
        tails_dp = dp[indices]
        return np.average(tails_dp)
