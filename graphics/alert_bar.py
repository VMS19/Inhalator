import time
import timeago
import datetime
from tkinter import *

from data.alerts import Alert, AlertCodes
from graphics.themes import Theme
from data import alerts
from data.configurations import Configurations
from graphics.version import __version__


class IndicatorAlertBar(object):
    def __init__(self, parent, events, drivers):
        self.parent = parent
        self.root = parent.element
        self.events = events
        self.configs = Configurations.instance()
        self.drivers = drivers

        self.height = self.parent.height
        self.width = self.parent.width

        self.bar = Frame(self.root, bg=Theme.active().ALERT_BAR_OK,
                         height=self.height, width=self.width)

        self.message_label = Label(master=self.bar,
                                   font=("Roboto", 32),
                                   text="OK",
                                   bg=Theme.active().ALERT_BAR_OK,
                                   fg=Theme.active().ALERT_BAR_OK_TXT,)

        self.timestamp_label = Label(master=self.root, font=("Roboto", 12),
                                     text="",
                                     fg=Theme.active().ALERT_BAR_OK_TXT,
                                     bg=Theme.active().ALERT_BAR_OK)

        self.version_label = Label(master=self.root, font=("Roboto", 12),
                                   text="Ver. {}".format(__version__),
                                   fg=Theme.active().ALERT_BAR_OK_TXT,
                                   bg=Theme.active().ALERT_BAR_OK)

        self.current_alert = Alert(AlertCodes.OK)

    @property
    def element(self):
        return self.bar

    def render(self):
        self.bar.place(relx=0, rely=0)
        self.message_label.place(anchor="nw", relx=0.03, rely=0.05)
        self.timestamp_label.place(anchor="nw", relx=0.04, rely=0.7)
        self.version_label.place(anchor="nw", relx=0.8, rely=0.4)

    def update(self):
        # Check mute time limit
        if (self.events.mute_alerts._alerts_muted and
                (time.time() - self.events.mute_alerts.mute_time) >
                self.configs.mute_time_limit):
            self.events.mute_alerts.mute_alerts(False)
        last_alert_in_queue = self.events.alerts_queue.last_alert

        # If the queue says everything is ok, and the graphics shows
        # otherwise, change the graphics state and update the GUI
        if last_alert_in_queue == AlertCodes.OK:
            if self.current_alert != AlertCodes.OK:
                self.current_alert = Alert(AlertCodes.OK)
                self.set_no_alert()

        # If the queue says there's an issue, and graphics shows
        # everything to be okay, change the graphics state and update the GUI
        else:
            if self.current_alert == AlertCodes.OK:
                self.current_alert = last_alert_in_queue
                self.set_alert(last_alert_in_queue)

        self.update_timestamp_label()

    def set_no_alert(self):
        self.bar.config(bg=Theme.active().ALERT_BAR_OK)
        self.message_label.config(bg=Theme.active().ALERT_BAR_OK,
                                  fg=Theme.active().ALERT_BAR_OK_TXT,
                                  text="OK")
        self.version_label.config(bg=Theme.active().ALERT_BAR_OK,
                                  fg=Theme.active().ALERT_BAR_OK_TXT)
        self.timestamp_label.config(bg=Theme.active().ALERT_BAR_OK,
                                    fg=Theme.active().ALERT_BAR_OK_TXT)
        self.timestamp_label.configure(text="")

    def set_alert(self, alert: Alert):
        self.bar.config(bg=Theme.active().ERROR)
        self.message_label.config(bg=Theme.active().ERROR,
                                  fg=Theme.active().TXT_ON_ERROR, text=str(alert))
        self.version_label.config(bg=Theme.active().ERROR,
                                  fg=Theme.active().TXT_ON_ERROR)
        self.timestamp_label.config(bg=Theme.active().ERROR,
                                    fg=Theme.active().TXT_ON_ERROR)

    def update_timestamp_label(self):
        if self.current_alert == AlertCodes.OK:
            self.timestamp_label.configure(text="")
            return


        # We can't use simple alert.date() or time.time() for this calculation
        # because we want to support both simulation mode and real mode.
        # hence, we look at the differential time since the alert last happened.
        now = self.drivers.acquire_driver("timer").get_time()
        then = self.current_alert.timestamp

        now_dt = datetime.datetime.fromtimestamp(now)
        then_dt = datetime.datetime.fromtimestamp(then)

        # This display a '2 minutes ago' text
        self.timestamp_label.configure(text=f"{(timeago.format(now_dt - then_dt))}")
