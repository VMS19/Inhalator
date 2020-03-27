from math import sin


class MockAirFlowSensor(object):
    sample_interval = 0.03

    def __init__(self):
        self.sample_x = 0
        pass

    def read_flow_slm(self, retries=2):
        value = max(0, sin(self.sample_x) * 20)
        self.sample_x += self.sample_interval
        return value

    def soft_reset(self):
        pass
