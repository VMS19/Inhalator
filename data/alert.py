import time
import datetime
from enum import IntEnum


class AlertCodes(IntEnum):
    OK = 0

    # medical alerts
    PRESSURE_LOW = 1
    PRESSURE_HIGH = 2
    VOLUME_LOW = 3
    VOLUME_HIGH = 4
    PEEP_TOO_HIGH = 5
    PEEP_TOO_LOW = 6
    BPM_LOW = 7
    BPM_HIGH = 8
    NO_BREATH = 9
    OXYGEN_LOW = 10
    OXYGEN_HIGH = 11

    # system alerts
    NO_CONFIGURATION_FILE = 101
    FLOW_SENSOR_ERROR = 102
    PRESSURE_SENSOR_ERROR = 103
    OXYGEN_SENSOR_ERROR = 104
    NO_BATTERY = 105

    def __getitem__(self, item):
        return getattr(self, item)

    @classmethod
    def is_valid(cls, alert_code):
        return alert_code in map(int, cls)


class Alert(object):
    ALERT_CODE_TO_MESSAGE = {
        AlertCodes.PRESSURE_LOW: "Low Pressure",
        AlertCodes.PRESSURE_HIGH: "High Pressure",
        AlertCodes.VOLUME_LOW: "Low Volume",
        AlertCodes.VOLUME_HIGH: "High Volume",
        AlertCodes.NO_BREATH: "No Breathing",
        AlertCodes.PEEP_TOO_HIGH: "High PEEP",
        AlertCodes.PEEP_TOO_LOW: "Low PEEP",
        AlertCodes.BPM_HIGH: "High BPM",
        AlertCodes.BPM_LOW: "Low BPM",
        AlertCodes.OXYGEN_HIGH: "Oxygen Too High",
        AlertCodes.OXYGEN_LOW: "Oxygen Too Low",
        AlertCodes.NO_CONFIGURATION_FILE: "Configuration Error",
        AlertCodes.FLOW_SENSOR_ERROR: "Flow Sensor Error",
        AlertCodes.PRESSURE_SENSOR_ERROR: "Pressure Sensor Error",
        AlertCodes.OXYGEN_SENSOR_ERROR: "Oxygen Sensor Error",
        AlertCodes.NO_BATTERY: "No Battery",
    }

    def __init__(self, alert_code, timestamp=None):
        self.code = alert_code
        if timestamp is None:
            self.timestamp = time.time()  # TODO: Remove

        else:
            self.timestamp = timestamp

        self.seen = False

    def __eq__(self, other):
        return self.code == other

    def is_medical_condition(self):
        return 0 < self.code <= 100

    def is_system_alert(self):
        return 100 < self.code

    def __str__(self):
        if self.code in self.ALERT_CODE_TO_MESSAGE:
            return self.ALERT_CODE_TO_MESSAGE[self.code]

        # For each on bit it in the alert code, we want to concatenate the
        # relevant error message
        errors = []
        for code, message in self.ALERT_CODE_TO_MESSAGE.items():
            if self.contains(code):
                errors.append(message)

        return " | ".join(errors)

    def contains(self, code):
        return self.code & code != 0

    def date(self):
        return datetime.datetime.fromtimestamp(self.timestamp).strftime("%A %X")

    def mark_as_seen(self):
        self.seen = True
