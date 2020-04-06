import platform

# Tkinter stuff
from data.alerts import AlertCodes
from graphics.alerts_history.bottom_bar import BottomBar
from graphics.alerts_history.entries.container import EntriesContainer
from graphics.alerts_history.scroll_up_down import ScrollUpDownContainer
from graphics.alerts_history.titles import AlertTitles

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from graphics.themes import Theme


class HistoryScreen(object):

    def __init__(self, root, events):
        self.root = root
        self.events = events

        self.alerts_history_screen = Frame(master=self.root, bg=Theme.active().BACKGROUND)
        self.titles = AlertTitles(self.alerts_history_screen)
        self.bottom_bar = BottomBar(self, self.alerts_history_screen)
        self.entries_container = EntriesContainer(self.alerts_history_screen, events)
        self.scroll_up_down_container = ScrollUpDownContainer(self, self.alerts_history_screen)

        self.events.alerts_queue.observable.subscribe(self, self.on_new_alert)

    def on_new_alert(self, alert):
        if alert == AlertCodes.OK:
            self.entries_container.on_clear_alerts()

        else:
            self.entries_container.on_new_alert()

    def on_scroll_up(self):
        self.entries_container.on_scroll_up()

    def on_scroll_down(self):
        self.entries_container.on_scroll_down()

    def on_back_button_click(self):
        self.hide()

    def show(self):
        self.alerts_history_screen.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)
        self.titles.render()
        self.bottom_bar.render()
        self.entries_container.render()
        self.scroll_up_down_container.render()

    def hide(self):
        self.alerts_history_screen.place_forget()
        self.events.alerts_queue.observable.unsubscribe(self)