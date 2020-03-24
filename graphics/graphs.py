from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *


MIN_TRHLD_COLOR = "green"
MAX_TRHLD_COLOR = "red"


class BlankGraph(object):
    def __init__(self, root):
        self.root = root

        blank_figure = Figure(figsize=(15, 6), dpi=100)
        blank_axis = blank_figure.add_subplot(111, label="")
        blank_canvas = FigureCanvasTkAgg(blank_figure, master=self.root)
        blank_canvas.draw()
        self.graph_bbox = blank_axis.bbox
        self.graph_bg = blank_figure.canvas.copy_from_bbox(self.graph_bbox)


class AirPressureGraph(object):
    def __init__(self, parent, store, blank):
        self.parent = parent
        self.root = parent.element
        self.store = store
        self.blank = blank

        self.height = self.parent.height * 0.5
        self.width = self.parent.width

        self.pressure_figure = Figure(figsize=(5, 2), dpi=100)
        self.pressure_axis = self.pressure_figure.add_subplot(111, label="pressure")
        self.pressure_axis.set_ylabel('Pressure [cmH20]')
        self.pressure_axis.set_xlabel('sec')

        # Calibrate x-axis
        self.pressure_axis.set_xticks(range(0, (self.store.samples_in_graph_amount + 1),
            int(self.store.samples_in_graph_amount / self.store.graph_seconds)))
        labels = range(0, int(self.store.graph_seconds + 1))
        self.pressure_axis.set_xticklabels(labels)



        self.pressure_canvas = FigureCanvasTkAgg(self.pressure_figure, master=self.root)

        self.pressure_graph, = self.pressure_axis.plot(
            self.store.x_axis, self.store.pressure_display_values, linewidth=4, animated=True)

        # Scale y values
        self.pressure_graph.axes.set_ylim(self.store.PRESSURE_MIN_Y,
                                          self.store.PRESSURE_MAX_Y)

        # Thresholds
        self.pressure_max_threshold_graph, = \
            self.pressure_axis.plot(self.store.x_axis,
                                    [self.store.pressure_max_threshold.value] *
                                    len(self.store.x_axis),
                                    color=MAX_TRHLD_COLOR, linestyle=":", animated=True)

        self.pressure_min_threshold_graph, = \
            self.pressure_axis.plot(self.store.x_axis,
                                    [self.store.pressure_min_threshold.value] *
                                    len(self.store.x_axis),
                                    color=MIN_TRHLD_COLOR, linestyle=":", animated=True)

    def render(self):
        self.pressure_canvas.draw()
        self.pressure_canvas.get_tk_widget().place(relx=0, rely=0,
                                                   height=self.height,
                                                   width=self.width)

    def update(self):
        self.pressure_figure.canvas.restore_region(self.blank.graph_bg,
                                                       bbox=self.blank.graph_bbox,
                                                       xy=(0, 0))

        self.pressure_graph.set_ydata(self.store.pressure_display_values)
        # Update threshold lines
        self.pressure_min_threshold_graph.set_ydata([self.store.pressure_min_threshold.value] *
                                                    len(self.store.x_axis))
        self.pressure_max_threshold_graph.set_ydata([self.store.pressure_max_threshold.value] *
                                                    len(self.store.x_axis))

        self.pressure_axis.draw_artist(self.pressure_graph)
        self.pressure_axis.draw_artist(self.pressure_min_threshold_graph)
        self.pressure_axis.draw_artist(self.pressure_max_threshold_graph)
        self.pressure_figure.canvas.blit(self.pressure_axis.bbox)
        self.pressure_figure.canvas.flush_events()

    @property
    def element(self):
        return self.pressure_canvas


class AirFlowGraph(object):
    def __init__(self, parent, store, blank):
        self.parent = parent
        self.root = parent.element
        self.store = store
        self.blank = blank

        self.height = self.parent.height * 0.5
        self.width = self.parent.width

        self.flow_figure = Figure(figsize=(5, 2), dpi=100)
        self.flow_axis = self.flow_figure.add_subplot(111, label="flow")
        self.flow_axis.set_ylabel('Flow [L/min]')
        self.flow_axis.set_xlabel('sec')

        # Calibrate x-axis
        self.flow_axis.set_xticks(range(0, (self.store.samples_in_graph_amount + 1),
            int(self.store.samples_in_graph_amount / self.store.graph_seconds)))
        labels = range(0, int(self.store.graph_seconds + 1))
        self.flow_axis.set_xticklabels(labels)

        self.flow_graph, = self.flow_axis.plot(self.store.x_axis,
                                               self.store.flow_display_values,
                                               linewidth=4, animated=True)

        self.flow_canvas = FigureCanvasTkAgg(self.flow_figure, master=self.root)

        # Scale y values
        self.flow_graph.axes.set_ylim(self.store.FLOW_MIN_Y, self.store.FLOW_MAX_Y)

        self.flow_max_threshold_graph, = \
            self.flow_axis.plot(self.store.x_axis,
                                [self.store.flow_max_threshold.value] *
                                len(self.store.x_axis),
                                color=MAX_TRHLD_COLOR, linestyle=":", animated=True)

        self.flow_min_threshold_graph, = \
            self.flow_axis.plot(self.store.x_axis,
                                [self.store.flow_min_threshold.value] *
                                len(self.store.x_axis),
                                color=MIN_TRHLD_COLOR, linestyle=":", animated=True)

    def render(self):
        self.flow_canvas.draw()
        self.flow_canvas.get_tk_widget().place(relx=0, rely=0.5,
                                               height=self.height,
                                               width=self.width)

    def update(self):
        self.flow_figure.canvas.restore_region(self.blank.graph_bg,
                                               bbox=self.blank.graph_bbox,
                                               xy=(0, 0))
        self.flow_graph.set_ydata(self.store.flow_display_values)
        self.flow_axis.draw_artist(self.flow_graph)
        self.flow_axis.draw_artist(self.flow_min_threshold_graph)
        self.flow_axis.draw_artist(self.flow_max_threshold_graph)
        self.flow_figure.canvas.blit(self.flow_axis.bbox)
        self.flow_figure.canvas.flush_events()

        # Update threshold lines
        self.flow_min_threshold_graph.set_ydata([self.store.flow_min_threshold.value] *
                                                len(self.store.x_axis))
        self.flow_max_threshold_graph.set_ydata([self.store.flow_max_threshold.value] *
                                                len(self.store.x_axis))

    @property
    def element(self):
        return self.flow_canvas
