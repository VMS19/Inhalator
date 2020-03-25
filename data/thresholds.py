class Threshold(object):
    UNIT = NotImplemented

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __setattr__(self, key, value):
        # We want to limit the precision of thresholds to 3 after the dot
        if key == "value":
            self.__dict__["value"] = float("{:.3f}".format(value))

        else:
            self.__dict__[key] = value

    def __repr__(self):
        return "{}={:.2f}({})".format(self.name, self.value, self.UNIT)


class PressureThreshold(Threshold):
    UNIT = "cmH2O"


class AirFlowThreshold(Threshold):
    UNIT = "lpm"


class NewThreshold(object):
    NAME = NotImplemented
    UNIT = NotImplemented
    OFF = "off"

    def __init__(self, min, max):
        self.min = min
        self.max = max

    def __setattr__(self, key, value):
        # We want to limit the precision of thresholds to 3 after the dot
        if key in ("min", "max") and value != self.OFF:
            self.__dict__[key] = float("{:.3f}".format(value))

        else:
            self.__dict__[key] = value


class VtiThreshold(NewThreshold):
    NAME = "Vti"
    UNIT = "mL"


class MViThreshold(NewThreshold):
    NAME = "MVi"
    UNIT = "L/min"


class PresThreshold(NewThreshold):
    NAME = "Pressure"
    UNIT = "cmH2O"

class RespiratoryRateThreshold(NewThreshold):
    NAME = "Resp. rate"
    UNIT = "per min"
