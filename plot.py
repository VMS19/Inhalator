import argparse

import pandas as pd
import matplotlib.pyplot as plt

from algo import VentilationStateMachine, VentilationState
from data.configurations import ConfigurationManager
from data.events import Events
from data.measurements import Measurements
from drivers.mocks.sensor import DifferentialPressureMockSensor
from logic.auto_calibration import TailDetector

TIMESTAMP_COLUMN = "time elapsed (seconds)"
FLOW_COLUMN = "flow"
PRESSURE_COLUMN = "pressure"
OXYGEN_COLUMN = "oxygen"
CONVERTERS = {
    TIMESTAMP_COLUMN: float,
    FLOW_COLUMN: float,
    PRESSURE_COLUMN: float,
    OXYGEN_COLUMN: float
}


def plot_file(file_path, start=0, end=-1):
    df = pd.read_csv(file_path, converters=CONVERTERS)[start:end]
    measurements = Measurements(seconds_in_graph=12)
    events = Events()
    ConfigurationManager.initialize(events)
    vsm = VentilationStateMachine(measurements, events)

    #  define auto calibrator
    tail_detector = TailDetector(
        dp_driver=DifferentialPressureMockSensor([0]),
        sample_threshold=vsm._config.auto_cal_sample_threshold,
        slope_threshold=vsm._config.auto_cal_slope_threshold,
        min_tail_length=vsm._config.auto_cal_min_tail,
        grace_length=vsm._config.auto_cal_grace_length
    )

    # Run the machine
    for index, row in df.iterrows():
        vsm.update(
            pressure_inh2o=row[PRESSURE_COLUMN],
            flow_slm=row[FLOW_COLUMN],
            o2_percentage=row[OXYGEN_COLUMN],
            timestamp=row[TIMESTAMP_COLUMN])
        tail_detector.add_sample(row[FLOW_COLUMN], row[TIMESTAMP_COLUMN])

    tail_detector.process()
    fig, (ax_pressure, ax_flow) = plt.subplots(2, 1, sharex="all")
    draw_pressure(ax_pressure, df[PRESSURE_COLUMN], df[TIMESTAMP_COLUMN], vsm,
                  tail_detector)
    draw_flow(ax_flow, df[FLOW_COLUMN], df[TIMESTAMP_COLUMN], vsm,
              tail_detector)

    mng = plt.get_current_fig_manager()
    if hasattr(mng, "window"):
        window = getattr(mng, "window")
        if hasattr(window, "showMaximized"):
            getattr(window, "showMaximized")()

    plt.show()


def draw_flow(axes, samples, timestamps, vsm, td):
    axes.set_ylabel("Air Flow (L/m)")
    axes.plot(timestamps, samples, "black")
    axes.vlines(
        vsm.entry_points_ts[VentilationState.Inhale],
        ymin=-40, ymax=40, colors="g", linestyle="dashed")
    axes.vlines(
        vsm.entry_points_ts[VentilationState.Exhale],
        ymin=-40, ymax=40, colors="r", linestyle="dashed")
    axes.vlines(td.start_tails_ts,
                ymin=-40, ymax=40, colors="pink", linestyle="dotted")
    axes.vlines(td.end_tails_ts,
                ymin=-40, ymax=40, colors="brown", linestyle="dotted")
    axes.axhline(color="black", linewidth=1)
    where_insp = [s > 0 for s in samples]
    where_exp = [s < 0 for s in samples]
    axes.fill_between(
        timestamps, samples, where=where_insp, facecolor="green")
    axes.fill_between(
        timestamps, samples, where=where_exp,
        facecolor="red")
    for ts, vol in vsm.insp_volumes:
        axes.annotate(f"{round(vol)}ml", (ts, 25), color="green")

    for ts, vol in vsm.exp_volumes:
        axes.annotate(f"{round(vol)}ml", (ts, -25), color="red")


def draw_pressure(axes, samples, timestamp, vsm, td):
    axes.set_ylabel("Pressure (inH2o)")
    axes.plot(timestamp, samples, "black")
    axes.vlines(
        vsm.entry_points_ts[VentilationState.Inhale],
        ymin=0, ymax=30, colors="g", linestyle="dashed")
    axes.vlines(
        vsm.entry_points_ts[VentilationState.Exhale],
        ymin=0, ymax=30, colors="r", linestyle="dashed")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", help="The path to the CSV file")
    parser.add_argument(
        "start_line", default=0, type=int, nargs="?",
        help="Start from this line (not including CSV header)")
    parser.add_argument(
        "end_line", default=-1, type=int, nargs="?",
        help="Read up to this line (not including CSV header)")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    plot_file(file_path=args.csv_path, start=args.start_line, end=args.end_line)
