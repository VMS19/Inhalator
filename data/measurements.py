from queue import Queue
from threading import Lock


class Measurements(object):
    def __init__(self, seconds_in_graph=12, sample_rate=22):
        self._seconds_in_graph = seconds_in_graph
        self.sample_rate = sample_rate
        self.inspiration_volume = 0
        self.expiration_volume = 0
        self.avg_insp_volume = 0
        self.avg_exp_volume = 0
        self.flow_measurements = Queue(maxsize=4000)  # TODO: Rename?
        self.pressure_measurements = Queue(maxsize=40)  # TODO: Rename?
        self.x_axis = range(0, self.max_samples)
        self.intake_peak_flow = 0
        self.intake_peak_pressure = 0
        self.peep_min_pressure = 0
        self.bpm = 0
        self.o2_saturation_percentage = 20
        self.battery_percentage = 0
        self.lock = Lock()

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
            # pop last item if queue is full
            if self.flow_measurements.full():
                self.flow_measurements.get()
            self.flow_measurements.put(new_value)

    def set_pressure_value(self, new_value):
        with self.lock:
            # pop last item if queue is full
            if self.pressure_measurements.full():
                self.pressure_measurements.get()
            self.pressure_measurements.put(new_value)

    def get_flow_value(self, new_value):
        with self.lock:
            self.flow_measurements.get(new_value)

    def get_pressure_value(self, new_value):
        with self.lock:
            self.pressure_measurements.get(new_value)

    def set_intake_peaks(self, flow, pressure, volume):
        self.intake_peak_flow = flow
        self.intake_peak_pressure = pressure
        self.inspiration_volume = volume

    def set_saturation_percentage(self, o2_saturation_percentage):
        self.o2_saturation_percentage = o2_saturation_percentage

    def set_battery_percentage(self, percentage):
        self.battery_percentage = percentage

    @property
    def max_samples(self):
        return 4000
        return int(self._seconds_in_graph * self.sample_rate)
