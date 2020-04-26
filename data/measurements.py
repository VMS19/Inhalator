from collections import deque
from threading import Lock

from data.configurations import Configurations


class Measurements(object):
    def __init__(self, sample_rate=22):
        self.inspiration_volume = 0
        self.expiration_volume = 0
        self.avg_insp_volume = 0
        self.avg_exp_volume = 0
        self.sample_interval = 1 / sample_rate
        self.init_samples_queues(0)
        self.x_axis = range(0, self.samples_in_graph)
        self.intake_peak_flow = 0
        self.intake_peak_pressure = 0
        self.peep_min_pressure = 0
        self.bpm = 0
        self.o2_saturation_percentage = 20
        self.battery_percentage = 0
        self.lock = Lock()

    def init_samples_queues(self, init_value, size=0):
        self.flow_measurements = deque([init_value] * size,
                                       maxlen=self.samples_in_graph)
        self.pressure_measurements = deque([init_value] * size,
                                           maxlen=self.samples_in_graph)

    def reset(self):
        self.inspiration_volume = 0
        self.expiration_volume = 0
        self.avg_insp_volume = 0
        self.avg_exp_volume = 0
        self.intake_peak_flow = 0
        self.intake_peak_pressure = 0
        self.peep_min_pressure = 0
        self.bpm = 0

    def set_flow_value(self, new_value):
        with self.lock:
            self.flow_measurements.append(new_value)

    def set_pressure_value(self, new_value):
        with self.lock:
            self.pressure_measurements.append(new_value)

    def get_flow_value(self):
        with self.lock:
            return (self.flow_measurements[-2], self.flow_measurements[-1])

    def get_pressure_value(self):
        with self.lock:
            return (self.pressure_measurements[-2], self.pressure_measurements[-1])

    def set_intake_peaks(self, flow, pressure, volume):
        self.intake_peak_flow = flow
        self.intake_peak_pressure = pressure
        self.inspiration_volume = volume

    def set_saturation_percentage(self, o2_saturation_percentage):
        self.o2_saturation_percentage = o2_saturation_percentage

    def set_battery_percentage(self, percentage):
        self.battery_percentage = percentage

    @property
    def samples_in_graph(self):
        config = Configurations.instance()
        return int(config.graph_seconds / self.sample_interval)
