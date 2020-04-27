import time
import datetime
from collections import deque
from enum import IntEnum
from queue import Queue

from uptime import uptime

from data.observable import Observable
from data.configurations import ConfigurationManager


class AlertCodes(IntEnum):
    OK = 0

    # medical alerts
    PRESSURE_LOW = 1 << 0
    PRESSURE_HIGH = 1 << 1
    VOLUME_LOW = 1 << 2
    VOLUME_HIGH = 1 << 3
    PEEP_TOO_HIGH = 1 << 4
    PEEP_TOO_LOW = 1 << 5
    BPM_LOW = 1 << 6
    BPM_HIGH = 1 << 7
    NO_BREATH = 1 << 8
    OXYGEN_LOW = 1 << 9
    OXYGEN_HIGH = 1 << 10
    # WARNING - You're adding something? look below at is_medical_condition

    # system alerts
    INVALID_CONFIGURATION_FILE = 1 << 11
    FLOW_SENSOR_ERROR = 1 << 12
    PRESSURE_SENSOR_ERROR = 1 << 13
    OXYGEN_SENSOR_ERROR = 1 << 14
    NO_BATTERY = 1 << 15

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
        AlertCodes.INVALID_CONFIGURATION_FILE: "Configuration Error",
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

    def __hash__(self):
        return hash(self.code)

    def is_medical_condition(self):
        return 0 < self.code <= 1 << 10

    def is_system_alert(self):
        return 1 << 10 < self.code

    def __repr__(self):
        return f"Alert(code={self.code}, message={str(self)})"

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
        # We need `active_alerts` for the telemetry feature. Without it there is
        # no way to get the active alerts in the system, since Queue is not
        # iterable and cannot be converted to a list without emptying it.
        # I intentionally DID NOT change the current workings of AlertsQueue,
        # in order to avoid changing critical parts of the system in such a
        # late stage.
        # TODO: For v2.0 maybe, replace self.queue with a proper data structure
        #  such as `deque` and call it `active_alerts`.
        self.active_alerts = deque(maxlen=self.MAXIMUM_HISTORY_COUNT)
        self.active_alert_set = set()  # Keeps track for duplicates.
        self.last_alert = Alert(AlertCodes.OK)
        self.observer = Observable()
        self.initial_uptime = uptime()

    def __len__(self):
        return len(self.active_alerts)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"AlertQueue({str(self.active_alerts)})"

    def enqueue_alert(self, alert, timestamp=None):
        if not isinstance(alert, Alert):
            alert = Alert(alert, timestamp)

        grace_time = ConfigurationManager.config().boot_alert_grace_time
        grace_time_end = self.initial_uptime + grace_time
        if alert.is_medical_condition() and uptime() < grace_time_end:
            return

        if self.queue.qsize() == self.MAXIMUM_ALERTS_AMOUNT:
            self.dequeue_alert()

        self.last_alert = alert

        self.observer.publish(self.last_alert)
        self.queue.put(alert)
        if alert not in self.active_alert_set:
            self.active_alerts.append(alert)
            self.active_alert_set.add(alert)

    def dequeue_alert(self):
        alert = self.queue.get()
        self.last_alert = self.queue.queue[0]

        self.observer.publish(self.last_alert)
        return alert

    def clear_alerts(self):
        # Note that emptying a queue is not thread-safe
        self.queue.queue.clear()
        self.active_alerts.clear()
        self.active_alert_set.clear()

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
