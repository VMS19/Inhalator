from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import rcParams

from data.configurations import Configurations
from graphics.themes import Theme

from tkinter import *


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
    def __init__(self, parent, measurements, blank):
        super().__init__()
        self.parent = parent
        self.root = parent.element
        self.blank = blank
        self.measurements = measurements
        self.config = Configurations.instance()

        self.height = self.parent.height * 0.5
        self.width = self.parent.width

        self.figure = Figure(figsize=(5, 2), dpi=100,
                             facecolor=Theme.active().SURFACE)
        self.axis = self.figure.add_subplot(111,
                                            label="pressure")
        self.axis.spines["right"].set_visible(False)
        self.axis.spines["bottom"].set_visible(False)
        self.axis.set_ylabel('Pressure [cmH20]')

        # Calibrate x-axis
        self.axis.set_xticks([])
        self.axis.set_xticklabels([])

        amount_of_xs = self.measurements._amount_of_samples_in_graph
        self.x_axis_display_values = [0] * amount_of_xs
        self.x_axis_graph, = \
            self.axis.plot(self.measurements.x_axis,
                           self.x_axis_display_values,
                           color=Theme.active().WHITE,
                           animated=True,
                           linewidth=1)

        self.canvas = FigureCanvasTkAgg(self.figure,
                                        master=self.root)

        self.display_values = [0] * amount_of_xs
        self.graph, = self.axis.plot(
            self.measurements.x_axis,
            self.display_values,
            color=Theme.active().YELLOW,
            linewidth=1,
            animated=True)

        # Scaling
        self.current_min_y, self.current_max_y = self.scale
        self.graph.axes.set_ylim(self.current_min_y, self.current_max_y)

        # Thresholds
        self.pressure_max_threshold_graph, = \
            self.axis.plot(self.measurements.x_axis,
                           [self.config.pressure_range.max] *
                           len(self.measurements.x_axis),
                           color=Theme.active().RED,
                           animated=True,
                           linewidth=1)

        self.pressure_min_threshold_graph, = \
            self.axis.plot(self.measurements.x_axis,
                           [self.config.pressure_range.min] *
                           len(self.measurements.x_axis),
                           color=Theme.active().RED,
                           animated=True,
                           linewidth=1)

    @property
    def scale(self):
        return self.config.pressure_y_scale

    def render(self):
        self.canvas.draw()
        self.canvas.get_tk_widget().place(relx=0, rely=0,
                                          height=self.height,
                                          width=self.width)

    def update(self):
        self.figure.canvas.restore_region(self.blank.graph_bg,
                                          bbox=self.blank.graph_bbox,
                                          xy=(0, 0))

        self.graph.set_ydata(self.display_values)
        # Update threshold lines
        self.pressure_min_threshold_graph.set_ydata([self.config.pressure_range.min] *
                                                    len(self.measurements.x_axis))
        self.pressure_max_threshold_graph.set_ydata([self.config.pressure_range.max] *
                                                    len(self.measurements.x_axis))

        self.x_axis_graph.set_ydata(self.x_axis_display_values)

        self.axis.draw_artist(self.graph)
        self.axis.draw_artist(self.pressure_min_threshold_graph)
        self.axis.draw_artist(self.pressure_max_threshold_graph)
        self.axis.draw_artist(self.x_axis_graph)

        self.figure.canvas.blit(self.axis.bbox)
        self.figure.canvas.flush_events()

    @property
    def element(self):
        return self.canvas


class FlowGraph(object):
    GRAPH_MARGINS = 3  # Used for calculating the empty space in the Y-axis
    ZOOM_OUT_FREQUENCY = 50
    ZOOM_IN_FREQUENCY = 1000

    def __init__(self, parent, measurements, blank):
        super().__init__()
        rcParams.update({'figure.autolayout': True})
        self.parent = parent
        self.root = parent.element
        self.measurements = measurements
        self.blank = blank
        self.config = Configurations.instance()

        self.height = self.parent.height * 0.5
        self.width = self.parent.width

        self.figure = Figure(figsize=(5, 2),
                             dpi=100, facecolor=Theme.active().SURFACE)
        self.axis = self.figure.add_subplot(111, label="flow")
        self.axis.spines["right"].set_visible(False)
        self.axis.spines["bottom"].set_visible(False)
        self.axis.set_ylabel('Flow [L/min]')

        # Calibrate x-axis
        self.axis.set_xticks([])
        self.axis.set_xticklabels([])

        self.display_values = [0] * self.measurements._amount_of_samples_in_graph
        self.graph, = self.axis.plot(
            self.measurements.x_axis,
            self.display_values,
            color=Theme.active().LIGHT_BLUE,
            linewidth=1,
            animated=True)

        amount_of_xs = self.measurements._amount_of_samples_in_graph
        self.x_axis_display_values = [0] * amount_of_xs
        self.x_axis_graph, = \
            self.axis.plot(self.measurements.x_axis,
                           self.x_axis_display_values,
                           color=Theme.active().WHITE,
                           animated=True,
                           linewidth=1)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)

        # Scaling
        self.current_min_y, self.current_max_y = self.scale
        self.graph.axes.set_ylim(self.current_min_y, self.current_max_y)

        # State
        self.current_iteration = 0

    @property
    def scale(self):
        return self.config.flow_y_scale

    def render(self):
        self.canvas.draw()
        self.canvas.get_tk_widget().place(relx=0, rely=0.5,
                                          height=self.height,
                                          width=self.width)

    def autoscale(self):
        """Symmetrically rescale the Y-axis. """
        self.current_iteration += 1

        new_min_y = min(self.display_values)
        new_max_y = max(self.display_values)

        # Once every <self.ZOOM_IN_FREQUENCY> calls we want to try and
        # zoom back-in
        original_min, original_max = self.scale

        if (self.current_iteration % self.ZOOM_IN_FREQUENCY == 0 and
                new_max_y <= original_max < self.current_max_y and
                new_min_y >= original_min > self.current_min_y):

            self.current_min_y, self.current_max_y = original_min, original_max
            self.graph.axes.set_ylim(self.current_min_y, self.current_max_y)

            self.render()
            return

        if self.current_iteration % self.ZOOM_OUT_FREQUENCY != 0:
            # We want to calculate new max once every
            # <self.ZOOM_OUT_FREQUENCY> calls
            return

        max_y_difference = max(new_max_y - self.current_max_y, 0)
        min_y_difference = abs(max(self.current_min_y - new_min_y, 0))

        difference = max(max_y_difference, min_y_difference)

        new_min_y = self.current_min_y - difference
        new_max_y = self.current_max_y + difference

        if new_max_y <= self.current_max_y and new_min_y >= self.current_min_y:
            # no need to re-render
            return

        self.current_min_y, self.current_max_y = new_min_y, new_max_y
        self.graph.axes.set_ylim(self.current_min_y - self.GRAPH_MARGINS,
                                 self.current_max_y + self.GRAPH_MARGINS)

        self.render()

    def update(self):
        if self.config.autoscale:
            self.autoscale()

        self.figure.canvas.restore_region(self.blank.graph_bg,
                                          bbox=self.blank.graph_bbox,
                                          xy=(0, 0))

        self.graph.set_ydata(self.display_values)
        self.x_axis_graph.set_ydata(self.x_axis_display_values)
        self.axis.draw_artist(self.graph)
        self.axis.draw_artist(self.x_axis_graph)
        self.figure.canvas.blit(self.axis.bbox)
        self.figure.canvas.flush_events()

    @property
    def element(self):
        return self.canvas
