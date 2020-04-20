from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import rcParams
from math import ceil

from data.configurations import Configurations
from graphics.themes import Theme

from tkinter import *

class Graph(object):
    RELX = NotImplemented
    RELY = NotImplemented
    LABEL = NotImplemented
    YLABEL = NotImplemented
    COLOR = NotImplemented
    DPI = 100  # pixels per inch
    ERASE_GAP = 10  # samples to be cleaned from tail, ahead of new sample print
    GRAPH_BEGIN_OFFSET = 80  # pixel offset from canvas edge, to begin of graph

    def __init__(self, parent, measurements, width, height):
        rcParams.update({'figure.autolayout': True})
        self.parent = parent
        self.root = parent.element
        self.measurements = measurements
        self.config = Configurations.instance()
        self.height = height
        self.width = width
        self.graph_bbox = None
        self.graph_clean_bg = None
        self.eraser_bg = None
        self.pixels_per_sample = None
        self.print_index = 0
        self.current_min_y, self.current_max_y = self.configured_scale

        self.figure = Figure(figsize=(self.width/self.DPI,
                                      self.height/self.DPI),
                             dpi=self.DPI, facecolor=Theme.active().SURFACE)
        self.axis = self.figure.add_subplot(111, label=self.LABEL)
        self.axis.spines["right"].set_visible(False)
        self.axis.spines["bottom"].set_visible(False)
        self.axis.set_ylabel(self.YLABEL)

        # Calibrate x-axis
        self.axis.set_xticks([])
        self.axis.set_xticklabels([])

        # Draw X axis
        self.axis.axhline(y=0, color='white', lw=1)

        # Configure graph
        self.samples_width = self.measurements._amount_of_samples_in_graph
        self.display_values = [0] * self.samples_width
        self.graph, = self.axis.plot(
            self.measurements.x_axis,
            self.display_values,
            color=self.COLOR,
            linewidth=1,
            animated=True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)

        # Scaling
        self.graph.axes.set_ylim(*self.configured_scale)
        self.figure.tight_layout()

    @property
    def graph_width(self):
        """Return the pixel width of the graph axis."""
        boundaries = self.axis.get_position() * \
                     self.axis.get_figure().get_size_inches() * self.DPI
        width, height = boundaries[1] - boundaries[0]
        return ceil(float(width))

    def save_bg(self):
        """Capture the current drawing of graph, and render it as background."""
        x1, y1, x2, y2 = self.graph_clean_bg.get_extents()

        # Capture column of pixels, from middle of the clean background,
        # This column will be pasted cyclically on the graph, to clean it.
        bbox = (x1 + 200, y1, ceil(x1 + 200 + self.pixels_per_sample), y2)
        self.eraser_bg = self.canvas.copy_from_bbox(bbox)

    def render(self):
        self.canvas.draw()
        self.canvas.get_tk_widget().place(relx=self.RELX, rely=self.RELY,
                                          height=self.height,
                                          width=self.width)
        self.graph_bbox = self.canvas.figure.bbox
        self.graph_clean_bg = self.canvas.copy_from_bbox(self.graph_bbox)

        self.pixels_per_sample = float(self.graph_width) / self.samples_width

        self.save_bg()

    def update(self):
        # print position advances cyclically
        self.print_index %= self.samples_width

        # Calculate which pixels to erase
        erase_index = \
            int(((self.print_index + self.ERASE_GAP) * self.pixels_per_sample) % self.graph_width \
            + self.GRAPH_BEGIN_OFFSET) + 1

        self.figure.canvas.restore_region(self.eraser_bg,
                                          xy=(erase_index, 0))

        self.graph.set_ydata([self.display_values[-2:]])
        self.graph.set_xdata([self.print_index, self.print_index + 1])
        self.axis.draw_artist(self.graph)
        self.figure.canvas.blit(self.graph_bbox)
        self.figure.canvas.flush_events()

        self.print_index += 1

    @property
    def element(self):
        return self.canvas

    @property
    def configured_scale(self):
        raise NotImplementedError()


class FlowGraph(Graph):
    RELX = 0
    RELY = 0.5
    LABEL = "flow"
    YLABEL = 'Flow [L/min]'
    COLOR = Theme.active().LIGHT_BLUE
    GRAPH_MARGINS = 3  # Used for calculating the empty space in the Y-axis

    # We must pick values that are a multiplication of each other, as we
    # "trim" the counter with the modulo of the maximal between them
    ZOOM_OUT_FREQUENCY = 50
    ZOOM_IN_FREQUENCY = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # State
        self.current_iteration = 0

    @property
    def configured_scale(self):
        return self.config.flow_y_scale

    def autoscale(self):
        """Symmetrically rescale the Y-axis."""
        self.current_iteration += 1
        self.current_iteration %= max(self.ZOOM_IN_FREQUENCY,
                                      self.ZOOM_OUT_FREQUENCY)

        new_min_y = min(self.display_values)
        new_max_y = max(self.display_values)

        # Once every <self.ZOOM_IN_FREQUENCY> calls we want to try and
        # zoom back-in
        original_min, original_max = self.configured_scale

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

        super().update()


class AirPressureGraph(Graph):
    RELX = 0
    RELY = 0
    LABEL = "pressure"
    YLABEL = 'Pressure [cmH20]'
    COLOR = Theme.active().YELLOW

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.min_threshold = None
        self.max_threshold = None
        self.config.pressure_range.observer.subscribe(self, self.update_thresholds)

    def update_thresholds(self, range):
        min_value, max_value = range

        if self.min_threshold:
            self.min_threshold.remove()
        if self.max_threshold:
            self.max_threshold.remove()

        # min threshold line
        self.min_threshold = self.axis.axhline(y=min_value, color='red', lw=1)
        # max threshold line
        self.max_threshold = self.axis.axhline(y=max_value, color='red', lw=1)

        self.canvas.draw()
        self.save_bg()

    def render(self):
        super().render()
        self.update_thresholds((self.config.pressure_range.min,
                                self.config.pressure_range.max))

    @property
    def configured_scale(self):
        return self.config.pressure_y_scale

    @property
    def element(self):
        return self.canvas
