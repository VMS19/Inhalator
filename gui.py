import platform

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


class Graphics(object):
    """Graphics class for Inhalator"""
    def __init__(self, data_store):
        self.store = data_store
        self.root = Tk()
        self.flow_graph = None
        self.pressure_graph = None
        self.root.title("Inhalator")
        self.root.geometry('800x480')

        self.flow_figure = None
        self.pressure_figure = None
        self.flow_min_threshold_label = None
        self.flow_max_threshold_label = None
        self.pressure_min_threshold_label = None
        self.pressure_max_threshold_label = None

    def exitProgram(self, sig, _):
        print("Exit Button pressed")
        self.root.quit()

    def update_pressure_graph(self):
        self.pressure_graph.set_ydata(self.store.pressure_display_values)
        self.pressure_figure.canvas.draw()
        self.pressure_figure.canvas.flush_events()

    def update_flow_graph(self):
        print("Updating flow with value: {}".format(self.store.flow_display_values[-1]))
        self.flow_graph.set_ydata(self.store.flow_display_values)
        self.flow_figure.canvas.draw()
        self.flow_figure.canvas.flush_events()

    def update_alert(self):
        if self.store.alerts.empty():
            return

        first_alert = self.store.alerts.get()
        self.alert(first_alert)

    def change_air_pressure_threshold(self, raise_value=True, min_threshold=True, prompt=True):
        if min_threshold:
            if raise_value:
                new_value = self.store.pressure_min_threshold + self.store.THRESHOLD_STEP_SIZE
            else:
                new_value = self.store.pressure_min_threshold - self.store.THRESHOLD_STEP_SIZE

        else:
            if raise_value:
                new_value = self.store.pressure_max_threshold + self.store.THRESHOLD_STEP_SIZE

            else:
                new_value = self.store.pressure_max_threshold - self.store.THRESHOLD_STEP_SIZE

        if prompt and not self.prompt_for_confirmation(
                is_pressure=True,
                going_to_increase=raise_value,
                is_min=min_threshold,
                value=new_value):
            return

        if min_threshold:
            self.store.pressure_min_threshold = new_value
            self.pressure_min_threshold_label.config(
                text="Min: {}bar".format(new_value))

        else:
            self.store.pressure_max_threshold = new_value
            self.pressure_max_threshold_label.config(
                text="Max: {}bar".format(new_value))

    def change_air_flow_threshold(self, raise_value=True, min_threshold=True, prompt=True):
        if min_threshold:
            if raise_value:
                new_value = self.store.flow_min_threshold + self.store.THRESHOLD_STEP_SIZE
            else:
                new_value = self.store.flow_min_threshold - self.store.THRESHOLD_STEP_SIZE

        else:
            if raise_value:
                new_value = self.store.flow_max_threshold + self.store.THRESHOLD_STEP_SIZE

            else:
                new_value = self.store.flow_max_threshold - self.store.THRESHOLD_STEP_SIZE

        if prompt and not self.prompt_for_confirmation(
                is_pressure=False,
                going_to_increase=raise_value,
                is_min=min_threshold,
                value=new_value):
            return

        if min_threshold:
            self.store.flow_min_threshold = new_value
            self.flow_min_threshold_label.config(
                text="Min: {}Liter".format(new_value))

        else:
            self.store.flow_max_threshold = new_value
            self.flow_max_threshold_label.config(
                text="Max: {}Liter".format(new_value))

    def prompt_for_confirmation(self, is_pressure, going_to_increase, is_min, value):
        action = "raise" if going_to_increase else "lower"
        affected = "air pressure" if is_pressure else "air flow"
        threshold_type = "minimum" if is_min else "maximum"
        message = "You asked to %s the %s's %s threshold to %s, are you sure?" % (
            action, affected, threshold_type, value)
        return messagebox.askyesno(u"ARE YOU SURE?", message)

    def alert(self, msg):
        # TODO: Play sounds as well and display flashing icon or whatever
        # tkinter.messagebox.askokcancel(title="Allah Yistor", message=msg)
        SoundDevice.beep()
        pass

    def render_gui(self):
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
        self.flow_min_threshold_label = Label(flow_min_threshold_frame,
                    text="Min: {}Liter".format(self.store.flow_min_threshold))
        self.flow_min_threshold_label.pack(fill="both", expand=True)
        self.flow_max_threshold_label = Label(flow_max_threshold_frame,
                                              text="Max: {}Liter".format(self.store.flow_max_threshold))
        self.flow_max_threshold_label.pack(fill="both", expand=True)
        # Buttons
        flow_increase_min_threshold_button = Button(flow_min_threshold_frame,
                                                    text="+ Min Flow Threshold",
                                                    command=partial(
                                                        self.change_air_flow_threshold,
                                                        raise_value=True,
                                                        min_threshold=True),
                                                    height=2, width=3)
        flow_increase_min_threshold_button.pack(fill="both", expand=True)
        flow_decrease_min_threshold_button = Button(flow_min_threshold_frame,
                                                    text="- Min Flow Threshold",
                                                    command=partial(
                                                        self.change_air_flow_threshold,
                                                        raise_value=False,
                                                        min_threshold=True),
                                                    height=2, width=3)
        flow_decrease_min_threshold_button.pack(fill="both", expand=True)
        flow_increase_max_threshold_button = Button(flow_max_threshold_frame,
                                                    text="+ Max Flow Threshold",
                                                    command=partial(
                                                        self.change_air_flow_threshold,
                                                        raise_value=True,
                                                        min_threshold=False),
                                                    height=2, width=3)
        flow_increase_max_threshold_button.pack(fill="both", expand=True)
        flow_decrease_max_threshold_button = Button(flow_max_threshold_frame,
                                                    text="- Max Flow Threshold",
                                                    command=partial(
                                                        self.change_air_flow_threshold,
                                                        raise_value=False,
                                                        min_threshold=False),
                                                    height=2, width=3)
        flow_decrease_max_threshold_button.pack(fill="both", expand=True)
        # Graph
        self.flow_figure = Figure(figsize=(5, 2), dpi=100)
        flow_axis = self.flow_figure.add_subplot(111, label="flow")
        flow_axis.set_ylabel('Flow [L/min]')
        flow_axis.set_xlabel('sec')
        self.flow_graph, = flow_axis.plot(self.store.x_axis, self.store.flow_display_values)
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
        self.pressure_min_threshold_label = Label(pressure_min_threshold_frame,
                                              text="Min: {}bar".format(self.store.pressure_min_threshold))
        self.pressure_min_threshold_label.pack(fill="both", expand=True)
        self.pressure_max_threshold_label = Label(pressure_max_threshold_frame,
                                              text="Max: {}bar".format(self.store.pressure_max_threshold))
        self.pressure_max_threshold_label.pack(fill="both", expand=True)
        # Buttons
        pressure_increase_min_threshold_button = Button(
            pressure_min_threshold_frame, text="+ Min Pressure Threshold",
            command=partial(self.change_air_pressure_threshold, raise_value=True,
                            min_threshold=True),
            height=2, width=6)
        pressure_increase_min_threshold_button.pack(fill="both", expand=True)
        pressure_decrease_min_threshold_button = Button(
            pressure_min_threshold_frame, text="- Min Pressure Threshold",
            command=partial(self.change_air_pressure_threshold, raise_value=False,
                            min_threshold=True),
            height=2, width=6)
        pressure_decrease_min_threshold_button.pack(fill="both", expand=True)
        pressure_increase_max_threshold_button = Button(
            pressure_max_threshold_frame, text="+ Max Pressure Threshold",
            command=partial(self.change_air_pressure_threshold, raise_value=True,
                            min_threshold=False),
            height=2, width=6)
        pressure_increase_max_threshold_button.pack(fill="both", expand=True)
        pressure_decrease_max_threshold_button = Button(
            pressure_max_threshold_frame, text="- Max Pressure Threshold",
            command=partial(self.change_air_pressure_threshold, raise_value=False,
                            min_threshold=False),
            height=2, width=6)
        pressure_decrease_max_threshold_button.pack(fill="both", expand=True)
        # Pressure Graph
        self.pressure_figure = Figure(figsize=(5, 2), dpi=100)
        pressure_axis = self.pressure_figure.add_subplot(111, label="pressure")
        pressure_axis.set_ylabel('Pressure [cmH20]')
        pressure_axis.set_xlabel('sec')
        self.pressure_graph, = pressure_axis.plot(self.store.x_axis,
                                             self.store.pressure_display_values,
                                                  linewidth=4)
        self.pressure_max_threshold_graph, = \
            pressure_axis.plot(self.store.x_axis,
                               [self.store.pressure_max_threshold] *
                               len(self.store.x_axis), linestyle=":")
        self.pressure_min_threshold_graph, = \
            pressure_axis.plot(self.store.x_axis,
                               [self.store.pressure_min_threshold] *
                               len(self.store.x_axis), linestyle=":")
        pressure_canvas = FigureCanvasTkAgg(self.pressure_figure,
                                            master=left_pressure_frame)
        pressure_canvas.draw()
        pressure_canvas.get_tk_widget().pack(side='top', fill='both',
                                             expand=1)

        # Calibrate the graphs y-values
        self.store.pressure_display_values = [0] * 40
        self.update_pressure_graph()
        self.store.flow_display_values = [0] * 40
        self.update_flow_graph()

    def gui_update(self):
        self.update_flow_graph()
        self.update_pressure_graph()
        self.update_alert()
        self.root.update()
        self.root.update_idletasks()
