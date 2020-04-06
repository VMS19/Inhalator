class Range(object):
    NAME = NotImplemented
    UNIT = NotImplemented
    MINIMAL_VALUE = 0

    def __init__(self, min=None, max=None, step=0.5):
        self.min = min
        self.max = max
        self.step = step

    def __setattr__(self, key, value):
        # We want to limit the precision of thresholds to 3 after the dot
        if key in ("min", "max") and value is not None:
            self.__dict__[key] = float("{:.3f}".format(value))
        else:
            self.__dict__[key] = value

    def copy(self):
        return self.__class__(self.min, self.max)

    def below(self, value):
        """
        Test is a value is below the range.
        :param value: The value to test.
        :return: True is a minimum threshold is set, and the tested value is
            below that. False otherwise.
        """
        return self.min is not None and value < self.min

    def over(self, value):
        """
        Test is a value is over the range.
        :param value: The value to test.
        :return: True is a maximum threshold is set, and the tested value is
            over that. False otherwise.
        """
        return self.max is not None and value > self.max

    def load_from(self, other):
        self.min = other.min
        self.max = other.max

    def increase_min(self):
        if self.min + self.step <= self.max:
            self.min += self.step

    def increase_max(self):
        self.max += self.step

    def decrease_min(self):
        self.min -= self.step

    def decrease_max(self):
        if self.max - self.step >= self.min:
            self.max -= self.step


class O2Range(Range):
    NAME = "O2"
    UNIT = "%"


class VolumeRange(Range):
    NAME = "Volume"
    UNIT = "mL"


class PressureRange(Range):
    NAME = "Pressure"
    UNIT = "cmH2O"


class RespiratoryRateRange(Range):
    NAME = "Rate"
    UNIT = "per min"
