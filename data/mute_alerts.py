import time

from data.observable import Observable


class MuteAlerts(object):
    def __init__(self):
        self.observable = Observable()
        self._alerts_muted = False
        self.mute_time = None

    def mute_alerts(self, value=None):
        if value is not None:
            self._alerts_muted = value
        else:
            self._alerts_muted = not self._alerts_muted

        if self._alerts_muted:
            self.mute_time = time.time()

        self.observable.publish(self._alerts_muted)