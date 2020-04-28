from math import copysign
from itertools import cycle
from numpy import random
from itertools import tee


class MockSensor(object):
    """
    Mock sensor class. On each read returns a sample from a pre-configured
    sequence. The sequence is replayed indefinitely.
    """

    def __init__(self, seq, error_probability=0):
        self.data, self.seq = tee(seq)
        self.data = cycle(self.data)
        self._calibration_offset = 0
        self.error_probability = error_probability
        self.offset_drift = 0

    def random_error(self):
        exe = random.choice([ValueError, OSError, TimeoutError, ZeroDivisionError])
        return exe(f"{self.__class__.__name__} failed to read")

    def read(self, *args, **kwargs):
        # We read the sample from the data before raising the exception so that
        # IF an exception will be raise - that sample will be lost.
        sample = next(self.data) + self.offset_drift

        if random.random() < self.error_probability:
            raise self.random_error()

        return sample

    def set_offset_drift(self, offset):
        self.offset_drift = offset


class DifferentialPressureMockSensor(MockSensor):
    def __init__(self, seq, error_probability=0):
        super().__init__(seq, error_probability)
        self._calibration_offset = 0

    def set_calibration_offset(self, offset):
        self._calibration_offset = offset

    def get_calibration_offset(self):
        return self._calibration_offset

    def read_differential_pressure(self):
        sample = super().read()
        return self.flow_to_pressure(sample) - self._calibration_offset

    def read(self, *args, **kwargs):
        sample = super().read(*args, **kwargs)

        return self.pressure_to_flow(self.flow_to_pressure(sample) -
                                     self._calibration_offset)

    def pressure_to_flow(self, pressure):
        return copysign(abs(pressure) ** 0.5, pressure)

    def flow_to_pressure(self, flow):
        return copysign(flow ** 2, flow)
