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

import time
import logging
from logging.handlers import RotatingFileHandler
from functools import partial

from data_store import DataStore
from algo import Sampler
from sound import SoundDevice

from mocks.mock_hce_pressure_sensor import MockHcePressureSensor
from mocks.mock_sfm3200_flow_sensor import MockSfm3200

root = Tk()
store = DataStore()
flow_graph = None
pressure_graph = None


def exitProgram(signal, frame):
    print("Exit Button pressed")
    root.quit()


def update_pressure_graph():
    pressure_graph.set_ydata(store.pressure_display_values)
    pressure_figure.canvas.draw()
    pressure_figure.canvas.flush_events()


def update_flow_graph():
    print("Updating flow with value: {}".format(store.flow_display_values[-1]))
    flow_graph.set_ydata(store.flow_display_values)
    flow_figure.canvas.draw()
    flow_figure.canvas.flush_events()


def update_alert():
    if store.alerts.empty():
        return

    first_alert = store.alerts.get()
    alert(first_alert)


def change_air_pressure_threshold(raise_value=True, min_threshold=True, prompt=True):
    if min_threshold:
        if raise_value:
            new_value = store.pressure_min_threshold + store.THRESHOLD_STEP_SIZE
        else:
            new_value = store.pressure_min_threshold - store.THRESHOLD_STEP_SIZE

    else:
        if raise_value:
            new_value = store.pressure_max_threshold + store.THRESHOLD_STEP_SIZE

        else:
            new_value = store.pressure_max_threshold - store.THRESHOLD_STEP_SIZE

    if prompt and not prompt_for_confirmation(
            is_pressure=True,
            going_to_increase=raise_value,
            is_min=min_threshold,
            value=new_value):
        return

    if min_threshold:
        store.pressure_min_threshold = new_value

    else:
        store.pressure_max_threshold = new_value


def change_air_flow_threshold(raise_value=True, min_threshold=True, prompt=True):
    if min_threshold:
        if raise_value:
            new_value = store.flow_min_threshold + store.THRESHOLD_STEP_SIZE
        else:
            new_value = store.flow_min_threshold - store.THRESHOLD_STEP_SIZE

    else:
        if raise_value:
            new_value = store.flow_max_threshold + store.THRESHOLD_STEP_SIZE

        else:
            new_value = store.flow_max_threshold - store.THRESHOLD_STEP_SIZE

    if prompt and not prompt_for_confirmation(
            is_pressure=False,
            going_to_increase=raise_value,
            is_min=min_threshold,
            value=new_value):
        return

    if min_threshold:
        store.flow_min_threshold = new_value

    else:
        store.flow_max_threshold = new_value


def prompt_for_confirmation(is_pressure, going_to_increase, is_min, value):
    action = "raise" if going_to_increase else "lower"
    affected = "air pressure" if is_pressure else "air flow"
    threshold_type = "minimum" if is_min else "maximum"
    message = "You asked to %s the %s's %s threshold to %s, are you sure?" % (
        action, affected, threshold_type, value)
    return messagebox.askyesno(u"ARE YOU SURE?", message)


def alert(msg):
    # TODO: Play sounds as well and display flashing icon or whatever
    # tkinter.messagebox.askokcancel(title="Allah Yistor", message=msg)
    SoundDevice.beep()
    pass


def render_gui():
    global flow_figure, flow_graph, pressure_figure, pressure_graph
    #  ---------------------- Flow -------------------------
    flow_frame = LabelFrame(master=root, text="Air Flow", bg='red')
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
    # Buttons
    flow_increase_min_threshold_button = Button(flow_min_threshold_frame,
                                                text="+ Min Flow Threshold",
                                                command=partial(
                                                    change_air_flow_threshold,
                                                    raise_value=True,
                                                    min_threshold=True),
                                                height=2, width=3)
    flow_increase_min_threshold_button.pack(fill="both", expand=True)
    flow_decrease_min_threshold_button = Button(flow_min_threshold_frame,
                                                text="- Min Flow Threshold",
                                                command=partial(
                                                    change_air_flow_threshold,
                                                    raise_value=False,
                                                    min_threshold=True),
                                                height=2, width=3)
    flow_decrease_min_threshold_button.pack(fill="both", expand=True)
    flow_increase_max_threshold_button = Button(flow_max_threshold_frame,
                                                text="+ Max Flow Threshold",
                                                command=partial(
                                                    change_air_flow_threshold,
                                                    raise_value=True,
                                                    min_threshold=False),
                                                height=2, width=3)
    flow_increase_max_threshold_button.pack(fill="both", expand=True)
    flow_decrease_max_threshold_button = Button(flow_max_threshold_frame,
                                                text="- Max Flow Threshold",
                                                command=partial(
                                                    change_air_flow_threshold,
                                                    raise_value=False,
                                                    min_threshold=False),
                                                height=2, width=3)
    flow_decrease_max_threshold_button.pack(fill="both", expand=True)
    # Graph
    flow_figure = Figure(figsize=(5, 2), dpi=100)
    flow_axis = flow_figure.add_subplot(111, label="flow")
    flow_axis.set_ylabel('Flow [L/min]')
    flow_axis.set_xlabel('sec')
    flow_graph, = flow_axis.plot(store.x_axis, store.flow_display_values)
    flow_canvas = FigureCanvasTkAgg(flow_figure, master=left_flow_frame)
    flow_canvas.draw()
    flow_canvas.get_tk_widget().pack(side='top', fill='both',
                                     expand=1)
    #  ---------------------- Pressure -------------------------
    pressure_frame = LabelFrame(master=root, text="Air Pressure", bg='blue')
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
    # Buttons
    pressure_increase_min_threshold_button = Button(
        pressure_min_threshold_frame, text="+ Min Pressure Threshold",
        command=partial(change_air_pressure_threshold, raise_value=True,
                        min_threshold=True),
        height=2, width=6)
    pressure_increase_min_threshold_button.pack(fill="both", expand=True)
    pressure_decrease_min_threshold_button = Button(
        pressure_min_threshold_frame, text="- Min Pressure Threshold",
        command=partial(change_air_pressure_threshold, raise_value=False,
                        min_threshold=True),
        height=2, width=6)
    pressure_decrease_min_threshold_button.pack(fill="both", expand=True)
    pressure_increase_max_threshold_button = Button(
        pressure_max_threshold_frame, text="+ Max Pressure Threshold",
        command=partial(change_air_pressure_threshold, raise_value=True,
                        min_threshold=False),
        height=2, width=6)
    pressure_increase_max_threshold_button.pack(fill="both", expand=True)
    pressure_decrease_max_threshold_button = Button(
        pressure_max_threshold_frame, text="- Max Pressure Threshold",
        command=partial(change_air_pressure_threshold, raise_value=False,
                        min_threshold=False),
        height=2, width=6)
    pressure_decrease_max_threshold_button.pack(fill="both", expand=True)
    # Pressure Graph
    pressure_figure = Figure(figsize=(5, 2), dpi=100)
    pressure_axis = pressure_figure.add_subplot(111, label="pressure")
    pressure_axis.set_ylabel('Pressure [cmH20]')
    pressure_axis.set_xlabel('sec')
    pressure_graph, = pressure_axis.plot(store.x_axis,
                                         store.pressure_display_values)
    pressure_canvas = FigureCanvasTkAgg(pressure_figure,
                                        master=left_pressure_frame)
    pressure_canvas.draw()
    pressure_canvas.get_tk_widget().pack(side='top', fill='both',
                                         expand=1)


def gui_update():
    update_flow_graph()
    update_pressure_graph()
    update_alert()


def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = RotatingFileHandler('inhalator.log', maxBytes=1024 * 100, backupCount=3)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


def main():
    configure_logging()
    root.title("Inhalator")
    root.geometry('800x480')
    flow_sensor = MockSfm3200()
    pressure_sensor = MockHcePressureSensor()
    sampler = Sampler(store, flow_sensor, pressure_sensor, alert)
    render_gui()
# Wait for GUI to render
#     time.sleep(5)

# Calibrate the graphs y-values

    store.pressure_display_values = [0] * 40
    update_pressure_graph()
    store.flow_display_values = [0] * 40
    update_flow_graph()

    sampler.start()

    while True:
        gui_update()
        time.sleep(0.02)

    # mainloop()


if __name__ == '__main__':
    main()
