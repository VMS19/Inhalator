import logging

log = logging.getLogger(__name__)


class MockA2D(object):
    def __init__(self, oxygen=21, battery_percentage=94, battery_existence=True):
        self.oxygen = oxygen
        self.battery_percentage = battery_percentage
        self.battery_existence = battery_existence

    def read_oxygen(self):
        return self.oxygen

    def set_oxygen_calibration(self, p1, p2):
        pass

    def read_oxygen_raw(self):
        return 1

    def convert_voltage_to_oxygen(self, voltage):
        return 101

    def read_battery_percentage(self):
        return self.battery_percentage

    def read_battery_existence(self):
        return self.battery_existence
