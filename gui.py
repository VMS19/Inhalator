import platform
import alerts

# Tkinter stuff
if platform.python_version() < '3':
    import tkMessageBox
    messagebox = tkMessageBox
    import Tkinter
    tk = Tkinter
    from Tkinter import *

else:
    from tkinter import messagebox
    import tkinter
    tk = tkinter
    from tkinter import *

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from functools import partial

from sound import SoundDevice
from graphics.threshold_prompt import ThresholdPrompt
from data_store import Threshold


MIN_TRHLD_COLOR = "green"
MAX_TRHLD_COLOR = "red"


class GUI(object):
    """GUI class for Inhalator"""
    TEXT_SIZE = 25

    def __init__(self, data_store):
        self.store = data_store
        self.root = Tk()
        self.flow_graph = None
        self.pressure_graph = None
        self.root.title("Inhalator")
        self.root.geometry('800x480')

        self.flow_figure = None
        self.pressure_figure = None
        self.pressure_min_threshold_graph = None
        self.pressure_max_threshold_graph = None
        self.flow_min_threshold_graph = None
        self.flow_max_threshold_graph = None

        # Labels
        self.flow_min_label = None
        self.flow_max_label = None
        self.pressure_min_label = None
        self.pressure_max_label = None

        self.pressure_min_threshold_change_button = None
        self.pressure_max_threshold_change_button = None

        self.error_dict = {
            alerts.alerts.PRESSURE_LOW : ("Pressure ({}mbar) dropped below healthy lungs pressure ({}mbar)", self.store.pressure_min_threshold),
            alerts.alerts.PRESSURE_HIGH : ("Pressure ({}mbar) exceeded healthy lungs pressure ({}mbar)", self.store.pressure_max_threshold),
            alerts.alerts.BREATHING_VOLUME_LOW : ("Breathing Volume ({}ltr) went under minimum threshold ({}ltr)", self.store.flow_min_threshold),
            alerts.alerts.BREATHING_VOLUME_HIGH : ("Breathing Volume ({}ltr) exceeded maximum threshold ({}ltr)", self.store.flow_max_threshold)
        }

    def exitProgram(self, sig, _):
        print("Exit Button pressed")
        self.root.quit()

    def update_thresholds(self):
        self.flow_max_label.config(text="{!r}".format(self.store.flow_max_threshold))
        self.flow_min_label.config(text="{!r}".format(self.store.flow_min_threshold))
        self.pressure_max_label.config(text="{!r}".format(self.store.pressure_max_threshold))
        self.pressure_min_label.config(text="{!r}".format(self.store.pressure_min_threshold))

    def update_pressure_graph(self):
        self.pressure_graph.set_ydata(self.store.pressure_display_values)
        self.pressure_figure.canvas.draw()
        self.pressure_figure.canvas.flush_events()

        # Update threshold lines
        self.pressure_min_threshold_graph.set_ydata([self.store.pressure_min_threshold.value] *
        len(self.store.x_axis))
        self.pressure_max_threshold_graph.set_ydata([self.store.pressure_max_threshold.value] *
                                                    len(self.store.x_axis))

    def update_flow_graph(self):
        self.flow_graph.set_ydata(self.store.flow_display_values)
        self.flow_figure.canvas.draw()
        self.flow_figure.canvas.flush_events()

        # Update threshold lines
        self.flow_min_threshold_graph.set_ydata([self.store.flow_min_threshold.value] *
                                                    len(self.store.x_axis))
        self.flow_max_threshold_graph.set_ydata([self.store.flow_max_threshold.value] *
                                                    len(self.store.x_axis))

    def update_alert(self):
        if self.store.alerts.empty():
            return

        cur_alert = self.store.alerts.get()
        alert_format = self.error_dict[cur_alert[0]]
        self.alert(alert_format[0].format(cur_alert[1], alert_format[1]))

    def change_threshold(self, threshold):
        prompt = ThresholdPrompt(self.root, self.store, threshold,
                                 self.on_change_threshold_prompt_exit)
        self.flow_max_threshold_change_button.configure(state="disabled")
        self.flow_min_threshold_change_button.configure(state="disabled")
        self.pressure_max_threshold_change_button.configure(state="disabled")
        self.pressure_min_threshold_change_button.configure(state="disabled")
        prompt.show()

    def on_change_threshold_prompt_exit(self):
        self.update_thresholds()
        self.flow_max_threshold_change_button.configure(state="normal")
        self.flow_min_threshold_change_button.configure(state="normal")
        self.pressure_max_threshold_change_button.configure(state="normal")
        self.pressure_min_threshold_change_button.configure(state="normal")

    def alert(self, msg):
        # TODO: display flashing icon or whatever
        tkinter.messagebox.askokcancel(title="Allah Yistor", message=msg)
        SoundDevice.beep()

    def render(self):
        #  ---------------------- Root -------------------------
        self.root.attributes("-fullscreen", True)

        #  ---------------------- Flow -------------------------
        flow_frame = LabelFrame(master=self.root, text="Air Flow", bg='red')
        flow_frame.pack(fill='both', expand=True, side="top")
        # Left-Right panes
        left_flow_frame = LabelFrame(master=flow_frame, bg='green')
        left_flow_frame.pack(fill='both', side="left", expand=True)
        right_flow_frame = LabelFrame(master=flow_frame, bg='yellow', width="40px")
        right_flow_frame.pack(fill='both', side="right", expand=True)
        # Threshold panes
        flow_max_threshold_frame = Frame(right_flow_frame, bg='gray')
        flow_max_threshold_frame.pack(fill='both', side="top", expand=True)
        flow_min_threshold_frame = Frame(right_flow_frame, bg='darkblue')
        flow_min_threshold_frame.pack(fill='both', side="bottom", expand=True)
        # Labels
        self.flow_min_label = Label(flow_min_threshold_frame, fg=MIN_TRHLD_COLOR,
                                    font=("Courier", self.TEXT_SIZE))
        self.flow_min_label.pack(fill="both", expand=True)
        self.flow_max_label = Label(flow_max_threshold_frame, fg=MAX_TRHLD_COLOR,
                                    font=("Courier", self.TEXT_SIZE))
        self.flow_max_label.pack(fill="both", expand=True)
        # Buttons
        self.flow_min_threshold_change_button = Button(flow_min_threshold_frame,
                                                       text="Change",
                                                       command=partial(
                                                           self.change_threshold,
                                                           self.store.flow_min_threshold),
                                                       height=2, width=3)
        self.flow_min_threshold_change_button.pack(fill="both", expand=True)
        self.flow_max_threshold_change_button = Button(flow_max_threshold_frame,
                                                       text="Change",
                                                       command=partial(
                                                           self.change_threshold,
                                                           self.store.flow_max_threshold),
                                                       height=2, width=3)
        self.flow_max_threshold_change_button.pack(fill="both", expand=True)
        # Graph
        self.flow_figure = Figure(figsize=(5, 2), dpi=100)
        self.flow_axis = self.flow_figure.add_subplot(111, label="flow")
        self.flow_axis.set_ylabel('Flow [L/min]')
        self.flow_axis.set_xlabel('sec')
        self.flow_graph, = self.flow_axis.plot(self.store.x_axis,
                                               self.store.flow_display_values,
                                               linewidth=4)

        # Scale y values
        self.flow_graph.axes.set_ylim(self.store.FLOW_MIN_Y, self.store.FLOW_MAX_Y)

        flow_canvas = FigureCanvasTkAgg(self.flow_figure, master=left_flow_frame)
        flow_canvas.draw()
        flow_canvas.get_tk_widget().pack(side='top', fill='both',
                                         expand=1)
        #  ---------------------- Pressure -------------------------
        pressure_frame = LabelFrame(master=self.root, text="Air Pressure", bg='blue')
        pressure_frame.pack(fill='both', expand=True, side=BOTTOM)
        # Left-Right panes
        left_pressure_frame = LabelFrame(master=pressure_frame, bg='maroon')
        left_pressure_frame.pack(fill='both', side="left", expand=True)
        right_pressure_frame = LabelFrame(master=pressure_frame, bg='cyan')
        right_pressure_frame.pack(fill='both', side="right", expand=True)
        # Threshold panes
        pressure_max_threshold_frame = Frame(right_pressure_frame, bg='orange')
        pressure_max_threshold_frame.pack(fill='both', side="top", expand=True)
        pressure_min_threshold_frame = Frame(right_pressure_frame, bg='pink')
        pressure_min_threshold_frame.pack(fill='both', side="bottom", expand=True)
        self.pressure_min_label = Label(pressure_min_threshold_frame,
                                        fg=MIN_TRHLD_COLOR, font=("Courier", self.TEXT_SIZE))
        self.pressure_min_label.pack(fill="both", expand=True)
        self.pressure_max_label = Label(pressure_max_threshold_frame,
                                        fg=MAX_TRHLD_COLOR, font=("Courier", self.TEXT_SIZE))
        self.pressure_max_label.pack(fill="both", expand=True)

        # Buttons
        self.pressure_min_threshold_change_button = Button(pressure_min_threshold_frame,
                                                           text="Change",
                                                           command=partial(
                                                               self.change_threshold,
                                                               self.store.pressure_min_threshold),
                                                           height=2, width=3)
        self.pressure_min_threshold_change_button.pack(fill="both", expand=True)
        self.pressure_max_threshold_change_button = Button(pressure_max_threshold_frame,
                                                           text="Change",
                                                           command=partial(
                                                               self.change_threshold,
                                                               self.store.pressure_max_threshold),
                                                           height=2, width=3)
        self.pressure_max_threshold_change_button.pack(fill="both", expand=True)
        # Pressure Graph
        self.pressure_figure = Figure(figsize=(5, 2), dpi=100)
        self.pressure_axis = self.pressure_figure.add_subplot(111, label="pressure")
        self.pressure_axis.set_ylabel('Pressure [cmH20]')
        self.pressure_axis.set_xlabel('sec')
        self.pressure_graph, = self.pressure_axis.plot(self.store.x_axis,
                                             self.store.pressure_display_values,
                                                  linewidth=4)

        # Scale y values
        self.pressure_graph.axes.set_ylim(self.store.PRESSURE_MIN_Y,
                                            self.store.PRESSURE_MAX_Y)

        pressure_canvas = FigureCanvasTkAgg(self.pressure_figure,
                                            master=left_pressure_frame)
        pressure_canvas.draw()
        pressure_canvas.get_tk_widget().pack(side='top', fill='both',
                                             expand=1)

        # Treshold line graphs
        self.pressure_max_threshold_graph, = \
            self.pressure_axis.plot(self.store.x_axis,
                                    [self.store.pressure_max_threshold.value] *
                                    len(self.store.x_axis),
                                    color=MAX_TRHLD_COLOR, linestyle=":")
        self.pressure_min_threshold_graph, = \
            self.pressure_axis.plot(self.store.x_axis,
                                    [self.store.pressure_min_threshold.value] *
                                    len(self.store.x_axis),
                                    color=MIN_TRHLD_COLOR, linestyle=":")
        self.flow_max_threshold_graph, = \
            self.flow_axis.plot(self.store.x_axis,
                                [self.store.flow_max_threshold.value] *
                                len(self.store.x_axis),
                                color=MAX_TRHLD_COLOR, linestyle=":")
        self.flow_min_threshold_graph, = \
            self.flow_axis.plot(self.store.x_axis,
                                [self.store.flow_min_threshold.value] *
                                len(self.store.x_axis),
                                color=MIN_TRHLD_COLOR, linestyle=":")


        # Calibrate the graphs y-values
        self.store.pressure_display_values = [0] * self.store.samples_in_graph_amount
        self.update_pressure_graph()
        self.store.flow_display_values = [0] * self.store.samples_in_graph_amount
        self.update_flow_graph()

        self.update_thresholds()

    def gui_update(self):
        self.update_flow_graph()
        self.update_pressure_graph()
        self.update_alert()
        self.root.update()
        self.root.update_idletasks()
