from tkinter import *

from graphics.alert_bar import IndicatorAlertBar
from graphics.graphs import FlowGraph, AirPressureGraph, BlankGraph
from graphics.graph_summaries import VolumeSummary, BPMSummary, \
    PressurePeakSummary, O2SaturationSummary
from graphics.right_menu_options import (MuteAlertsButton,
                                         ClearAlertsButton,
                                         LockThresholdsButton,
                                         OpenConfigureAlertsScreenButton, OpenAlertsHistoryScreenButton)
from graphics.snackbar.recalibration_snackbar import RecalibrationSnackbar
from graphics.themes import Theme
from data.observable import Observable

from graphics.snackbar.lock_snackbar import LockSnackbar


class MasterFrame(object):
    def __init__(self, root, drivers, events, measurements):
        self.root = root
        observer = Observable()

        self.master_frame = Frame(master=self.root, bg="black")
        self.left_pane = LeftPane(self, measurements=measurements)
        self.right_pane = RightPane(self, events=events, drivers=drivers,
                                    observer=observer)
        self.center_pane = CenterPane(self, measurements=measurements)
        self.top_pane = TopPane(self, events=events, drivers=drivers,
                                measurements=measurements)
        self.recalibration_bar = RecalibrationSnackbar(self.root,
                                                       drivers,
                                                       observer)
        self.lock_bar = LockSnackbar(self.root)

    @property
    def panes(self):
        return [self.top_pane, self.center_pane,
                self.left_pane, self.right_pane]

    @property
    def bars(self):
        return [self.recalibration_bar]

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

        for bar in self.bars:
            bar.update()


class LeftPane(object):
    def __init__(self, parent, measurements):
        self.parent = parent
        self.measurements = measurements
        self.root = parent.element

        self.screen_height = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()

        self.height = self.screen_height * 0.85
        self.width = self.screen_width * 0.2

        self.frame = Frame(master=self.root,
                           bg=Theme.active().SURFACE,
                           height=self.height,
                           width=self.width)

        self.volume_summary = VolumeSummary(self, measurements)
        self.bpm_summary = BPMSummary(self, measurements)
        self.pressure_peak_summary = PressurePeakSummary(self, measurements)
        self.o2_saturation_summary = O2SaturationSummary(self, measurements)

    @property
    def element(self):
        return self.frame

    @property
    def summaries(self):
        return (self.volume_summary, self.bpm_summary,
                self.pressure_peak_summary, self.o2_saturation_summary)

    def render(self):
        self.frame.grid(row=1, column=0)
        for summary in self.summaries:
            summary.render()

    def update(self):
        for summary in self.summaries:
            summary.update()


class CenterPane(object):
    def __init__(self, parent, measurements):
        self.parent = parent
        self.measurements = measurements

        self.root = parent.element
        self.screen_height = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()

        self.height = self.screen_height * 0.85
        self.width = self.screen_width * 0.7

        self.frame = Frame(master=self.root, bg=Theme.active().SURFACE,
                           height=self.height, width=self.width)
        self.blank_graph = BlankGraph(self.frame)
        self.flow_graph = FlowGraph(self, self.measurements, blank=self.blank_graph)
        self.pressure_graph = AirPressureGraph(self, self.measurements, blank=self.blank_graph)

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

        had_pressure_change = self.pop_queue_to_list(self.measurements.pressure_measurements,
                                                     self.pressure_graph.display_values)
        had_flow_change = self.pop_queue_to_list(self.measurements.flow_measurements,
                                                 self.flow_graph.display_values)

        for graph in self.graphs:
            graph.update()


class RightPane(object):
    def __init__(self, parent, events, drivers, observer):
        self.parent = parent
        self.events = events
        self.drivers = drivers

        self.root = parent.element
        self.screen_height = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()

        self.height = self.screen_height * 0.85
        self.width = self.screen_width * 0.1

        self.frame = Frame(master=self.root, bg=Theme.active().SURFACE,
                           height=self.height, width=self.width)

        self.mute_alerts_btn = MuteAlertsButton(parent=self, events=self.events)
        self.clear_alerts_btn = ClearAlertsButton(parent=self, events=self.events)
        self.lock_thresholds_btn = LockThresholdsButton(parent=self)
        self.configure_alerts_btn = OpenConfigureAlertsScreenButton(
            self, drivers=self.drivers, observer=observer)
        self.are_buttons_locked = False
        self.lockable_buttons = [self.mute_alerts_btn, self.configure_alerts_btn]
    @property
    def buttons(self):
        return (self.mute_alerts_btn,
                self.clear_alerts_btn,
                self.configure_alerts_btn,
                self.lock_thresholds_btn)

    @property
    def element(self):
        return self.frame

    def render(self):
        self.frame.grid(row=1, column=2)
        for button in self.buttons:
            button.render()

    def update(self):
        for btn in self.buttons:
            btn.update()

    def lock_buttons(self):
        if self.are_buttons_locked:
            for button in self.lockable_buttons:
                button.enable_button()
            self.parent.lock_bar.hide()
            self.are_buttons_locked = False

        else:
            for button in self.lockable_buttons:
                button.disable_button()
            self.lock_thresholds_btn.lock_button()
            self.parent.lock_bar.show()
            self.are_buttons_locked = True

class TopPane(object):
    def __init__(self, parent, events, drivers, measurements):
        self.parent = parent
        self.events = events

        self.root = parent.element
        self.screen_height = self.root.winfo_screenheight()
        self.screen_width = self.root.winfo_screenwidth()

        self.height = self.screen_height * 0.15
        self.width = self.screen_width

        self.frame = Frame(master=self.root, bg=Theme.active().SURFACE,
                           height=self.height,
                           width=self.width)

        self.alerts_bar = IndicatorAlertBar(self,
                                            events=events,
                                            drivers=drivers,
                                            measurements=measurements)

    @property
    def element(self):
        return self.frame

    def render(self):
        self.frame.grid(row=0, columnspan=3)

        self.alerts_bar.render()

    def update(self):
        self.alerts_bar.update()
