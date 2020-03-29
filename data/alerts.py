from queue import Queue


class AlertCodes(object):
    OK = 0
    PRESSURE_LOW = 1 << 0
    PRESSURE_HIGH = 1 << 1
    VOLUME_LOW = 1 << 2
    VOLUME_HIGH = 1 << 3
    PEEP_TOO_HIGH = 1 << 4
    PEEP_TOO_LOW = 1 << 5


class Alert(object):
    def __init__(self, alert_code, additional_info=None):
        self.code = alert_code
        self.value = additional_info

    def __eq__(self, other):
        return self.code == other


class AlertsQueue(object):
    MAXIMUM_ALERTS_AMOUNT = 2

    def __init__(self):
        self.queue = Queue(maxsize=self.MAXIMUM_ALERTS_AMOUNT)
        self.last_alert = Alert(AlertCodes.OK)
        self._subscribers = {}

    def __len__(self):
        return self.queue.qsize()

    def enqueue_alert(self, alert):
        if self.queue.qsize() == self.MAXIMUM_ALERTS_AMOUNT:
            self.dequeue_alert()

        # with self.queue.mutex:
        self.last_alert = alert

        self.publish()
        self.queue.put(alert)

    def dequeue_alert(self):
        alert = self.queue.get()
        # with self.queue.mutex:
        self.last_alert = self.queue.queue[0]

        self.publish()
        return alert

    def clear_alerts(self):
        # Note that emptying a queue is not thread-safe hence the mutex lock
        # with self.queue.mutex:
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
