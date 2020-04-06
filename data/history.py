from collections import deque

from data.alert import Alert
from data.observable import Observable


class AlertsHistory(object):
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

    def on_clear_alerts(self):
        # Mark all history alerts as 'seen'
        for unseen_alert in self.stack:
            unseen_alert.mark_as_seen()