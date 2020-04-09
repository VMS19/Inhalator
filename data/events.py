import logging

from data.mute_controller import MuteController
from data.alert_queue import AlertQueue

log = logging.getLogger(__name__)


class Events(object):
    def __init__(self):
        self.alert_queue = AlertQueue()
        self.mute_controller = MuteController()
