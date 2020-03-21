from math import sin

class MockSfm3200(object):
    sample_interval = 0.1

    def __init__(self):
        self.sample_x = 0
        pass

    def read_flow_slm(self, retries=2):
        value = sin(self.sample_x)
        if value < 0:
            value = 0

        self.sample_x += 1

        return value

    def soft_reset(self):
        pass