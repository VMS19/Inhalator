from pydantic.dataclasses import dataclass


@dataclass
class Range:
    NAME = NotImplemented
    UNIT = NotImplemented

    min: float = None
    max: float = None
    step: float = 0.5

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
    UNIT = "inH2o"


class RespiratoryRateRange(Range):
    NAME = "Rate"
    UNIT = "BPM"
