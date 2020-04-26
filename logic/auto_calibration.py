import logging

import numpy as np


class TimeRange:
    def __init__(self, start_time, length):
        self.start_time = start_time
        self.length = length

    def __contains__(self, timestamp):
        return timestamp - self.start_time <= self.length


class AutoFlowCalibrator:
    def __init__(self, dp_driver, interval_length, iterations,
                 iteration_length, sample_threshold, slope_threshold,
                 min_tail_length, grace_length):
        self.dp_driver = dp_driver
        self.interval_length = interval_length
        self.iterations = iterations
        self.iteration_length = iteration_length

        self.log = logging.getLogger(__name__)
        self.interval_start_time = None
        self.iteration_start_time = None
        self.iterations_count = 0
        self.tail_detector = TailDetector(dp_driver=dp_driver,
                                          sample_threshold=sample_threshold,
                                          slope_threshold=slope_threshold,
                                          min_tail_length=min_tail_length,
                                          grace_length=grace_length)

    @property
    def interval(self):
        return TimeRange(self.interval_start_time, self.interval_length)

    @property
    def iteration(self):
        return TimeRange(self.iteration_start_time, self.iteration_length)

    def get_offset(self, flow_slm, ts):
        if (self.interval_start_time is None or self.iteration_start_time is None or
                ts not in self.interval):
            self.log.debug("Starting a new auto calibration interval")
            self.interval_start_time = ts
            self.iteration_start_time = ts
            self.iterations_count = 0

        if ts in self.iteration:
            self.tail_detector.add_sample(flow_slm, ts)
            return None

        if self.iterations_count < self.iterations:
            self.log.debug("Done accumulating within one iteration")
            tail_offset = self.tail_detector.process()
            if tail_offset is not None:
                self.log.debug("Tail offset is %f L/min",
                               self.dp_driver.pressure_to_flow(tail_offset))
                self.log.debug("Writing offset of %f to the driver",
                               tail_offset)
                self.dp_driver.set_calibration_offset(tail_offset)

            self.iteration_start_time = None
            self.tail_detector.reset()
            self.iterations_count += 1

        if self.iterations_count == self.iterations:
            self.log.info("Done accumulating within the interval")
            self.iterations_count += 1
            return self.dp_driver.get_calibration_offset()

        return None


class TailDetector:
    def __init__(self, dp_driver, sample_threshold, slope_threshold,
                 min_tail_length, grace_length):
        self.dp_driver = dp_driver
        self.sample_threshold = sample_threshold
        self.slope_threshold = slope_threshold
        self.min_tail_length = min_tail_length
        self.grace_length = grace_length

        self.samples = []
        self.timestamps = []
        self.tail_indices = []
        self.candidate_indices = []
        self.grace_count = 0

    def reset(self):
        self.samples = []
        self.timestamps = []
        self.tail_indices = []
        self.candidate_indices = []
        self.grace_count = 0

    def add_sample(self, sample, timestamp):
        self.samples.append(sample)
        self.timestamps.append(timestamp)

    def check_close_up(self, current_index, in_grace=False):
        if len(self.samples) > 0 and (self.grace_count >= self.grace_length or
                                      current_index == len(self.samples) - 1):
            tail = self.candidate_indices[:-self.grace_count]
            if len(tail) >= self.min_tail_length:
                self.tail_indices += tail[int(len(tail) * 3 / 4):]

            self.grace_count = 0
            self.candidate_indices = []

        elif in_grace:
            self.grace_count += 1

    def process(self):
        for index in range(1, len(self.samples)):
            slope = ((self.samples[index] - self.samples[index - 1]) /
                     (self.timestamps[index] - self.timestamps[index - 1]))
            if abs(self.samples[index]) >= self.sample_threshold:
                self.check_close_up(index)

            elif abs(slope) < self.slope_threshold:
                self.candidate_indices.append(index)
                self.grace_count = 0

            else:
                self.candidate_indices.append(index)
                self.check_close_up(index, in_grace=True)

        indices = np.array(self.tail_indices)
        if len(indices) == 0:
            return None

        if len(self.tail_indices) < self.min_tail_length:
            return None

        dp = np.array([self.dp_driver.flow_to_pressure(f) +
                       self.dp_driver.get_calibration_offset()
                       for f in self.samples])

        tails_dp = dp[indices]
        return np.average(tails_dp)
