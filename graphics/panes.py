# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from graphics.alert_bar import IndicatorAlertBar
from graphics.graphs import AirFlowGraph, AirPressureGraph, BlankGraph
from graphics.graph_summaries import AirOutputSummary, BPMSummary, PressurePeakSummary

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

        self.frame = Frame(master=self.root, bg="red",
                           height=self.height,
                           width=self.width)

        self.air_output_summary = AirOutputSummary(self, store)
        self.bpm_summary = BPMSummary(self, store)
        self.pressure_peak_summary = PressurePeakSummary(self, store)

    @property
    def element(self):
        return self.frame

    @property
    def summaries(self):
        return (self.air_output_summary, self.bpm_summary, self.pressure_peak_summary)

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
        self.width = self.screen_width * 0.6

        self.frame = Frame(master=self.root, bg="yellow",
                           height=self.height, width=self.width)

        self.blank_graph = BlankGraph(self.frame)
        self.flow_graph = AirFlowGraph(self, self.store, blank=self.blank_graph)
        self.pressure_graph = AirPressureGraph(self, self.store, blank=self.blank_graph)


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
        self.width = self.screen_width * 0.2

        self.frame = Frame(master=self.root, bg="blue",
                           height=self.height, width=self.width)

    @property
    def element(self):
        return self.frame

    def render(self):
        self.frame.grid(row=1, column=2)

    def update(self):
        pass


class TopPane(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store

        self.root = parent.element
        self.screen_height = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()

        self.height = self.screen_height * 0.15
        self.width = self.screen_width

        self.frame = Frame(master=self.root, bg="orange",
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
                           bg="maroon",
                           height=self.height,
                           width=self.width)

    @property
    def element(self):
        return self.frame

    def render(self):
        self.frame.grid(row=2, columnspan=3)

    def update(self):
        pass

