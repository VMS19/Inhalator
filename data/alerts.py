import time
import datetime
from collections import deque
from enum import IntEnum
from queue import Queue
from functools import lru_cache


class AlertCodes(IntEnum):
    OK = 0
    PRESSURE_LOW = 1 << 0
    PRESSURE_HIGH = 1 << 1
    VOLUME_LOW = 1 << 2
    VOLUME_HIGH = 1 << 3
    PEEP_TOO_HIGH = 1 << 4
    PEEP_TOO_LOW = 1 << 5
    NO_BREATH = 1 << 6
    NO_CONFIGURATION_FILE = 1 << 7
    FLOW_SENSOR_ERROR = 1 << 8
    PRESSURE_SENSOR_ERROR = 1 << 9
    SATURATION_SENSOR_ERROR = 1 << 10
    OXYGEN_LOW = 1 << 11
    OXYGEN_HIGH = 1 << 12
    LOW_BATTERY = 1 << 13
    NO_BATTERY = 1 << 14

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
        AlertCodes.OXYGEN_HIGH: "Oxygen Too High",
        AlertCodes.OXYGEN_LOW: "Oxygen Too Low",
        AlertCodes.NO_CONFIGURATION_FILE: "Configuration Error",
        AlertCodes.FLOW_SENSOR_ERROR: "Flow Sensor Error",
        AlertCodes.PRESSURE_SENSOR_ERROR: "Pressure Sensor Error",
        AlertCodes.SATURATION_SENSOR_ERROR: "Saturation Sensor Error",
        AlertCodes.NO_BATTERY: "No Battery",
        AlertCodes.LOW_BATTERY: "Low Battery",
    }

    def __init__(self, alert_code, timestamp=None):
        self.code = alert_code
        if timestamp is None:
            self.timestamp = time.time()

        else:
            self.timestamp = timestamp

    def __eq__(self, other):
        return self.code == other

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
        self._subscribers = {}

    def __len__(self):
        return self.queue.qsize()

    def enqueue_alert(self, alert, timestamp=None):
        if not isinstance(alert, Alert):
            alert = Alert(alert, timestamp)

        if self.queue.qsize() == self.MAXIMUM_ALERTS_AMOUNT:
            self.dequeue_alert()

        self.last_alert = alert

        self.publish()
        self.queue.put(alert)

    def dequeue_alert(self):
        alert = self.queue.get()
        self.last_alert = self.queue.queue[0]

        self.publish()
        return alert

    def clear_alerts(self):
        # Note that emptying a queue is not thread-safe
        self.queue.queue.clear()

        self.last_alert = Alert(AlertCodes.OK)
        self.publish()

    def subscribe(self, object, callback):
        self._subscribers[object] = callback

    def unsubscribe(self, object):
        del self._subscribers[object]

    def publish(self):
        for callback in self._subscribers.values():
            callback(self.last_alert)
