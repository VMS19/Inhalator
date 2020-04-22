import logging
import numpy as np
from collections import deque

from converter import flow_to_pressure


class TailDetector:
    TAIL_THRESHOLD = 8  # absolute flow value
    SLOPE_THRESHOLD = 5  # absolute flow slope
    MIN_TAIL_LENGTH = 6  # samples
    GRACE_LENGTH = 5  # samples

    def __init__(self):
        self.current_tail = deque(maxlen=5000)
        self.grace_count = 0
        self.previous_sample = None
        self.previous_timestamp = None
        self.last_tails = deque(maxlen=5)
        self.log = logging.getLogger(__name__)

        # debug
        self.timestamps = deque(maxlen=5000)

    def process(self, flow, timestamp):
        current_tail_length = len(self.current_tail)
        if self.previous_sample is None:
            self.previous_sample = flow
            self.previous_timestamp = timestamp
            return

        slope = (flow - self.previous_sample) / (timestamp - self.previous_timestamp)

        if abs(flow) > self.TAIL_THRESHOLD:
            # self.log.debug(f"Entered threshold")
            if len(self.current_tail) > 0:
                # self.log.debug(f"\tTail already exists")
                if len(self.current_tail) > self.MIN_TAIL_LENGTH:
                    # self.log.debug(f"\t\tDeleting existing tail")
                    self.last_tails.appendleft(self.current_tail)

                    self.current_tail.clear()
                    self.grace_count = 0

        elif abs(slope) <= self.SLOPE_THRESHOLD:
            self.grace_count = 0
            self.current_tail.appendleft(flow)
            self.timestamps.appendleft(timestamp)

        else:
            if len(self.current_tail) > 0 and self.grace_count >= self.GRACE_LENGTH:
                if len(self.current_tail) > self.MIN_TAIL_LENGTH:
                    self.last_tails.appendleft(self.current_tail)
                    self.current_tail.clear()

                self.grace_count = 0

            else:
                self.grace_count += 1

        if current_tail_length > self.MIN_TAIL_LENGTH and len(self.current_tail) == 0:
            print(self.timestamps[0], self.timestamps[-1])
            self.timestamps.clear()


class NewTailDetector:
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
