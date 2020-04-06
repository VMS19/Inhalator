import logging

from data.mute_alerts import MuteAlerts
from data.alerts_queue import AlertsQueue

log = logging.getLogger(__name__)


class Events(object):
    def __init__(self):
        self.alerts_queue = AlertsQueue()
        self.mute_alerts = MuteAlerts()
