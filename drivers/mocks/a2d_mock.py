import logging

log = logging.getLogger(__name__)


class MockA2D(object):
    def __init__(self, oxygen=21, battery_percentage=94, battery_existence=True):
        self.oxygen = oxygen
        self.battery_percentage = battery_percentage
        self.battery_existence = battery_existence

    def read_oxygen(self):
        return self.oxygen

    def read_battery_percentage(self):
        return self.battery_percentage

    def read_battery_existence(self):
        return self.battery_existence
