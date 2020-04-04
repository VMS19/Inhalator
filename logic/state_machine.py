import logging
import sys
from collections import deque
from enum import Enum

from data.alerts import AlertCodes
from data.configurations import Configurations
from logic.utils import RunningSlope, RunningAvg, RateMeter, \
    VolumeAccumulator

class VentilationStateMachine(object):

    NO_BREATH_ALERT_TIME_SECONDS = 12
    EPSILON = 0.1  # 100 mL

    def __init__(self, measurements, events):
        self._measurements = measurements
        self._events = events
        self.log = logging.getLogger(self.__class__.__name__)
        self._config = Configurations.instance()
        self.last_breath_timestamp = None

        self.peak_pressure = 0
        self.min_pressure = sys.maxsize
        self.peak_flow = 0

        # No good reason for 1000 max samples. Sounds enough.
        self.peep_avg_calculator = RunningAvg(max_samples=1000)
        self.breathes_rate_meter = RateMeter(time_span_seconds=60, max_samples=4)
        self.inspiration_volume = VolumeAccumulator()
        self.expiration_volume = VolumeAccumulator()

        self.last_flow_sample = 0
        self.flow_sample = 0

    def check_volume_thresholds(self, timestamp):
        if self._config.volume_range.below(self._measurements.inspiration_volume):
            self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_LOW, timestamp)
            self.log.warning(
                "volume too low %s, bottom threshold %s",
                self._measurements.inspiration_volume, self._config.volume_range.min)
        elif self._config.volume_range.over(self._measurements.inspiration_volume):
            self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_HIGH, timestamp)
            self.log.warning(
                "volume too high %s, top threshold %s",
                self._measurements.inspiration_volume, self._config.volume_range.max)

    def reset_peaks(self):
        self._measurements.intake_peak_pressure = self.peak_pressure
        self._measurements.intake_peak_flow = self.peak_flow
        self.peak_pressure = 0
        self.peak_flow = 0

    def reset_min_values(self):
        self._measurements.peep_min_pressure = self.min_pressure
        self.min_pressure = sys.maxsize

    def finish_breath_cycle(self, timestamp):
        self.last_breath_timestamp = timestamp
        self._measurements.bpm = self.breathes_rate_meter.beat(timestamp)
        # Update final expiration
        exp_volume_ml = self.expiration_volume.air_volume_liter * 1000
        insp_volume_ml = self.inspiration_volume.air_volume_liter * 1000
        self.log.debug("TV exp: : %sml", exp_volume_ml)
        self.log.debug("TV insp: : %sml", insp_volume_ml)
        self._measurements.expiration_volume = exp_volume_ml
        self._measurements.inspiration_volume = insp_volume_ml
        self.expiration_volume.reset()
        self.inspiration_volume.reset()

        self.check_volume_thresholds(timestamp)
        self.reset_peaks()
        self.reset_min_values()

    def is_breath_cycle_finished(self):
        minimal_insp_volume = self.inspiration_volume.air_volume_liter > self.EPSILON
        minimal_exp_volume = self.expiration_volume.air_volume_liter > self.EPSILON
        return (minimal_insp_volume and minimal_exp_volume and
                        self.last_flow_sample <= 0 < self.flow_sample)

    def update(self, pressure_cmh2o, flow_slm, o2_saturation_percentage, timestamp):
        self.last_flow_sample = self.flow_sample
        self.flow_sample = flow_slm

        if self.last_breath_timestamp is None:
            # First time initialization. Not done in __init__ to avoid reading
            # the time in this class, which improves its testability.
            self.last_breath_timestamp = timestamp

        # First - check how long it was since last breath
        seconds_from_last_breath = timestamp - self.last_breath_timestamp
        if seconds_from_last_breath >= self.NO_BREATH_ALERT_TIME_SECONDS:
            self.log.warning("No breath detected for the last 12 seconds")
            self._events.alerts_queue.enqueue_alert(AlertCodes.NO_BREATH, timestamp)

        # We track inhale and exhale volume separately. Positive flow means
        # inhale, and negative flow means exhale.
        accumulator = self.inspiration_volume if flow_slm > 0 else self.expiration_volume
        accumulator.accumulate(timestamp, abs(flow_slm),
                               abs(self.last_flow_sample))

        self._measurements.set_pressure_value(pressure_cmh2o)
        self._measurements.set_flow_value(flow_slm)
        self._measurements.set_saturation_percentage(o2_saturation_percentage)

        # Update peak pressure/flow values
        self.peak_pressure = max(self.peak_pressure, pressure_cmh2o)
        self.min_pressure = min(self.min_pressure, pressure_cmh2o)
        self.peak_flow = max(self.peak_flow, flow_slm)

        if self._config.pressure_range.over(pressure_cmh2o):
            self.log.warning(
                "pressure too high %s, top threshold %s",
                pressure_cmh2o, self._config.pressure_range.max)
            self._events.alerts_queue.enqueue_alert(AlertCodes.PRESSURE_HIGH, timestamp)
        elif self._config.pressure_range.below(pressure_cmh2o):
            self.log.warning(
                "pressure too low %s, bottom threshold %s",
                pressure_cmh2o, self._config.pressure_range.min)
            self._events.alerts_queue.enqueue_alert(AlertCodes.PRESSURE_LOW, timestamp)

        if self.is_breath_cycle_finished():
            self.finish_breath_cycle(timestamp)
            self._measurements.set_state_value(40)
        else:
            self._measurements.set_state_value(-40)

