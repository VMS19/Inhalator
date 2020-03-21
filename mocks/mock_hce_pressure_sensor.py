from math import sin


class MockHcePressureSensor(object):
    sample_interval = 0.1

    def __init__(self):
        self.sample_x = 0
        pass

    def read_pressure(self):
        value = sin(self.sample_x) * 10
        if value < 0:
            value = 0

        self.sample_x += 1

        return value + 3
