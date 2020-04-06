import time
import datetime
from collections import deque
from enum import IntEnum
from queue import Queue
from functools import lru_cache
from data.observable import Observable


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
    OXYGEN_SENSOR_ERROR = 1 << 10
    OXYGEN_LOW = 1 << 11
    OXYGEN_HIGH = 1 << 12
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
        AlertCodes.OXYGEN_SENSOR_ERROR: "Oxygen Sensor Error",
        AlertCodes.NO_BATTERY: "No Battery",
    }

    def __init__(self, alert_code, timestamp=None):  # TODO: Add 'Seen'
        self.code = alert_code
        if timestamp is None:
            self.timestamp = time.time()  # TODO: Remove

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


class AlertsHistory(object):  # TODO: Move to own file
    MAXIMUM_HISTORY_COUNT = 40
    TIME_DIFFERENCE_BETWEEN_SAME_ALERTS = 60 * 15  # 15 Minutes

    def __init__(self):
        self.stack = deque(maxlen=40)
        self.observable = Observable()

    def __len__(self):
        return len(self.stack)

    def copy(self):
        instance = AlertsHistory()
        instance.stack = self.stack.copy()
        return instance

    def append_to_history(self, alert: Alert):
        """
        We append an alert to the history in any one of the following cases:
            * The alert history is empty
            * The last alert is different from this one
            * The last alert is the same as this one, but some time has passed since
        """
        if alert == AlertCodes.OK:
            return  # TODO: Figure out

        if len(self.stack) == 0:
            # The history is empty, we definitely want it in the queue
            self.insert_to_stack(alert)
            return

        last_alert = self.stack[0]
        same_as_last_alert = last_alert == alert

        # This is a new alert, we definitely want it in the history
        if not same_as_last_alert:
            # TODO: Spam-filter logic should go here,
            # Consider this case: LOW-PRESSURE | HIGH-PRESSURE | LOW-PRESSURE repeatedly
            self.insert_to_stack(alert)
            return

        # This is the same alert as the last one, but enough time has passed since,
        # We want it in the history, because it's a new event.
        time_passed_since = alert.timestamp - last_alert.timestamp
        if time_passed_since >= self.TIME_DIFFERENCE_BETWEEN_SAME_ALERTS:
            self.insert_to_stack(alert)

    def insert_to_stack(self, alert):
        self.observable.publish(alert)
        self.stack.appendleft(alert)

    def get(self, start, amount):
        return list(self.stack)[start:start+amount]


class AlertsQueue(object):
    MAXIMUM_ALERTS_AMOUNT = 2

    def __init__(self):
        self.queue = Queue(maxsize=self.MAXIMUM_ALERTS_AMOUNT)
        self.last_alert = Alert(AlertCodes.OK)
        self.history = AlertsHistory()
        self.observable = Observable()

    def __len__(self):
        return self.queue.qsize()

    def enqueue_alert(self, alert, timestamp):
        if not isinstance(alert, Alert):
            alert = Alert(alert, timestamp)

        self.history.append_to_history(alert)

        if self.queue.qsize() == self.MAXIMUM_ALERTS_AMOUNT:
            self.dequeue_alert()

        self.last_alert = alert

        self.observable.publish(self.last_alert)
        self.queue.put(alert)

    def dequeue_alert(self):
        alert = self.queue.get()
        self.last_alert = self.queue.queue[0]

        self.observable.publish(self.last_alert)
        return alert

    def clear_alerts(self):
        # Note that emptying a queue is not thread-safe
        self.queue.queue.clear()

        self.last_alert = Alert(AlertCodes.OK)
        self.observable.publish(self.last_alert)


class MuteAlerts(object):
    def __init__(self):
        self.observable = Observable()
        self._alerts_muted = False
        self.mute_time = None

    def mute_alerts(self, value=None):
        if value is not None:
            self._alerts_muted = value
        else:
            self._alerts_muted = not self._alerts_muted

        if self._alerts_muted:
            self.mute_time = time.time()

        self.observable.publish(self._alerts_muted)
