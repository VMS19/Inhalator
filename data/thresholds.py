class Range(object):
    NAME = NotImplemented
    UNIT = NotImplemented
    MINIMAL_VALUE = 0

    def __init__(self, min=None, max=None, step=0.5):
        self.min = min
        self.max = max
        self.step = step
        self.temporary_min = min
        self.temporary_max = max

    def __setattr__(self, key, value):
        # We want to limit the precision of thresholds to 3 after the dot
        if key in ("min", "max") and value is not None:
            self.__dict__[key] = float("{:.3f}".format(value))
        else:
            self.__dict__[key] = value

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
        if self.temporary_min + self.step <= self.temporary_max:
            self.temporary_min += self.step

    def increase_max(self):
        self.temporary_max += self.step

    def decrease_min(self):
        self.temporary_min -= self.step

    def decrease_max(self):
        if self.temporary_max - self.step >= self.temporary_min:
            self.temporary_max -= self.step

    def confirm(self):
        self.max = self.temporary_max
        self.min = self.temporary_min

    def cancel(self):
        self.temporary_max = self.max
        self.temporary_min = self.min


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
