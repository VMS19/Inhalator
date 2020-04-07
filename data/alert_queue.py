from collections import deque

from data.alert import Alert, AlertCodes
from data.history import AlertsHistory
from data.observable import Observable


class AlertQueue(object):
    MAXIMUM_ALERTS_AMOUNT = 2

    def __init__(self):
        self.queue = deque(maxlen=self.MAXIMUM_ALERTS_AMOUNT)
        self.last_alert = Alert(AlertCodes.OK)
        self.history = AlertsHistory()
        self.observable = Observable()

    def __len__(self):
        return len(self.queue)

    def __iter__(self):
        return iter(self.queue)

    def enqueue_alert(self, alert, timestamp):
        if not isinstance(alert, Alert):
            alert = Alert(alert, timestamp)

        self.last_alert = alert
        self.queue.append(alert)
        self.history.append_to_history(alert)

        self.observable.publish(self.last_alert)

    def clear_alerts(self):
        # Note that emptying a queue is not thread-safe
        self.queue.clear()
        self.history.on_clear_alerts()

        self.last_alert = Alert(AlertCodes.OK)
        self.observable.publish(self.last_alert)
