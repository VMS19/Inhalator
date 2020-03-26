from math import sin


class MockPressureSensor(object):
    sample_interval = 0.03
    PEEP = 3  # baseline pressure

    def __init__(self):
        self.sample_x = 0
        pass

    def read_pressure(self):
        value = max(0, sin(self.sample_x) * 15)
        self.sample_x += self.sample_interval
        return value + self.PEEP
