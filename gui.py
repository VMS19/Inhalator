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
root.title("Respirator")
root.geometry('800x480')

x = np.arange(0, 3, .01)

debug_running_counter = 0

AIR_PRESSURE_MIN_THRESHOLD = 0
AIR_PRESSURE_MAX_THRESHOLD = 0

AIR_VOLUME_MIN_THRESHOLD = 0
AIR_VOLUME_MAX_THRESHOLD = 0

THRESHOLD_STEP_SIZE = 0.5


def change_vol_graph_each_time():
    global debug_running_counter
    update_volume_graph(np.sin(x + debug_running_counter))
    debug_running_counter += 1


def change_pres_graph_each_time():
    global debug_running_counter
    update_pressure_graph(np.sin(x + debug_running_counter))
    debug_running_counter += 1


def update_pressure_graph(ydata):
    pressure_y.set_ydata(ydata)
    pressure_graph.canvas.draw()
    pressure_graph.canvas.flush_events()


def update_volume_graph(ydata):
    volume_y.set_ydata(ydata)
    volume_graph.canvas.draw()
    volume_graph.canvas.flush_events()


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


def change_air_volume_threshold(raise_value=True, min_threshold=True, prompt=True):
    global AIR_VOLUME_MAX_THRESHOLD
    global AIR_VOLUME_MIN_THRESHOLD

    if min_threshold:
        if raise_value:
            new_value = AIR_VOLUME_MIN_THRESHOLD + THRESHOLD_STEP_SIZE
        else:
            new_value = AIR_VOLUME_MIN_THRESHOLD - THRESHOLD_STEP_SIZE

    else:
        if raise_value:
            new_value = AIR_VOLUME_MAX_THRESHOLD + THRESHOLD_STEP_SIZE

        else:
            new_value = AIR_VOLUME_MAX_THRESHOLD - THRESHOLD_STEP_SIZE

    if prompt and not prompt_for_confirmation(
            is_pressure=False,
            going_to_increase=raise_value,
            is_min=min_threshold,
            value=new_value):
        return

    if min_threshold:
        AIR_VOLUME_MIN_THRESHOLD = new_value

    else:
        AIR_VOLUME_MAX_THRESHOLD = new_value


def prompt_for_confirmation(is_pressure, going_to_increase, is_min, value):
    action = "raise" if going_to_increase else "lower"
    affected = "air pressure" if is_pressure else "volume"
    threshold_type = "minimum" if is_min else "maximum"
    message = "You asked to %s the %s's %s value to %s, are you sure?" % (
        action, affected, threshold_type, value)
    return messagebox.askyesno(u"ARE YOU SURE?", message)



volume_button_frame = tkinter.Frame(root)
volume_increase_min_threshold_button = Button(volume_button_frame, text="+ Min Volume Threshold",
                                          command=partial(change_air_volume_threshold, raise_value=True, min_threshold=True),
                                          height=2, width=6)
volume_decrease_min_threshold_button = Button(volume_button_frame, text="- Min Volume Threshold",
                                          command=partial(change_air_volume_threshold, raise_value=False, min_threshold=True),
                                          height=2, width=6)
volume_increase_max_threshold_button = Button(volume_button_frame, text="+ Max Volume Threshold",
                                          command=partial(change_air_volume_threshold, raise_value=True, min_threshold=False),
                                          height=2, width=6)
volume_decrease_max_threshold_button = Button(volume_button_frame, text="- Max Volume Threshold",
                                          command=partial(change_air_volume_threshold, raise_value=False, min_threshold=False),
                                          height=2, width=6)


volume_button_frame.pack(fill=tkinter.X, side=tkinter.BOTTOM)
volume_button_frame.columnconfigure(0, weight=1)
volume_button_frame.columnconfigure(1, weight=1)
volume_increase_min_threshold_button.grid(row=0, column=0, sticky=tk.W + tk.E)
volume_decrease_min_threshold_button.grid(row=0, column=1, sticky=tk.W + tk.E)
volume_increase_max_threshold_button.grid(row=1, column=0, sticky=tk.W + tk.E)
volume_decrease_max_threshold_button.grid(row=1, column=1, sticky=tk.W + tk.E)


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



pressure_graph = Figure(figsize=(5, 2), dpi=100)
pressure_axis = pressure_graph.add_subplot(111, label="pressure")
pressure_axis.set_ylabel('Pressure [cmH20]')
pressure_axis.set_xlabel('sec')
pressure_y, = pressure_axis.plot(x, 2 * np.sin(2 * np.pi * x))

volume_graph = Figure(figsize=(5, 2), dpi=100)
volume_axis = volume_graph.add_subplot(111, label="volume")
volume_axis.set_ylabel('Flow [L/min]')
volume_axis.set_xlabel('sec')
volume_y, = volume_axis.plot(x, 2 * np.sin(2 * np.pi * x))

canvas1 = FigureCanvasTkAgg(pressure_graph, master=root)  # A tk.DrawingArea.
canvas2 = FigureCanvasTkAgg(volume_graph, master=root)  # A tk.DrawingArea.
canvas1.draw()
canvas2.draw()
canvas1.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
canvas2.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

mainloop()

print(5)