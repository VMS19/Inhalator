from math import sin

import numpy as np


def sinus(sample_rate, amplitude, freq):
    full_cycle = 1 / freq
    num_samples = int(sample_rate * full_cycle)
    signal = [amplitude * sin(2 * np.pi * i * freq / sample_rate)
              for i in range(num_samples)]
    return signal


def truncate(signal, lower_limit, upper_limit):
    return [min(upper_limit, max(lower_limit, s)) for s in signal]


def add_noise(signal, sigma):
    return [s + np.random.normal(scale=sigma) for s in signal]
