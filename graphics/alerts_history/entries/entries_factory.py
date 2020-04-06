from enum import Enum
from typing import List

from graphics.alerts_history.entries.entry import AlertEntry

class CacheState(Enum):
    VISIBLE = 0
    HIDDEN = 1
    NO_ENTRY = 2


class CachedEntry(object):
    def __init__(self, entry, state):
        self.entry = entry
        self.state = state


# noinspection PyTypeChecker
class EntriesFactory(object):
    """This class is basically a Flyweight-Factory for Entries.

    The naive implementation is rendering `Entry` objects and then disposing of them,
    on each time the user opened the History-Screen, and every-time he scrolls.

    This works just fine on our development machines, but when it comes to the
    Raspberry-Pi, the CPU can't handle this much rendering and disposing on every alert.

    Thus, we separate our alert-entries to their extrinsic state and their intrinsic state,
    Their extrinsic state is the actual graphics and their positioning,
    whereas their intrinsic state is the actual Alert that is displayed as text.

    We never dispose of the entries created, we just hide them and recycle
    them whenever needed.

    For further reading about the 'Flyweight' design pattern, See:
    https://en.wikipedia.org/wiki/Flyweight_pattern
    """
    def __init__(self, root, number_of_alerts_on_screen):
        self.root = root
        self.alerts_on_screen = number_of_alerts_on_screen

        # We always start with an empty alerts screen
        self.entries = [CachedEntry(state=CacheState.NO_ENTRY, entry=None)
                        for _ in range(self.alerts_on_screen)]

        self.entries: List[CachedEntry]

    def __len__(self):
        """Return the amount of currently displayed items"""
        return len([entry for entry in self.entries if entry.state == CacheState.VISIBLE])

    def render_if_absent(self, index) -> AlertEntry:
        cached_entry = self.entries[index]
        entry = cached_entry.entry
        state = cached_entry.state

        # First check if we already rendered this entry and it is visible
        if state == CacheState.VISIBLE:
            return entry

        # Entry is hidden, display it, mark it visible, return it
        if state == CacheState.HIDDEN:
            entry.render()
            self.entries[index].state = CacheState.VISIBLE
            return entry

        # Entry wasn't rendered yet, thus we'll have to create it
        entry = AlertEntry(root=self.root,
                           index=index,
                           total_alerts_in_screen=self.alerts_on_screen)

        # Render it, mark it visible, return it
        entry.render()
        self.entries[index].state = CacheState.VISIBLE
        self.entries[index].entry = entry

        return entry

    def dispose(self, index):
        entry, state = self.entries[index]

        if state in (CacheState.HIDDEN, CacheState.NO_ENTRY):
            return

        entry.hide()
        self.entries[index].state = CacheState.HIDDEN
