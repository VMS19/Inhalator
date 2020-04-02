import sys
import time
import logging
from enum import Enum
from statistics import mean
from collections import deque

from scipy.stats import linregress

from data.alerts import AlertCodes
from data.measurements import Measurements
from data.configurations import Configurations

TRACE = logging.DEBUG - 1
logging.addLevelName(TRACE, 'TRACE')


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

    def __init__(self, max_samples):
        self.samples = deque(maxlen=max_samples)

    def reset(self):
        self.samples.clear()

    def process(self, pressure):
        self.samples.append(pressure)
        return mean(self.samples)


class RateMeter(object):

    def __init__(self, time_span_seconds, max_samples):
        """
        :param time_span_seconds: How long (seconds) the sliding window of the
            running average should be
        """
        if time_span_seconds <= 0:
            raise ValueError("Time span must be non-zero and positive")
        self.time_span_seconds = time_span_seconds
        self.samples = deque(maxlen=max_samples)

    def reset(self):
        self.samples.clear()

    def beat(self, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        self.samples.append(timestamp)
        # Discard beats older than `self.time_span_seconds`
        while self.samples[0] < (timestamp - self.time_span_seconds):
            self.samples.popleft()

        # Basically the rate is the number of elements left, since the container
        # represents only the relevant time span.
        # BUT there is a corner-case at the beginning of the process - what if
        # we did not yet passed a single time span? The rate then will be
        # artificially low. For example on the first two beats, even if there
        # are only 10 seconds between them and the time span is 60 seconds, the
        # rate will be 2/min, instead of 6/min (1 beats every 10 seconds).
        # This is why we compute the interval between the oldest and newest beat
        # in the data, and calculate the rate based on it. After we accumulate
        # enough data, this interval will be pretty close to the desired span.
        oldest = self.samples[0]
        interval = timestamp - oldest
        # protect against division by zero
        if interval == 0:
            # Technically rate is infinity, but 0 will be more descriptive
            return 0

        # We subtract 1 because we have both 1st and last sentinels.
        rate = (len(self.samples) - 1) * (self.time_span_seconds / interval)
        return rate


class RunningSlope(object):

    def __init__(self, num_samples=10, period_ms=100):
        self.period_ms = period_ms
        self.max_samples = num_samples
        self.data = deque(maxlen=num_samples)
        self.ts = deque(maxlen=num_samples)

    def reset(self):
        self.data.clear()
        self.ts.clear()

    def add_sample(self, value, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        self.data.append(value)
        self.ts.append(timestamp)
        if len(self.data) < self.max_samples:
            return None  # Not enough data to infer.
        slope, _, _, _, _ = linregress(self.ts, self.data)
        return slope


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
        self.last_breath_timestamp = time.time()
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


class Sampler(object):

    def __init__(self, measurements, events, flow_sensor, pressure_sensor, oxygen_a2d):
        super(Sampler, self).__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self._measurements = measurements  # type: Measurements
        self._flow_sensor = flow_sensor
        self._pressure_sensor = pressure_sensor
        self._oxygen_a2d = oxygen_a2d
        self._config = Configurations.instance()
        self._events = events
        self.vsm = VentilationStateMachine(measurements, events)

    def read_single_sensor(self, sensor, alert_code, timestamp):
        try:
            return sensor.read()
        except Exception as e:
            self._events.alerts_queue.enqueue_alert(alert_code, timestamp)
            self.log.error(e)
        return None

    def read_sensors(self, timestamp):
        """
        Read the sensors and return the samples.

        We try to read all of the sensors even in case of error in order to
        better understand the nature of the problem - Is it a single sensor that
        failed, or maybe something wrong with out bus for example.
        :return: Tuple of (flow, pressure, saturation) if there are no errors,
                or None if an error occurred in any of the drivers.
        """
        flow_slm = self.read_single_sensor(
            self._flow_sensor, AlertCodes.FLOW_SENSOR_ERROR, timestamp)
        pressure_cmh2o = self.read_single_sensor(
            self._pressure_sensor, AlertCodes.PRESSURE_SENSOR_ERROR, timestamp)
        o2_saturation_percentage = self.read_single_sensor(
            self._oxygen_a2d, AlertCodes.SATURATION_SENSOR_ERROR, timestamp)

        data = (flow_slm, pressure_cmh2o, o2_saturation_percentage)
        errors = [x is None for x in data]
        return None if any(errors) else data

    def sampling_iteration(self):
        ts = time.time()
        # Read from sensors
        result = self.read_sensors(ts)
        if result is None:
            return

        flow_slm, pressure_cmh2o, o2_saturation_percentage = result
        # WARNING! These log messages are useful for debugging sensors but
        # might spam you since they are printed on every sample. In order to see
        # them run the application in maximum verbosity mode by passing `-vvv` to `main.py
        self.log.log(TRACE, 'flow: %s', flow_slm)
        self.log.log(TRACE, 'pressure: %s', pressure_cmh2o)
        self.log.log(TRACE, 'oxygen: %s', o2_saturation_percentage)

        self.vsm.update(
            pressure_cmh2o=pressure_cmh2o,
            flow_slm=flow_slm,
            o2_saturation_percentage=o2_saturation_percentage,
            timestamp=ts)