from itertools import cycle
from numpy import random


class MockSensor(object):
    """
    Mock sensor class. On each read returns a sample from a pre-configured
    sequence. The sequence is replayed indefinitely.
    """

    def __init__(self, seq, error_probability=0):
        self.data = cycle(seq)
        self.error_probability = error_probability

    def random_error(self):
        exe = random.choice([ValueError, OSError, TimeoutError, ZeroDivisionError])
        return exe(f"{self.__class__.__name__} failed to read")

    def read(self, *args, **kwargs):
        # We read the sample from the data before raising the exception so that
        # IF an exception will be raise - that sample will be lost.
        sample = next(self.data)
        if random.random() < self.error_probability:
            raise self.random_error()
        return sample
