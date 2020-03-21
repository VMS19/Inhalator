import tkinter
import signal

tk = tkinter
from tkinter import *
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import numpy as np

from functools import partial

def exitProgram(signal, frame):
    print("Exit Button pressed")
    root.quit()

signal.signal(signal.SIGTERM, exitProgram)
root = Tk()
root.title("Inhalator")
root.geometry('800x480')

# Graphs X's and Y's
x = np.arange(0, 40, 1)
flow_y = np.arange(0, 40, 1)
pressure_y = np.arange(0, 40, 1)

AIR_PRESSURE_MIN_THRESHOLD = 0
AIR_PRESSURE_MAX_THRESHOLD = 0

AIR_FLOW_MIN_THRESHOLD = 0
AIR_FLOW_MAX_THRESHOLD = 0

THRESHOLD_STEP_SIZE = 0.5


def change_flow_graph_each_time():
    import random
    update_flow_graph(random.randint(1, 10))


def change_pres_graph_each_time():
    import random
    update_pressure_graph(random.randint(1, 10))


def update_pressure_graph(yvalue):
    global pressure_y
    if len(pressure_y) == len(x):
        pressure_y = np.append(np.delete(pressure_y, 0), yvalue)

    else:
        pressure_y = np.append(pressure_y, yvalue)

    pressure_graph.set_ydata(pressure_y)
    pressure_figure.canvas.draw()
    pressure_figure.canvas.flush_events()


def update_flow_graph(yvalue):
    global flow_y
    if len(flow_y) == len(x):
        flow_y = np.append(np.delete(flow_y, 0), yvalue)

    else:
        flow_y = np.append(flow_y, yvalue)

    flow_graph.set_ydata(flow_y)
    flow_figure.canvas.draw()
    flow_figure.canvas.flush_events()


def change_air_pressure_threshold(raise_value=True, min_threshold=True, prompt=True):
    global AIR_PRESSURE_MAX_THRESHOLD
    global AIR_PRESSURE_MIN_THRESHOLD

    if min_threshold:
        if raise_value:
            new_value = AIR_PRESSURE_MIN_THRESHOLD + THRESHOLD_STEP_SIZE
        else:
            new_value = AIR_PRESSURE_MIN_THRESHOLD - THRESHOLD_STEP_SIZE

    else:
        if raise_value:
            new_value = AIR_PRESSURE_MAX_THRESHOLD + THRESHOLD_STEP_SIZE

        else:
            new_value = AIR_PRESSURE_MAX_THRESHOLD - THRESHOLD_STEP_SIZE

    if prompt and not prompt_for_confirmation(
            is_pressure=True,
            going_to_increase=raise_value,
            is_min=min_threshold,
            value=new_value):
        return

    if min_threshold:
        AIR_PRESSURE_MIN_THRESHOLD = new_value

    else:
        AIR_PRESSURE_MAX_THRESHOLD = new_value


def change_air_flow_threshold(raise_value=True, min_threshold=True, prompt=True):
    global AIR_FLOW_MAX_THRESHOLD
    global AIR_FLOW_MIN_THRESHOLD

    if min_threshold:
        if raise_value:
            new_value = AIR_FLOW_MIN_THRESHOLD + THRESHOLD_STEP_SIZE
        else:
            new_value = AIR_FLOW_MIN_THRESHOLD - THRESHOLD_STEP_SIZE

    else:
        if raise_value:
            new_value = AIR_FLOW_MAX_THRESHOLD + THRESHOLD_STEP_SIZE

        else:
            new_value = AIR_FLOW_MAX_THRESHOLD - THRESHOLD_STEP_SIZE

    if prompt and not prompt_for_confirmation(
            is_pressure=False,
            going_to_increase=raise_value,
            is_min=min_threshold,
            value=new_value):
        return

    if min_threshold:
        AIR_FLOW_MIN_THRESHOLD = new_value

    else:
        AIR_FLOW_MAX_THRESHOLD = new_value


def prompt_for_confirmation(is_pressure, going_to_increase, is_min, value):
    action = "raise" if going_to_increase else "lower"
    affected = "air pressure" if is_pressure else "air flow"
    threshold_type = "minimum" if is_min else "maximum"
    message = "You asked to %s the %s's %s threshold to %s, are you sure?" % (
        action, affected, threshold_type, value)
    return messagebox.askyesno(u"ARE YOU SURE?", message)


flow_button_frame = tkinter.Frame(root)
flow_increase_min_threshold_button = Button(flow_button_frame, text="+ Min Flow Threshold",
                                              command=partial(change_air_flow_threshold, raise_value=True, min_threshold=True),
                                              height=2, width=6)
flow_decrease_min_threshold_button = Button(flow_button_frame, text="- Min Flow Threshold",
                                              command=partial(change_air_flow_threshold, raise_value=False, min_threshold=True),
                                              height=2, width=6)
flow_increase_max_threshold_button = Button(flow_button_frame, text="+ Max Flow Threshold",
                                              command=partial(change_air_flow_threshold, raise_value=True, min_threshold=False),
                                              height=2, width=6)
flow_decrease_max_threshold_button = Button(flow_button_frame, text="- Max Flow Threshold",
                                              command=partial(change_air_flow_threshold, raise_value=False, min_threshold=False),
                                              height=2, width=6)


flow_button_frame.pack(fill=tkinter.X, side=tkinter.BOTTOM)
flow_button_frame.columnconfigure(0, weight=1)
flow_button_frame.columnconfigure(1, weight=1)
flow_increase_min_threshold_button.grid(row=0, column=0, sticky=tk.W + tk.E)
flow_decrease_min_threshold_button.grid(row=0, column=1, sticky=tk.W + tk.E)
flow_increase_max_threshold_button.grid(row=1, column=0, sticky=tk.W + tk.E)
flow_decrease_max_threshold_button.grid(row=1, column=1, sticky=tk.W + tk.E)


pressure_button_frame = tkinter.Frame(root)
pressure_increase_min_threshold_button = Button(pressure_button_frame, text="+ Min Pressure Threshold",
                                          command=partial(change_air_pressure_threshold, raise_value=True, min_threshold=True),
                                          height=2, width=6)
pressure_decrease_min_threshold_button = Button(pressure_button_frame, text="- Min Pressure Threshold",
                                          command=partial(change_air_pressure_threshold, raise_value=False, min_threshold=True),
                                          height=2, width=6)
pressure_increase_max_threshold_button = Button(pressure_button_frame, text="+ Max Pressure Threshold",
                                          command=partial(change_air_pressure_threshold, raise_value=True, min_threshold=False),
                                          height=2, width=6)
pressure_decrease_max_threshold_button = Button(pressure_button_frame, text="- Max Pressure Threshold",
                                          command=partial(change_air_pressure_threshold, raise_value=False, min_threshold=False),
                                          height=2, width=6)


pressure_button_frame.pack(fill=tkinter.X, side=tkinter.BOTTOM)
pressure_button_frame.columnconfigure(0, weight=1)
pressure_button_frame.columnconfigure(1, weight=1)
pressure_increase_min_threshold_button.grid(row=0, column=0, sticky=tk.W + tk.E)
pressure_decrease_min_threshold_button.grid(row=0, column=1, sticky=tk.W + tk.E)
pressure_increase_max_threshold_button.grid(row=1, column=0, sticky=tk.W + tk.E)
pressure_decrease_max_threshold_button.grid(row=1, column=1, sticky=tk.W + tk.E)


pressure_figure = Figure(figsize=(5, 2), dpi=100)
pressure_axis = pressure_figure.add_subplot(111, label="pressure")
pressure_axis.set_ylabel('Pressure [cmH20]')
pressure_axis.set_xlabel('sec')
pressure_graph, = pressure_axis.plot(x, pressure_y)

flow_figure = Figure(figsize=(5, 2), dpi=100)
flow_axis = flow_figure.add_subplot(111, label="flow")
flow_axis.set_ylabel('Flow [L/min]')
flow_axis.set_xlabel('sec')
flow_graph, = flow_axis.plot(x, flow_y)

canvas1 = FigureCanvasTkAgg(pressure_figure, master=root)  # A tk.DrawingArea.
canvas2 = FigureCanvasTkAgg(flow_figure, master=root)  # A tk.DrawingArea.
canvas1.draw()
canvas2.draw()
canvas1.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
canvas2.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

random_flow_point = Button(master=root, text="New Flow Data", command=change_flow_graph_each_time)
random_pressure_point = Button(master=root, text="New Pressure Data", command=change_pres_graph_each_time)

random_flow_point.pack(side=tkinter.BOTTOM)
random_pressure_point.pack(side=tkinter.BOTTOM)

mainloop()
