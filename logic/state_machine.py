import logging
import sys
from collections import deque
from enum import Enum

from data.alerts import AlertCodes
from data.configurations import Configurations
from logic.utils import RunningSlope, RunningAvg, RateMeter, \
    VolumeAccumulator


class VentilationState(Enum):
    Calibration = 0  # State unknown yet
    Inhale = 1  # Air is flowing to the lungs
    Hold = 2  # PIP is maintained
    Exhale = 3  # Pressure is relieved, air flowing out
    PEEP = 4  # Positive low pressure is maintained until next cycle.


class VentilationStateMachine(object):

    NO_BREATH_ALERT_TIME_SECONDS = 12
    PEEP_TO_INHALE_SLOPE = 8
    INHALE_TO_HOLD_SLOPE = 4
    HOLD_TO_EXHALE_SLOPE = -4
    EXHALE_TO_PEEP_SLOPE = -4

    # Transition table:
    # The key is a given current state, and the value is a tuple of:
    # 1. The compare func against the threshold (greater-than, less-than)
    # 2. The threshold to compare against
    # 3. The next state if the comparison evaluates to true.
    #
    # For each new sample we compute the current slope, and according to
    # the current state we perform the appropriate comparison against the
    # appropriate threshold. If the comparison returns True - we transition
    # to the next state according to the table.
    TRANSITION_TABLE = {
        VentilationState.PEEP: (float.__gt__, PEEP_TO_INHALE_SLOPE, VentilationState.Inhale),
        VentilationState.Inhale: (float.__lt__, INHALE_TO_HOLD_SLOPE, VentilationState.Hold),
        VentilationState.Hold: (float.__lt__, HOLD_TO_EXHALE_SLOPE, VentilationState.Exhale),
        VentilationState.Exhale: (float.__gt__, EXHALE_TO_PEEP_SLOPE, VentilationState.PEEP),
    }

    def __init__(self, measurements, events):
        self._measurements = measurements
        self._events = events
        self.log = logging.getLogger(self.__class__.__name__)
        self.rs = RunningSlope(num_samples=7)
        self._config = Configurations.instance()
        self.last_breath_timestamp = None
        self.current_state = VentilationState.PEEP

        # Data structure to record last 100 entry timestamp for each state.
        # Useful for debugging and plotting.
        self.entry_points_ts = {
            VentilationState.PEEP: deque(maxlen=100),
            VentilationState.Inhale: deque(maxlen=100),
            VentilationState.Hold: deque(maxlen=100),
            VentilationState.Exhale: deque(maxlen=100)
        }

        # Function to call when entering a state.
        self.entry_handlers = {
            VentilationState.Inhale: self.enter_inhale,
            VentilationState.Exhale: self.enter_exhale,
            VentilationState.PEEP: self.enter_peep
        }
        self.peak_pressure = 0
        self.min_pressure = sys.maxsize
        self.peak_flow = 0
        # No good reason for 1000 max samples. Sounds enough.
        self.peep_avg_calculator = RunningAvg(max_samples=1000)
        self.breathes_rate_meter = RateMeter(time_span_seconds=60, max_samples=4)
        self.inspiration_volume = VolumeAccumulator()
        self.expiration_volume = VolumeAccumulator()

    def enter_inhale(self, timestamp):
        self.last_breath_timestamp = timestamp
        self._measurements.bpm = self.breathes_rate_meter.beat(timestamp)
        # Update final expiration volume
        exp_volume_ml = self.expiration_volume.air_volume_liter * 1000
        self.log.debug("TV exp: : %sml", exp_volume_ml)
        self._measurements.expiration_volume = exp_volume_ml
        self.expiration_volume.reset()
        self.reset_min_values()

    def enter_exhale(self, timestamp):
        self.reset_peaks()

    def enter_peep(self, timestamp):
        # Update final inspiration volume
        insp_volume_ml = self.inspiration_volume.air_volume_liter * 1000
        self.log.debug("TV insp: : %sml", insp_volume_ml)
        self._measurements.inspiration_volume = insp_volume_ml
        self.inspiration_volume.reset()

        if self._config.volume_range.below(insp_volume_ml):
            self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_LOW, timestamp)
            self.log.warning(
                "volume too low %s, bottom threshold %s",
                insp_volume_ml, self._config.volume_range.min)
        elif self._config.volume_range.over(insp_volume_ml):
            self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_HIGH, timestamp)
            self.log.warning(
                "volume too high %s, top threshold %s",
                insp_volume_ml, self._config.volume_range.max)

    def reset_peaks(self):
        self._measurements.intake_peak_pressure = self.peak_pressure
        self._measurements.intake_peak_flow = self.peak_flow
        self.peak_pressure = 0
        self.peak_flow = 0

    def reset_min_values(self):
        self._measurements.peep_min_pressure = self.min_pressure
        self.min_pressure = sys.maxsize

    def update(self, pressure_cmh2o, flow_slm, o2_saturation_percentage, timestamp):
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
        accumulator.accumulate(timestamp, abs(flow_slm))
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

        self.check_transition(pressure_cmh2o, timestamp)

    def check_transition(self, pressure_cmh2o, timestamp):
        # Now, calculate the current slope of the pressure graph to see in which
        # ventilation state we are.
        slope = self.rs.add_sample(pressure_cmh2o, timestamp)
        if slope is None:
            return  # Not enough data

        func, threshold, next_state = self.TRANSITION_TABLE.get(self.current_state)
        if func(slope, threshold):
            self.rs.reset()  # TODO: Rethink. Maybe not reset?
            self.log.debug("%s -> %s", self.current_state, next_state)
            self.current_state = next_state
            self.entry_points_ts[next_state].append(timestamp)
            entry_handler = self.entry_handlers.get(next_state, None)
            if entry_handler is not None:
                # noinspection PyArgumentList
                entry_handler(timestamp)
