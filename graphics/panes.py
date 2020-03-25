# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from graphics.alert_bar import IndicatorAlertBar
from graphics.graphs import FlowGraph, AirPressureGraph, BlankGraph
from graphics.graph_summaries import VolumeSummary, BPMSummary, PressurePeakSummary
from graphics.configure_alerts_button import OpenConfigureAlertsScreenButton
from graphics.right_menu_options import (MuteAlertsButton,
                                         ClearAlertsButton,
                                         LockThresholdsButton)

from drivers.wd_driver import WdDriver

class MasterFrame(object):
    def __init__(self, root, store):
        self.root = root
        self.store = store

        self.master_frame = Frame(master=self.root, bg="black")
        self.left_pane = LeftPane(self, store=store)
        self.right_pane = RightPane(self, store=store)
        self.center_pane = CenterPane(self, store=store)
        self.top_pane = TopPane(self, store=store)
        self.bottom_pane = BottomPane(self, store=store)

    @property
    def panes(self):
        return [self.top_pane, self.bottom_pane,
                self.center_pane, self.left_pane, self.right_pane]

    @property
    def element(self):
        return self.master_frame

    def render(self):
        self.master_frame.pack(fill="both", expand=True)

        for pane in self.panes:
            pane.render()


    def update(self):
        for pane in self.panes:
            pane.update()

class LeftPane(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store

        self.root = parent.element

        self.screen_height = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()

        self.height = self.screen_height * 0.65
        self.width = self.screen_width * 0.2

        self.frame = Frame(master=self.root, bg="white",
                           height=self.height,
                           width=self.width)

        self.volume_summary = VolumeSummary(self, store)
        self.bpm_summary = BPMSummary(self, store)
        self.pressure_peak_summary = PressurePeakSummary(self, store)

    @property
    def element(self):
        return self.frame

    @property
    def summaries(self):
        return (self.volume_summary, self.bpm_summary, self.pressure_peak_summary)

    def render(self):
        self.frame.grid(row=1, column=0)
        for summary in self.summaries:
            summary.render()

    def update(self):
        for summary in self.summaries:
            summary.update()


class CenterPane(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store

        self.root = parent.element
        self.screen_height = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()

        self.height = self.screen_height * 0.65
        self.width = self.screen_width * 0.7

        self.frame = Frame(master=self.root, bg="white",
                           height=self.height, width=self.width)
        self.blank_graph = BlankGraph(self.frame)
        self.flow_graph = FlowGraph(self, self.store, blank=self.blank_graph)
        self.pressure_graph = AirPressureGraph(self, self.store, blank=self.blank_graph)
        self.wd = WdDriver()  

    def pop_queue_to_list(self, q, lst):
        # pops all queue values into list, returns if items appended to queue
        had_values = not q.empty()
        while not q.empty():
            lst.pop(0)
            lst.append(q.get())
        return had_values

    @property
    def element(self):
        return self.frame

    @property
    def graphs(self):
        return [self.flow_graph, self.pressure_graph]

    def render(self):
        self.frame.grid(row=1, column=1)

        for graph in self.graphs:
            graph.render()

    def update(self):
        # Get measurments from peripherals

        had_pressure_change = self.pop_queue_to_list(self.store.pressure_measurements,
            self.pressure_graph.pressure_display_values)
        had_flow_change = self.pop_queue_to_list(self.store.flow_measurements,
            self.flow_graph.flow_display_values)
        arm_wd = had_flow_change & had_pressure_change

        # arm wd only if both queues had values
        if arm_wd:
            self.wd.arm_wd()

        for graph in self.graphs:
            graph.update()


class RightPane(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store

        self.root = parent.element
        self.screen_height = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()

        self.height = self.screen_height * 0.65
        self.width = self.screen_width * 0.1

        self.frame = Frame(master=self.root, bg="white",
                           height=self.height, width=self.width)

        self.mute_alerts_btn = MuteAlertsButton(parent=self, store=self.store)
        self.clear_alerts_btn = ClearAlertsButton(parent=self, store=self.store)
        self.lock_thresholds_btn = LockThresholdsButton(parent=self, store=self.store)

    @property
    def buttons(self):
        return (self.mute_alerts_btn, self.clear_alerts_btn, self.lock_thresholds_btn)

    @property
    def element(self):
        return self.frame

    def render(self):
        self.frame.grid(row=1, column=2)
        for button in self.buttons:
            button.render()

    def update(self):
        for button in self.buttons:
            button.update()


class TopPane(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store

        self.root = parent.element
        self.screen_height = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()

        self.height = self.screen_height * 0.15
        self.width = self.screen_width

        self.frame = Frame(master=self.root, bg="white",
                           height=self.height,
                           width=self.width)

        self.alerts_bar = IndicatorAlertBar(self, store=self.store)

    @property
    def element(self):
        return self.frame

    def render(self):
        self.frame.grid(row=0, columnspan=3)

        self.alerts_bar.render()

    def update(self):
        self.alerts_bar.update()


class BottomPane(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store

        self.root = parent.element

        self.screen_height = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()

        self.height = self.screen_height * 0.2
        self.width = self.screen_width

        self.frame = Frame(master=self.root,
                           bg="white",
                           height=self.height,
                           width=self.width)

        self.configure_alerts_btn = OpenConfigureAlertsScreenButton(self, self.store)

    @property
    def element(self):
        return self.frame

    def render(self):
        self.frame.grid(row=2, columnspan=3)
        self.configure_alerts_btn.render()

    def update(self):
        pass
