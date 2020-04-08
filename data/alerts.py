import time
import datetime
from enum import IntEnum
from queue import Queue
from data.observable import Observable


class AlertCodes(IntEnum):
    MEDICAL_ALERT_OFFSET = 1
    SYSTEM_ALERT_OFFSET = 100
    OK = 0
    PRESSURE_LOW = MEDICAL_ALERT_OFFSET
    PRESSURE_HIGH = MEDICAL_ALERT_OFFSET + 1
    VOLUME_LOW = MEDICAL_ALERT_OFFSET + 2
    VOLUME_HIGH = MEDICAL_ALERT_OFFSET + 3
    PEEP_TOO_HIGH = MEDICAL_ALERT_OFFSET + 4
    PEEP_TOO_LOW = MEDICAL_ALERT_OFFSET + 5
    BPM_LOW = MEDICAL_ALERT_OFFSET + 6
    BPM_HIGH = MEDICAL_ALERT_OFFSET + 7
    NO_BREATH = MEDICAL_ALERT_OFFSET + 8
    NO_CONFIGURATION_FILE = SYSTEM_ALERT_OFFSET
    FLOW_SENSOR_ERROR = SYSTEM_ALERT_OFFSET + 1
    PRESSURE_SENSOR_ERROR = SYSTEM_ALERT_OFFSET + 2
    OXYGEN_SENSOR_ERROR = SYSTEM_ALERT_OFFSET + 3
    OXYGEN_LOW = SYSTEM_ALERT_OFFSET + 4
    OXYGEN_HIGH = SYSTEM_ALERT_OFFSET + 5
    NO_BATTERY = SYSTEM_ALERT_OFFSET + 6

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
            self.timestamp = time.time()

        else:
            self.timestamp = timestamp

    def __eq__(self, other):
        return self.code == other

    def __ge__(self, other):
        return self.code >= other

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


class AlertsQueue(object):
    MAXIMUM_ALERTS_AMOUNT = 2
    MAXIMUM_HISTORY_COUNT = 40
    TIME_DIFFERENCE_BETWEEN_SAME_ALERTS = 60 * 5

    def __init__(self):
        self.queue = Queue(maxsize=self.MAXIMUM_ALERTS_AMOUNT)
        self.last_alert = Alert(AlertCodes.OK)
        self.observer = Observable()

    def __len__(self):
        return self.queue.qsize()

    def enqueue_alert(self, alert, timestamp=None):
        if not isinstance(alert, Alert):
            alert = Alert(alert, timestamp)

        if self.queue.qsize() == self.MAXIMUM_ALERTS_AMOUNT:
            self.dequeue_alert()

        self.last_alert = alert

        self.observer.publish(self.last_alert)
        self.queue.put(alert)

    def dequeue_alert(self):
        alert = self.queue.get()
        self.last_alert = self.queue.queue[0]

        self.observer.publish(self.last_alert)
        return alert

    def clear_alerts(self):
        # Note that emptying a queue is not thread-safe
        self.queue.queue.clear()

        self.last_alert = Alert(AlertCodes.OK)
        self.observer.publish(self.last_alert)


class MuteAlerts(object):

    def __init__(self):
        self.observer = Observable()
        self._alerts_muted = False
        self.mute_time = None

    def mute_alerts(self, value=None):
        if value is not None:
            self._alerts_muted = value
        else:
            self._alerts_muted = not self._alerts_muted

        if self._alerts_muted:
            self.mute_time = time.time()

        self.observer.publish(self._alerts_muted)
