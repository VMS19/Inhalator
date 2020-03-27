import time
import logging
import threading
from enum import Enum
from statistics import mean

from data.alerts import AlertCodes
from data.measurements import Measurements
from data.configurations import Configurations


class VolumeAccumulator(object):
    def __init__(self):
        self.air_volume_liter = 0
        self.last_sample_ts = None

    def accumulate(self, timestamp, air_flow):
        if self.last_sample_ts is not None:
            elapsed_time_seconds = timestamp - self.last_sample_ts
            elapsed_time_minutes = elapsed_time_seconds / 60
            # flow is measured in Liter/minute, so we multiply the last read by
            # the time elapsed in minutes to calculate the accumulated volume
            # inhaled in this inhale.
            self.air_volume_liter += air_flow * elapsed_time_minutes
        self.last_sample_ts = timestamp

    def reset(self):
        self.air_volume_liter = 0
        self.last_sample_ts = None


class RunningAvg(object):

    def __init__(self):
        self.samples = []

    def reset(self):
        self.samples = []

    def process(self, pressure):
        self.samples.append(pressure)
        return mean(self.samples)


class VentilationState(Enum):
    Inhale = 0
    Exhale = 1
    PEEP = 2


class Sampler(threading.Thread):
    SAMPLING_INTERVAL = 0.02  # sec
    MS_IN_MIN = 60 * 1000
    ML_IN_LITER = 1000

    def __init__(self, measurements, events, flow_sensor, pressure_sensor):
        super(Sampler, self).__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.daemon = True
        self._measurements = measurements  # type: Measurements
        self._flow_sensor = flow_sensor
        self._pressure_sensor = pressure_sensor
        self._config = Configurations.instance()
        self._events = events
        self.accumulator = VolumeAccumulator()
        self.peep_avg_calculator = RunningAvg()
        self.alerts = AlertCodes.OK

        # State
        self.handlers = {
            VentilationState.Inhale: self.handle_inhale,
            VentilationState.Exhale: self.handle_exhale,
            VentilationState.PEEP: self.handle_peep
        }

        self.current_state = VentilationState.Inhale  # Initial Value
        self.last_pressure = 0
        self._inhale_max_flow = 0
        self._inhale_max_pressure = 0
        self._has_crossed_first_cycle = False
        self._is_during_intake = False
        self._last_inhale_ts = 0

    def handle_inhale(self, flow_slm, pressure):
        if pressure <= self.last_pressure:
            self.log.debug("Inhale volume: %s" % self.accumulator.air_volume_liter)
            self._inhale_finished()

        ts = time.time()
        self.accumulator.accumulate(ts, flow_slm)

        if (self._config.volume_threshold.max != 'off' and
                self.accumulator.air_volume_liter >
                self._config.volume_threshold.max):
            self.alerts |= AlertCodes.VOLUME_HIGH

        if pressure <= self._config.breathing_threshold:
            self._has_crossed_first_cycle = True

        self._inhale_max_pressure = max(pressure, self._inhale_max_pressure)
        self._inhale_max_flow = max(flow_slm, self._inhale_max_flow)

    def _inhale_finished(self):
        self.log.debug("Inhale finished. Exhale starts")
        ts = time.time()
        self._config.bpm = 1.0 / (ts - self._last_inhale_ts) * 60
        self._last_inhale_ts = ts
        if (self._config.volume_threshold != "off" and
                self.accumulator.air_volume_liter <
                self._config.volume_threshold.min and
                self._has_crossed_first_cycle):

            self.alerts |= AlertCodes.VOLUME_LOW

        self._measurements.set_intake_peaks(self._inhale_max_pressure,
                                            self._inhale_max_pressure,
                                            self.accumulator.air_volume_liter)
        # reset values of last intake
        self.accumulator.reset()
        self._inhale_max_flow = 0
        self._inhale_max_pressure = 0
        self.current_state = VentilationState.Exhale

    def handle_exhale(self, flow, pressure):
        if pressure < self._config.breathing_threshold:
            self.current_state = VentilationState.PEEP

    def handle_peep(self, flow, pressure):
        # peep_avg = self.peep_avg_calculator.process(pressure)
        if pressure > self._config.breathing_threshold:
            # self.log.debug("Last PEEP: %s", peep_avg)
            self.current_state = VentilationState.Inhale

    def run(self):
        while True:
            self.sampling_iteration()
            time.sleep(self.SAMPLING_INTERVAL)

    def sampling_iteration(self):
        # Read from sensors
        flow_slm = self._flow_sensor.read()
        pressure_cmh2o = self._pressure_sensor.read()

        handler = self.handlers.get(self.current_state)
        handler(flow_slm, pressure_cmh2o)
        self._measurements.set_pressure_value(pressure_cmh2o)

        if self._config.pressure_threshold.max != "off" and \
                pressure_cmh2o > self._config.pressure_threshold.max:
            # Above healthy lungs pressure
            self.alerts |= AlertCodes.PRESSURE_HIGH

        if self._config.pressure_threshold.max != "off" and \
                pressure_cmh2o < self._config.pressure_threshold.min:
            # Below healthy lungs pressure
            self.alerts |= AlertCodes.PRESSURE_LOW

        self._measurements.set_flow_value(flow_slm)

        if (self.alerts != AlertCodes.OK and
                self._events.alerts_queue.last_alert != self.alerts):
            self._events.alerts_queue.enqueue_alert(self.alerts)
        self.last_pressure = pressure_cmh2o
