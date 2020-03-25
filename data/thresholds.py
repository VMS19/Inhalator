class NewThreshold(object):  # TODO: Rename
    NAME = NotImplemented
    UNIT = NotImplemented
    MINIMAL_VALUE = 0
    OFF = "off"

    def __init__(self, min=OFF, max=OFF, step=0.5):
        self.min = min
        self.max = max
        self.step = step

    def __setattr__(self, key, value):
        # We want to limit the precision of thresholds to 3 after the dot
        if key in ("min", "max") and value != self.OFF:
            self.__dict__[key] = float("{:.3f}".format(value))

        else:
            self.__dict__[key] = value

    def copy(self):
        return self.__class__(self.min, self.max)

    def load_from(self, threshold):
        self.min = threshold.min
        self.max = threshold.max

    def increase_min(self):
        if self.min == self.OFF:
            self.min = self.MINIMAL_VALUE

        else:
            self.min += self.step

    def increase_max(self):
        if self.max == self.OFF:
            self.max = self.MINIMAL_VALUE

        else:
            self.max += self.step

    def decrease_min(self):
        if self.min == self.OFF:
            return

        if self.min == self.MINIMAL_VALUE:
            self.min = self.OFF

        else:
            self.min -= self.step

    def decrease_max(self):
        if self.max == self.OFF:
            return

        if self.max == self.MINIMAL_VALUE:
            self.max = self.OFF

        else:
            self.max -= self.step



class VtiThreshold(NewThreshold):
    NAME = "Vti"
    UNIT = "mL"


class MViThreshold(NewThreshold):
    NAME = "MVi"
    UNIT = "L/min"


class PresThreshold(NewThreshold):  # TODO: Rename to pressure
    NAME = "Pressure"
    UNIT = "cmH2O"

class RespiratoryRateThreshold(NewThreshold):
    NAME = "Resp. rate"
    UNIT = "per min"
