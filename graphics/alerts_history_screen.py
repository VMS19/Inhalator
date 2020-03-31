import os
import platform

from cached_property import cached_property

# Tkinter stuff
from data.alerts import Alert, AlertCodes
from data.configurations import Configurations

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from graphics.imagebutton import ImageButton
from graphics.themes import Theme

THIS_FILE = __file__
THIS_DIRECTORY = os.path.dirname(THIS_FILE)
RESOURCES_DIRECTORY = os.path.join(os.path.dirname(THIS_DIRECTORY), "resources")


class AlertTitles(object):
    def __init__(self, root):
        self.root = root
        self.frame = Frame(master=self.root)
        self.time_label = Label(master=self.frame,
                                text="Date",
                                font=("Roboto", 20),
                                bg=Theme.active().BACKGROUND,
                                fg=Theme.active().TXT_ON_BG)

        self.description_label = Label(master=self.frame,
                                       text="Description",
                                       font=("Roboto", 20),
                                       bg=Theme.active().BACKGROUND,
                                       fg=Theme.active().TXT_ON_BG)

    def render(self):
        self.frame.place(relx=0, rely=0, relwidth=0.85, relheight=0.15)

        self.time_label.place(relx=0, rely=0, relheight=1, relwidth=0.3)
        self.description_label.place(relx=0.3, rely=0, relheight=1, relwidth=0.7)


class BottomBar(object):
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root
        self.frame = Frame(master=self.root, bg=Theme.active().BACKGROUND)
        self.back_btn = Button(master=self.frame,
                               bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
                               text="Back",
                               font=("Roboto", 20),
                               command=self.on_click,
                               fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
                               activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
                               activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE)

    def on_click(self):
        self.parent.on_back_button_click()

    def render(self):
        self.frame.place(relx=0, rely=0.85, relwidth=0.85, relheight=0.15)
        self.back_btn.place(relx=0.25, rely=0.1, relheight=0.8, relwidth=0.5)


class EntriesContainer(object):
    def __init__(self, root, total_alerts_in_screen):
        self.root = root
        self.total_alerts_in_screen = total_alerts_in_screen

        self.frame = Frame(master=self.root, bg=Theme.active().BACKGROUND)
        self.entries = []

    def set_entries(self, alerts):
        self.entries = [AlertEntry(self.frame, alert, index, self.total_alerts_in_screen)
                        for index, alert in enumerate(alerts)]
        self.render()

    def render(self):
        self.frame.place(relx=0, rely=0.15, relwidth=0.85, relheight=0.7)

        for entry in self.entries:
            entry.render()

class ScrollUpDownContainer(object):

    DOWN_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_less_white_36dp.png")
    UP_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_more_white_36dp.png")

    def __init__(self, parent, root):
        self.root = root
        self.parent = parent
        self.frame = Frame(master=self.root, bg=Theme.active().BACKGROUND)

        self.up_button = ImageButton(master=self.frame,
                                     image_path=self.UP_IMAGE_PATH,
                                     compound="center",
                                     command=self.parent.on_scroll_up,
                                     bg=Theme.active().BUTTON,
                                     activebackground=Theme.active().BUTTON_ACTIVE)

        self.down_button = ImageButton(master=self.frame,
                                       image_path=self.DOWN_IMAGE_PATH,
                                       compound="center",
                                       command=self.parent.on_scroll_down,
                                       bg=Theme.active().BUTTON,
                                       activebackground=Theme.active().BUTTON_ACTIVE)

    def render(self):
        self.frame.place(relx=0.85, rely=0, relwidth=0.15, relheight=1)
        self.up_button.place(relx=0, rely=0, relheight=0.5, relwidth=1)
        self.down_button.place(relx=0, rely=0.5, relheight=0.5, relwidth=1)


class AlertEntry(object):
    def __init__(self, root, alert, index, total_alerts_in_screen):
        self.root = root
        self.alert = alert
        self.index = index
        self.total_alerts_in_screen = total_alerts_in_screen

        self.frame = Frame(master=self.root,
                           highlightbackground="white",
                           highlightcolor="white",
                           highlightthickness=1)

        self.time_label = Label(master=self.frame,
                                text=self.alert.date(),
                                bg=Theme.active().SURFACE,
                                fg=Theme.active().TXT_ON_SURFACE)
        self.description_label = Label(master=self.frame,
                                       text=str(self.alert),
                                       bg=Theme.active().SURFACE,
                                       fg=Theme.active().TXT_ON_SURFACE)

    def render(self):
        relheight = 1 / self.total_alerts_in_screen
        rely = relheight * self.index
        self.frame.place(relwidth=1, relheight=relheight, relx=0, rely=rely)

        self.time_label.place(relx=0, rely=0, relheight=1, relwidth=0.3)
        self.description_label.place(relx=0.3, rely=0, relheight=1, relwidth=0.7)


class AlertsHistoryScreen(object):

    ALERTS_ON_SCREEN = 6

    def __init__(self, root, events):
        self.root = root
        self.events = events

        # State
        self.index = 0

        self.alerts_history_screen = Frame(master=self.root, bg=Theme.active().BACKGROUND)
        self.titles = AlertTitles(self.alerts_history_screen)
        self.bottom_bar = BottomBar(self, self.alerts_history_screen)
        self.entries_container = EntriesContainer(self.alerts_history_screen,
                                                  total_alerts_in_screen=self.ALERTS_ON_SCREEN)
        self.scroll_up_down_container = ScrollUpDownContainer(self, self.alerts_history_screen)

        self.events.alerts_queue.subscribe(self, self.on_new_alert)

    @property
    def alerts(self):
        return self.events.alerts_queue.history()

    def on_new_alert(self, alert):
        self.update_entries()

    def on_scroll_up(self):
        if self.index == 0:
            return

        self.index -= 1
        self.update_entries()


    def on_scroll_down(self):
        if len(self.alerts) - self.index <= self.ALERTS_ON_SCREEN:
            return

        self.index += 1
        self.update_entries()

    def on_back_button_click(self):
        self.hide()

    def update_entries(self):
        """This function assumes that there ARE alerts to be shown.

        Whether we reached the end of our alerts queue is decided by the functions:
            * on_scroll_down()
            * on_scroll_up()
        """
        self.entries_container.set_entries(
            alerts=self.alerts[self.index:self.index + self.ALERTS_ON_SCREEN]
        )


    def show(self):
        self.alerts_history_screen.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)
        self.titles.render()
        self.bottom_bar.render()
        self.entries_container.render()
        self.scroll_up_down_container.render()

        self.update_entries()

    def hide(self):
        self.alerts_history_screen.place_forget()
