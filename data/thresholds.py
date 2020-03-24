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
        return "{}={:.2f}{}".format(self.name, self.value, self.UNIT)


class PressureThreshold(Threshold):
    UNIT = "bar"


class AirFlowThreshold(Threshold):
    UNIT = "ltr"
