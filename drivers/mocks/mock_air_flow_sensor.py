import itertools

from drivers.mocks import pig


class MockAirFlowSensor(object):

    def __init__(self):
        self.values = itertools.cycle(pig.file_sampling_generator('flow'))

    def read_flow_slm(self, retries=2):
        value = next(self.values)
        return value

    def soft_reset(self):
        pass
