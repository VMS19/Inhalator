from tkinter import Frame

from data.alerts import AlertsHistory
from graphics.alerts_history.entries.entries_factory import EntriesFactory, CacheState
from graphics.alerts_history.entries.entry import AlertEntry
from graphics.themes import Theme


class EntriesContainer(object):
    NUMBER_OF_ALERTS_ON_SCREEN = 6

    def __init__(self, root, events):
        self.root = root
        self.events = events

        self.frame = Frame(master=self.root, bg=Theme.active().BACKGROUND)
        self.factory = EntriesFactory(self.frame, self.NUMBER_OF_ALERTS_ON_SCREEN)

        # State
        self.index = 0

    @property
    def history(self) -> AlertsHistory:
        return self.events.alerts_queue.history

    def load(self):
        for index, alert in enumerate(self.history.latest(self.NUMBER_OF_ALERTS_ON_SCREEN)):
            entry = self.factory.render_if_absent(index)
            entry.set_alert(alert)

    def on_scroll_up(self):
        pass

    def on_scroll_down(self):
        pass

    def on_clear_alerts(self):
        pass

    def on_new_alert(self):
        pass

    def render(self):
        self.frame.place(relx=0, rely=0.15, relwidth=0.85, relheight=0.7)
        self.load()
