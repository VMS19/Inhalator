import logging

from data.alerts import AlertsQueue, MuteAlerts

log = logging.getLogger(__name__)


class Events(object):
    def __init__(self):
        self.alerts_queue = AlertsQueue()
        self.mute_alerts = MuteAlerts()
