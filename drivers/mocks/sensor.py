from itertools import cycle


class MockSensor(object):
    """
    Mock sensor class. On each read returns a sample from a pre-configured
    sequence. The sequence is replayed indefinitely.
    """

    def __init__(self, seq):
        self.data = cycle(seq)

    def read(self, *args, **kwargs):
        return next(self.data)
