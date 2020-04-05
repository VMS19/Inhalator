import logging

from data.alerts import AlertsQueue, MuteAlerts
import time
from data.publisher_subscriber import PublishSubscriber

log = logging.getLogger(__name__)


class Events(object):
    def __init__(self):
        self.alerts_queue = AlertsQueue()
        self.mute_alerts = MuteAlerts()
