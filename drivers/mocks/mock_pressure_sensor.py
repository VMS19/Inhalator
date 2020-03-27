from itertools import cycle

from drivers.mocks.sinus import sinus, add_noise, truncate


class MockPressureSensor(object):
    SAMPLE_RATE_HZ = 50  # 20ms between reads assumed
    AMPLITUDE = 25
    PIP = 25  # Peak Intake Pressure
    PEEP = 3  # baseline pressure

    def __init__(self, bpm, noise_sigma):
        samples = sinus(
            sample_rate=self.SAMPLE_RATE_HZ,
            amplitude=self.AMPLITUDE,
            freq=bpm / 60.0)

        # upper limit is `PIP - PEEP` and not simply PIP because we will raise
        # the entire signal by PEEP later
        samples = truncate(samples, lower_limit=0, upper_limit=self.PIP - self.PEEP)

        # # Raise by PEEP so it will be the baseline
        samples = [s + self.PEEP for s in samples]
        #
        # # Add some noise
        samples = add_noise(samples, noise_sigma)
        self.samples = cycle(samples)

    def read_pressure(self):
        return next(self.samples)
