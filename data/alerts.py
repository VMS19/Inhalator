from queue import Queue

class AlertCodes(object):
    OK = 0
    PRESSURE_LOW = 1
    PRESSURE_HIGH = 2
    BREATHING_VOLUME_LOW = 4
    BREATHING_VOLUME_HIGH = 8


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

    def __len__(self):
        return self.queue.qsize()

    def enqueue_alert(self, alert):
        if self.queue.qsize() == self.MAXIMUM_ALERTS_AMOUNT:
            self.dequeue_alert()

        # with self.queue.mutex:
        self.last_alert = alert

        self.queue.put(alert)

    def dequeue_alert(self):
        alert = self.queue.get()
        # with self.queue.mutex:
        self.last_alert = self.queue.queue[0]

        return alert

    def clear_alerts(self):
        # Note that emptying a queue is not thread-safe hence the mutex lock
        # with self.queue.mutex:
        self.queue.queue.clear()

        self.last_alert = Alert(AlertCodes.OK)
