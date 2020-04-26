from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import rcParams
from matplotlib.transforms import Bbox
from matplotlib import ticker
from math import ceil

from data.configurations import Configurations
from graphics.themes import Theme


class Graph(object):
    RELX = NotImplemented
    RELY = NotImplemented
    LABEL = NotImplemented
    YLABEL = NotImplemented
    COLOR = NotImplemented
    DPI = 100  # pixels per inch
    ERASE_GAP = 10  # samples to be cleaned from tail, ahead of new sample print
    GRAPH_BEGIN_OFFSET = 70  # pixel offset from canvas edge, to begin of graph

    def __init__(self, parent, measurements, width, height):
        rcParams.update({'figure.autolayout': True})
        self.parent = parent
        self.root = parent.element
        self.measurements = measurements
        self.config = Configurations.instance()
        self.height = height
        self.width = width

        # pixel width of graph draw area, without axes
        self.graph_width = None
        self.graph_height = None
        self.graph_bbox = None
        # snapshot of graph frame, in clean state
        self.graph_clean_bg = None
        # snapshot of 1 sample-width column, from clean graph
        self.eraser_bg = None
        self.pixels_per_sample = None
        # index of last updated sample
        self.print_index = -1
        self.erase_index = None

        self.figure = Figure(figsize=(self.width/self.DPI,
                                      self.height/self.DPI),
                             dpi=self.DPI, facecolor=Theme.active().SURFACE)

        self.axis = self.figure.add_subplot(111, label=self.LABEL)
        self.axis.set_ylabel(self.YLABEL, labelpad=0)

        # Remove white lines around graph frame
        self.axis.spines["right"].set_visible(False)
        self.axis.spines["bottom"].set_visible(False)
        self.axis.spines["left"].set_visible(False)
        self.axis.spines["top"].set_visible(False)

        self.axis.tick_params(axis='y', direction='out', length=3, width=1, colors='w')
        # Calibrate x-axis
        self.axis.set_xticks([])
        self.axis.set_xticklabels([])
        # Set max number of tick labels in y axis to 7
        self.axis.yaxis.set_major_locator(ticker.MaxNLocator(nbins=7,
                                                             integer=True))

        # Make y axis labels aligned
        self.axis.yaxis.set_major_formatter(self.tick_aligned_format)

        # Draw X axis
        self.axis.axhline(y=0, color='white', lw=1)

        # Configure graph
        self.graph, = self.axis.plot(
            self.measurements.x_axis,
            self.display_values,
            color=self.COLOR,
            linewidth=1,
            animated=True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)

        # Scaling
        self.current_min_y, self.current_max_y = self.configured_scale
        self.graph.axes.set_ylim(*self.configured_scale)
        self.figure.tight_layout()

    def get_graph_width(self):
        """Return the pixel width of the graph axis."""
        boundaries = self.axis.get_position() * \
                     self.axis.get_figure().get_size_inches() * self.DPI
        width, height = boundaries[1] - boundaries[0]
        return ceil(float(width))

    def save_eraser_bg(self):
        """Capture background for eraser of cyclic graph."""
        # graph boundary points
        x1, y1, x2, y2 = self.graph_clean_bg.get_extents()

        # Capture column of pixels, from middle of the clean background,
        # This column will be pasted cyclically on the graph, to clean it.
        capture_offset = x1 + (self.graph_width / 2)
        eraser_width = ceil(self.pixels_per_sample)
        self.graph_height = y2 - y1
        bbox = (capture_offset, y1, capture_offset + eraser_width, y2)
        self.eraser_bg = self.canvas.copy_from_bbox(bbox)

    @staticmethod
    @ticker.FuncFormatter
    def tick_aligned_format(x, pos):
        """Print positive tick numbers with space placeholder,
           to align with minus sign of negative numbers
        """
        label = f"{x:.0f}"
        if x >= 0:
            label = " " + label

        return label

    def render(self):
        self._redraw_frame()

    def _redraw_frame(self):
        """Called only once - to render the graph"""
        self.canvas.draw()
        self.canvas.get_tk_widget().place(relx=self.RELX, rely=self.RELY,
                                          height=self.height,
                                          width=self.width)
        self.graph_bbox = self.canvas.figure.bbox
        self.graph_clean_bg = self.canvas.copy_from_bbox(self.graph_bbox)
        self.graph_width = self.get_graph_width()
        self.pixels_per_sample = \
            float(self.graph_width) / self.measurements.samples_in_graph
        self.save_eraser_bg()

    def redraw_graph(self):
        """Redraw entire graph. Called when graph properties changed."""
        print_index = self.print_index + 2

        # Clone and reorder samples list, to match the draw order
        recovery_y_values = self.display_values.copy()
        recovery_y_values.rotate(print_index)
        recovery_y_values = list(recovery_y_values)

        # Ranges of graph parts to redraw
        draw_ranges = []

        if self.print_index < self.erase_index:
            # Normal case: during draw cycle
            # |~~~ ~~~|
            draw_ranges = [(0, print_index),
                           (self.erase_index+5, self.measurements.samples_in_graph)]

        elif self.print_index > self.erase_index:
            # Draw cycle at the right edge. started erasing the left edge
            # | ~~~~ |
            draw_ranges = [(self.erase_index+5, print_index)]

        # Draw all graph parts
        for start_index, end_index in draw_ranges:
            self.graph.set_ydata(recovery_y_values[start_index:end_index])
            self.graph.set_xdata(self.measurements.x_axis[start_index:end_index])
            self.axis.draw_artist(self.graph)

        self.figure.canvas.blit(self.graph_bbox)

    def update(self):
        # drawn sample index advances cyclically
        self.print_index += 1
        self.print_index %= self.measurements.samples_in_graph

        # Calculate pixel offsets to erase and print at
        self.erase_index = (self.print_index + self.ERASE_GAP) % \
            self.measurements.samples_in_graph
        erase_offset = int(self.erase_index * self.pixels_per_sample) \
            % self.graph_width + self.GRAPH_BEGIN_OFFSET
        print_offset = int(self.print_index * self.pixels_per_sample) \
            % self.graph_width + self.GRAPH_BEGIN_OFFSET

        # Paste eraser column background, to erase tail sample
        self.figure.canvas.restore_region(self.eraser_bg,
                                          xy=(erase_offset, 0))

        # Draw line between 2 most recent samples
        self.graph.set_ydata([self.display_values[-2], self.display_values[-1]])
        self.graph.set_xdata([self.print_index, self.print_index + 1])
        self.axis.draw_artist(self.graph)

        # Update screen only in printed column and erased column areas
        self.figure.canvas.blit(Bbox.from_bounds(x0=print_offset, y0=0,
                                                 width=self.pixels_per_sample,
                                                 height=self.graph_height))
        self.figure.canvas.blit(Bbox.from_bounds(x0=erase_offset, y0=0,
                                                 width=self.pixels_per_sample,
                                                 height=self.graph_height))
        self.figure.canvas.flush_events()

    @property
    def element(self):
        return self.canvas

    @property
    def configured_scale(self):
        raise NotImplementedError()

    @property
    def display_values(self):
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
    ZOOM_IN_FREQUENCY = 200

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # State
        self.current_iteration = 0

    @property
    def configured_scale(self):
        return self.config.flow_y_scale

    @property
    def display_values(self):
        return self.measurements.flow_measurements

    def autoscale(self):
        """Symmetrically rescale the Y-axis."""
        self.current_iteration += 1
        self.current_iteration %= max(self.ZOOM_IN_FREQUENCY,
                                      self.ZOOM_OUT_FREQUENCY)

        if len(self.display_values):
            new_min_y = min(self.display_values)
            new_max_y = max(self.display_values)
        else:
            new_min_y = 0
            new_max_y = 0

        # Once every <self.ZOOM_IN_FREQUENCY> calls we want to try and
        # zoom back-in
        original_min, original_max = self.configured_scale

        if (self.current_iteration % self.ZOOM_IN_FREQUENCY == 0 and
                new_max_y <= original_max < self.current_max_y and
                new_min_y >= original_min > self.current_min_y):

            self.current_min_y, self.current_max_y = original_min, original_max
            self.graph.axes.set_ylim(self.current_min_y, self.current_max_y)
            self._redraw_frame()
            self.redraw_graph()
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

        self._redraw_frame()
        self.redraw_graph()

    def update(self):
        super().update()
        if self.config.autoscale:
            self.autoscale()


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
        self.config.pressure_range.observer.subscribe(self,
                                                      self.update_thresholds)

    def update_thresholds(self, pressure_range, redraw_graph=True):
        min_value, max_value = pressure_range

        if self.min_threshold:
            self.min_threshold.remove()
        if self.max_threshold:
            self.max_threshold.remove()

        self.min_threshold = self.axis.axhline(y=min_value, color='red', lw=1)
        self.max_threshold = self.axis.axhline(y=max_value, color='red', lw=1)

        self._redraw_frame()
        if redraw_graph:
            self.redraw_graph()

    def render(self):
        self.update_thresholds((self.config.pressure_range.min,
                                self.config.pressure_range.max),
                               redraw_graph=False)

    @property
    def configured_scale(self):
        return self.config.pressure_y_scale

    @property
    def display_values(self):
        return self.measurements.pressure_measurements
