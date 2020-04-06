from queue import Queue

from data.alert import Alert, AlertCodes
from data.history import AlertsHistory
from data.observable import Observable


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
        self.history.on_clear_alerts()

        self.last_alert = Alert(AlertCodes.OK)
        self.observable.publish(self.last_alert)