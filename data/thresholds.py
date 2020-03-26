class Threshold(object):  # TODO: Add option to turn off
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
        self.min += self.step

    def increase_max(self):
        self.max += self.step

    def decrease_min(self):
        self.min -= self.step

    def decrease_max(self):
        self.max -= self.step



class FlowThreshold(Threshold):
    NAME = "Flow"
    UNIT = "L/min"


class VolumeThreshold(Threshold):
    NAME = "Volume"
    UNIT = "mL"


class PressureThreshold(Threshold):
    NAME = "Pressure"
    UNIT = "cmH2O"

class RespiratoryRateThreshold(Threshold):
    NAME = "Resp. rate"
    UNIT = "per min"
