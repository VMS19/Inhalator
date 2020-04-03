import csv
import sys
from collections import deque

import matplotlib.pyplot as plt

from algo import VentilationStateMachine, VentilationState
from data.events import Events
from data.measurements import Measurements


def plot_file(file_path):
    with open(file_path, "r") as f:
        r = csv.DictReader(f)
        data = list(r)
    time_series = [float(d["time_elapsed_sec"]) for d in data]
    pressure = [float(d["pressure"]) for d in data]
    flow = [float(d["flow"]) for d in data]
    measurements = Measurements()
    events = Events()
    vsm = VentilationStateMachine(measurements, events)

    # Run the machine
    for ti, pi, fi in zip(time_series, pressure, flow):
        vsm.update(pi, fi, 0, ti)

    fig, (ax_pressure, ax_flow) = plt.subplots(2, 1, sharex="all")
    draw_pressure(ax_pressure, pressure, time_series, vsm)
    draw_flow(ax_flow, flow, time_series, vsm)

    mng = plt.get_current_fig_manager()
    if hasattr(mng, "window"):
        window = mng.window
        if hasattr(window, "showMaximized"):
            window.showMaximized()

    plt.show()


def draw_flow(axes, samples, timestamps, vsm):
    axes.set_ylabel("Air Flow (L/m)")
    axes.plot(timestamps, samples, "black")
    axes.vlines(
        vsm.entry_points_ts[VentilationState.Inhale],
        ymin=-40, ymax=40, colors="g", linestyle="dashed")
    axes.vlines(
        vsm.entry_points_ts[VentilationState.Exhale],
        ymin=-40, ymax=40, colors="r", linestyle="dashed")
    axes.axhline(color="black", linewidth=1)
    where_insp = make_where_x(timestamps, vsm.insp_flows)
    where_exp = make_where_x(timestamps, vsm.exp_flows)
    axes.fill_between(
        timestamps, samples, where=where_insp, facecolor="green")
    axes.fill_between(
        timestamps, samples, where=where_exp,
        facecolor="red")
    for ts, vol in vsm.insp_volumes:
        axes.annotate(f"{round(vol)}ml", (ts, 25), color="green")

    for ts, vol in vsm.exp_volumes:
        axes.annotate(f"{round(vol)}ml", (ts, -25), color="red")


def draw_pressure(axes, samples, timestamp, vsm):
    axes.set_ylabel("Pressure (cmH2O)")
    axes.plot(timestamp, samples, "black")
    axes.vlines(
        vsm.entry_points_ts[VentilationState.Inhale],
        ymin=0, ymax=30, colors="g", linestyle="dashed")
    axes.vlines(
        vsm.entry_points_ts[VentilationState.Exhale],
        ymin=0, ymax=30, colors="r", linestyle="dashed")


def make_where_x(timestamps, markers):
    res = []
    markers = deque(markers)
    for ts in timestamps:
        if markers and ts == markers[0]:
            res.append(True)
            markers.popleft()
        else:
            res.append(False)
    return res


if __name__ == '__main__':
    plot_file(sys.argv[1])
