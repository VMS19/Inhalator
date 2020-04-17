from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import rcParams

from data.configurations import Configurations
from graphics.themes import Theme

from tkinter import *

class Graph(object):
    RELX = NotImplemented
    RELY = NotImplemented
    LABEL = NotImplemented
    YLABEL = NotImplemented
    COLOR = NotImplemented

    def __init__(self, parent, measurements, height):
        rcParams.update({'figure.autolayout': True})
        self.parent = parent
        self.root = parent.element
        self.measurements = measurements
        self.config = Configurations.instance()
        self.height = height
        self.width = self.parent.width
        self.graph_bbox = None
        self.graph_bg = None

        self.figure = Figure(figsize=(self.width/100.0, self.height/100.0),
                             dpi=100, facecolor=Theme.active().SURFACE)
        self.axis = self.figure.add_subplot(111, label=self.LABEL)
        self.axis.spines["right"].set_visible(False)
        self.axis.spines["bottom"].set_visible(False)
        self.axis.set_ylabel(self.YLABEL)

        # Calibrate x-axis
        self.axis.set_xticks([])
        self.axis.set_xticklabels([])

        # X axis
        self.axis.axhline(y=0, color='white', lw=1)

        self.display_values = [0] * self.measurements._amount_of_samples_in_graph
        self.graph, = self.axis.plot(
            self.measurements.x_axis,
            self.display_values,
            color=self.COLOR,
            linewidth=1,
            animated=True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)

        # Scale y values
        self.graph.axes.set_ylim(*self.y_scale)

    def save_bg(self):
        """Capture the current drawing of graph, and render it as background."""
        self.graph_bg = self.canvas.copy_from_bbox(self.graph_bbox)

    def render(self):
        self.canvas.draw()
        self.canvas.get_tk_widget().place(relx=self.RELX, rely=self.RELY,
                                          height=self.height,
                                          width=self.width)

        self.graph_bbox = self.canvas.figure.bbox
        self.save_bg()

    def update(self):
        self.figure.canvas.restore_region(self.graph_bg)
        self.graph.set_ydata(self.display_values)
        self.axis.draw_artist(self.graph)
        self.figure.canvas.blit(self.graph_bbox)
        self.figure.canvas.flush_events()

    @property
    def element(self):
        return self.canvas

    @property
    def y_scale(self):
        raise NotImplemented


class FlowGraph(Graph):
    RELX = 0
    RELY = 0.5
    LABEL = "flow"
    YLABEL = 'Flow [L/min]'
    COLOR = Theme.active().LIGHT_BLUE

    @property
    def y_scale(self):
        return self.config.flow_y_scale


class AirPressureGraph(Graph):
    RELX = 0
    RELY = 0
    LABEL = "pressure"
    YLABEL = 'Pressure [cmH20]'
    COLOR = Theme.active().YELLOW

    def __init__(self, *args):
        super().__init__(*args)
        self.config.pressure_range.observer.subscribe(self, self.update_thresholds)
        self.min_threshold = None
        self.max_threshold = None
        self.update_thresholds((self.config.pressure_range.min,
                                self.config.pressure_range.max))

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


    @property
    def y_scale(self):
        return self.config.pressure_y_scale
