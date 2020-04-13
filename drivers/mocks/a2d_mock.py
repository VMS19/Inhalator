import logging

from errors import InvalidCalibrationError
log = logging.getLogger(__name__)


class MockA2D(object):
    def __init__(self, oxygen=21, battery_percentage=94, battery_existence=True):
        self.oxygen = oxygen
        self.battery_percentage = battery_percentage
        self.battery_existence = battery_existence

    def read_oxygen(self):
        return self.oxygen

    #def set_oxygen_calibration(self, p1, p2):
    #    pass
    def set_oxygen_calibration(self, point1, point2):
        if point1["x"] > point2["x"]:
            left_p = point2
            right_p = point1
        elif point1["x"] < point2["x"]:
            left_p = point1
            right_p = point2
        else:
            raise InvalidCalibrationError(
                "Bad oxygen calibration.\n"
                "Two calibration points on same x value")

        new_scale = (right_p["y"] - left_p["y"]) / (
            right_p["x"] - left_p["x"])

        if new_scale <= 0:
            raise InvalidCalibrationError(
                f"Bad oxygen calibration.\nnegative slope."
                f"({left_p['x']}%,{left_p['y']}V),"
                f"({right_p['x']}%,{right_p['y']}V)")

        new_offset = point1["y"] - point1["x"] * new_scale

        self._oxygen_calibration_scale = new_scale
        self._oxygen_calibration_offset = new_offset

    def read_oxygen_raw(self):
        return 2

    def convert_voltage_to_oxygen(self, voltage):
        return 101

    def read_battery_percentage(self):
        return self.battery_percentage

    def read_battery_existence(self):
        return self.battery_existence
