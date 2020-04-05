class Observable(object):
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, object, callback):
        self._subscribers[object] = callback

    def unsubscribe(self, object):
        del self._subscribers[object]

    def publish(self, value):
        for callback in self._subscribers.values():
            callback(value)
