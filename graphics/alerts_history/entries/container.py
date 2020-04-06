from collections import deque
from tkinter import Frame

from cached_property import cached_property

from data.history import AlertsHistory
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
        self.alerts_displayed = [None] * self.NUMBER_OF_ALERTS_ON_SCREEN
        self.history_snapshot = self.events.alerts_queue.history.copy()

    def load(self):
        latest = self.history_snapshot.get(start=self.index, amount=self.NUMBER_OF_ALERTS_ON_SCREEN)
        for index, alert in enumerate(latest):
            self.alerts_displayed[index] = alert

            entry = self.factory.render_if_absent(index)
            entry.set_alert(alert, index + self.index + 1)

    def on_scroll_up(self):
        if self.index == 0:
            return

        self.index -= 1

        self.load()

    def on_scroll_down(self):
        # We have reached the bottom of the history
        if self.index + self.NUMBER_OF_ALERTS_ON_SCREEN >= len(self.history_snapshot):
            return

        self.index += 1

        self.load()

    def on_refresh(self):
        self.index = 0
        self.history_snapshot = self.events.alerts_queue.history.copy()
        self.load()

    def render(self):
        self.frame.place(relx=0, rely=0.15, relwidth=0.85, relheight=0.7)
        self.load()
