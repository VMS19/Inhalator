from itertools import cycle

from drivers.mocks.sinus import sinus, truncate, add_noise


class MockAirFlowSensor(object):
    SAMPLE_RATE_HZ = 50  # 20ms between reads assumed
    AMPLITUDE = 20

    def __init__(self, bpm, noise_sigma):
        samples = sinus(self.SAMPLE_RATE_HZ, self.AMPLITUDE, bpm / 60)
        samples = truncate(samples, lower_limit=0, upper_limit=self.AMPLITUDE)
        samples = add_noise(samples, noise_sigma)
        self.samples = cycle(samples)

    def read_flow_slm(self, retries=2):
        return next(self.samples)

    def soft_reset(self):
        pass
