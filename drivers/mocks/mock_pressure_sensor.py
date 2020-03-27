import itertools

from drivers.mocks import pig


class MockPressureSensor(object):

    def __init__(self):
        self.values = itertools.cycle(pig.file_sampling_generator('pressure'))

    def read_pressure(self):
        value = next(self.values)
        return value
