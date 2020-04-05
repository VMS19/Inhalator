import logging

from data.alerts import AlertsQueue
import time
from data.publisher_subscriber import PublishSubscriber

log = logging.getLogger(__name__)


class Events(object):
    def __init__(self):
        self.alerts_queue = AlertsQueue()
        self.mute_alerts = MuteAlerts()

class MuteAlerts(object):

    def __init__(self):
        self.pubsub = PublishSubscriber()
        self._alerts_muted = False
        self.mute_time = None

    def mute_alerts(self, value=None):
        if value is not None:
            self._alerts_muted = value
        else:
            self._alerts_muted = not self._alerts_muted

        self.pubsub.publish(self._alerts_muted)

        if self._alerts_muted:
            self.mute_time = time.time()
