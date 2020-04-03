import csv
import sys

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

    for ti, pi, fi in zip(time_series, pressure, flow):
        vsm.update(pi, fi, 0, ti)

    fig, (ax_pressure, ax_flow) = plt.subplots(2, 1, sharex="all")
    ax_pressure.set_ylabel("Pressure (cmH2O)")
    ax_pressure.plot(time_series, pressure, "black")
    ax_pressure.vlines(
        vsm.entry_points_ts[VentilationState.Inhale],
        ymin=0, ymax=30, colors="g", linestyle="dashed")
    ax_pressure.vlines(
        vsm.entry_points_ts[VentilationState.Exhale],
        ymin=0, ymax=30, colors="r", linestyle="dashed")

    ax_flow.set_ylabel("Air Flow (L/m)")
    ax_flow.plot(time_series, flow, "black")
    ax_flow.vlines(
        vsm.entry_points_ts[VentilationState.Inhale],
        ymin=-40, ymax=40, colors="g", linestyle="dashed")
    ax_flow.vlines(
        vsm.entry_points_ts[VentilationState.Exhale],
        ymin=-40, ymax=40, colors="r", linestyle="dashed")
    ax_flow.axhline(color="black", linewidth=1)
    ax_flow.fill_between(time_series, flow, where=[f >= 0 for f in flow], facecolor="green")
    ax_flow.fill_between(time_series, flow, where=[f < 0 for f in flow], facecolor="red")

    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()
    plt.show()


if __name__ == '__main__':
    plot_file(sys.argv[1])
