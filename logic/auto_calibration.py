import logging

import numpy as np


class AutoFlowCalibrator:
    def __init__(self, dp_driver, interval_between_calibrations,
                 calibration_length, iterations):
        self.dp_driver = dp_driver
        self.interval_between_calibrations = interval_between_calibrations
        self.calibration_length = calibration_length
        self.iterations = iterations

        self.log = logging.getLogger(__name__)
        self.interval_start_time = None
        self.window_start_time = None
        self.iterations_count = 0
        self.tail_detector = TailDetector(dp_driver=dp_driver)

    def get_offset(self, flow_slm, ts):
        if self.interval_start_time is None:
            self.log.debug("Starting auto calibration interval")
            self.interval_start_time = ts

        if self.window_start_time is None:
            self.log.debug("Starting auto calibration window")
            self.window_start_time = ts

        if ts - self.interval_start_time >= self.interval_between_calibrations:
            if ts - self.window_start_time < self.calibration_length:
                self.tail_detector.add_sample(flow_slm, ts)
            else:
                self.log.debug("Done accumulating within tail window")
                tail_offset = self.tail_detector.process()
                if tail_offset is not None:
                    self.log.debug("Tail offset is %f DP", tail_offset)
                    self.log.debug(
                        "Tail offset is %f L/min",
                        self.dp_driver.pressure_to_flow(tail_offset))
                    self.dp_driver.set_calibration_offset(tail_offset)

                self.window_start_time = None
                self.tail_detector = TailDetector(self.dp_driver)
                self.iterations_count += 1

                if self.iterations_count >= self.iterations:
                    self.log.info("Done accumulating within tail interval")
                    self.iterations_count = 0
                    self.interval_start_time = None
                    return self.dp_driver.get_calibration_offset()

        return None


class TailDetector:
    # TODO: move to config
    TAIL_THRESHOLD = 8  # absolute flow value
    SLOPE_THRESHOLD = 10  # absolute flow slope
    MIN_TAIL_LENGTH = 12  # samples
    GRACE_LENGTH = 5  # samples

    def __init__(self, dp_driver):
        self.dp_driver = dp_driver

        self.samples = []
        self.timestamps = []
        self.tail_indices = []
        self.candidate_indices = []

        self.grace_count = 0

    def add_sample(self, sample, timestamp):
        self.samples.append(sample)
        self.timestamps.append(timestamp)

    def check_close_up(self, current_index, in_grace=False):
        if len(self.samples) > 0 and (self. grace_count >= self.GRACE_LENGTH or
                                      current_index == len(self.samples) - 1):
            tail = self.candidate_indices[:-self.grace_count]
            if len(tail) >= self.MIN_TAIL_LENGTH:
                self.tail_indices += tail[int(len(tail) * 3 / 4):]

            self.grace_count = 0
            self.candidate_indices = []

        elif in_grace:
            self.grace_count += 1

    def process(self):
        for index in range(1, len(self.samples)):
            slope = ((self.samples[index] - self.samples[index - 1]) /
                     (self.timestamps[index] - self.timestamps[index - 1]))
            if abs(self.samples[index]) >= self.TAIL_THRESHOLD:
                self.check_close_up(index)

            elif abs(slope) < self.SLOPE_THRESHOLD:
                self.candidate_indices.append(index)
                self.grace_count = 0

            else:
                self.candidate_indices.append(index)
                self.check_close_up(index, in_grace=True)

        indices = np.array(self.tail_indices)
        if len(indices) == 0:
            return None

        if len(self.tail_indices) < self.MIN_TAIL_LENGTH:
            return None

        dp = np.array([self.dp_driver.flow_to_pressure(f) +
                       self.dp_driver.get_calibration_offset()
                       for f in self.samples])

        tails_dp = dp[indices]
        return np.average(tails_dp)
