import sys
import time
import logging
from enum import Enum
from statistics import mean
from collections import deque

from numpy import trapz
from scipy.stats import linregress

from data.alerts import AlertCodes
from data.measurements import Measurements
from data.configurations import Configurations
from sample_storage import SamplesStorage

TRACE = logging.DEBUG - 1
logging.addLevelName(TRACE, 'TRACE')

BYTES_IN_GB = 2 ** 30


class Accumulator(object):
    def __init__(self):
        self.samples = deque()
        self.timestamps = deque()

    def add_sample(self, timestamp, value):
        self.samples.append(value)
        self.timestamps.append(timestamp)

    def integrate(self):
        return trapz(self.samples, x=self.timestamps)

    def reset(self):
        self.samples.clear()
        self.timestamps.clear()


class RunningAvg(object):

    def __init__(self, max_samples):
        self.samples = deque(maxlen=max_samples)

    def reset(self):
        self.samples.clear()

    def process(self, pressure):
        if pressure is not None:
            self.samples.append(pressure)

        if len(self.samples) == 0:
            return 0

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
        self.start_timestamp = time.time()

    def reset(self):
        self.samples.clear()
        self.start_timestamp = time.time()

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
        rate_per_minute = (len(self.samples) - 1) * (60.0 / interval)
        return rate_per_minute

    def is_stable(self):
        has_timespan_passed = \
            time.time() - self.start_timestamp > self.time_span_seconds
        return has_timespan_passed or len(self.samples) >= 2


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
    Inhale = 1  # Air is flowing to the lungs and enough volume
    Hold = 2  # PIP is maintained
    Exhale = 3  # Pressure is relieved, air flowing out and enough volume
    PEEP = 4  # Positive low pressure is maintained until next cycle.
    Sub_inhale = 5  # Air is flowing to the lungs
    Sub_exhale = 6  # Pressure is relieved, air flowing out


class VentilationStateMachine(object):
    NO_BREATH_ALERT_TIME_SECONDS = 12

    def __init__(self, measurements, events):
        self._measurements = measurements
        self._events = events
        self.log = logging.getLogger(self.__class__.__name__)
        self.flow_slope = RunningSlope(num_samples=7)
        self.pressure_slope = RunningSlope(num_samples=7)
        self._config = Configurations.instance()
        self.last_breath_timestamp = None
        self.current_state = VentilationState.PEEP

        # Data structure to record last 100 entry timestamp for each state.
        # Useful for debugging and plotting.
        self.entry_points_ts = {
            VentilationState.Calibration: deque(maxlen=100),
            VentilationState.PEEP: deque(maxlen=100),
            VentilationState.Inhale: deque(maxlen=100),
            VentilationState.Hold: deque(maxlen=100),
            VentilationState.Exhale: deque(maxlen=100),
            VentilationState.Sub_inhale: deque(maxlen=100),
            VentilationState.Sub_exhale: deque(maxlen=100)
        }

        # Function to call when entering a state.
        self.entry_handlers = {
            VentilationState.Inhale: self.enter_inhale,
            VentilationState.Exhale: self.enter_exhale,
            VentilationState.Sub_inhale: self.enter_sub_inhale,
            VentilationState.Sub_exhale: self.enter_sub_exhale,
            VentilationState.PEEP: self.enter_peep
        }
        self.peak_pressure = 0
        self.min_pressure = sys.maxsize
        self.peak_flow = 0
        # No good reason for 1000 max samples. Sounds enough.
        self.peep_avg_calculator = RunningAvg(max_samples=1000)
        self.breathes_rate_meter = RateMeter(time_span_seconds=60,
                                             max_samples=4)
        self.inspiration_volume = Accumulator()
        self.expiration_volume = Accumulator()
        self.insp_volumes = deque(maxlen=100)
        self.exp_volumes = deque(maxlen=100)

    def reset(self):
        # Restart measurements
        self._measurements.reset()
        self.peak_pressure = 0
        self.peak_flow = 0
        self.min_pressure = sys.maxsize

        # Restart volume calculation
        self.inspiration_volume.reset()
        self.expiration_volume.reset()

        # Restart state machine
        print("reset")
        self.current_state = VentilationState.PEEP

    def enter_inhale(self, timestamp, prev_state):
        self.last_breath_timestamp = timestamp
        self._measurements.bpm = self.breathes_rate_meter.beat(timestamp)

        if self.breathes_rate_meter.is_stable():
            # Check bpm thresholds
            if self._config.resp_rate_range.over(self._measurements.bpm):
                self.log.warning(
                    "BPM too high %s, top threshold %s",
                    self._measurements.bpm, self._config.resp_rate_range.max)
                self._events.alerts_queue.enqueue_alert(AlertCodes.BPM_HIGH,
                                                        timestamp)
            elif self._config.resp_rate_range.below(self._measurements.bpm):
                self.log.warning(
                    "BPM too low %s, bottom threshold %s",
                    self._measurements.bpm, self._config.resp_rate_range.min)
                self._events.alerts_queue.enqueue_alert(AlertCodes.BPM_LOW,
                                                        timestamp)

        # # Update final expiration volume
        # exp_volume_ml = self.expiration_volume.integrate() * 1000
        # self.log.debug("TV exp: : %sml", exp_volume_ml)
        # self._measurements.expiration_volume = exp_volume_ml
        # self.expiration_volume.reset()
        # self.exp_volumes.append((timestamp, exp_volume_ml))
        #
        # if self._config.volume_range.below(exp_volume_ml):
        #     self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_LOW, timestamp)
        #     self.log.warning(
        #         "volume too low %s, bottom threshold %s",
        #         exp_volume_ml, self._config.volume_range.min)
        # elif self._config.volume_range.over(exp_volume_ml):
        #     self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_HIGH, timestamp)
        #     self.log.warning(
        #         "volume too high %s, top threshold %s",
        #         exp_volume_ml, self._config.volume_range.max)
        #
        # self.reset_min_values()
        return True

    def enter_exhale(self, timestamp, prev_state):
        # Update final inspiration volume
        # insp_volume_ml = self.inspiration_volume.integrate() * 1000
        # self.log.debug("TV insp: : %sml", insp_volume_ml)
        # self._measurements.inspiration_volume = insp_volume_ml
        # self.inspiration_volume.reset()
        # self.insp_volumes.append((timestamp, insp_volume_ml))
        # self.reset_peaks()
        return True

    def enter_sub_inhale(self, timestamp, prev_state):
        if prev_state == VentilationState.Exhale:
            # Update final expiration volume
            exp_volume_ml = self.expiration_volume.integrate() * 1000
            self.log.debug("TV exp: : %sml", exp_volume_ml)
            self._measurements.expiration_volume = exp_volume_ml
            self.expiration_volume.reset()
            self.exp_volumes.append((timestamp, exp_volume_ml))

            if self._config.volume_range.below(exp_volume_ml):
                self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_LOW,
                                                        timestamp)
                self.log.warning(
                    "volume too low %s, bottom threshold %s",
                    exp_volume_ml, self._config.volume_range.min)
            elif self._config.volume_range.over(exp_volume_ml):
                self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_HIGH,
                                                        timestamp)
                self.log.warning(
                    "volume too high %s, top threshold %s",
                    exp_volume_ml, self._config.volume_range.max)

            self.reset_min_values()

        else:
            insp_volume_ml = self.inspiration_volume.integrate() * 1000
            self.log.debug("TV insp: : %sml", insp_volume_ml)
            self._measurements.inspiration_volume = insp_volume_ml
            self.inspiration_volume.reset()
            self.insp_volumes.append((timestamp, insp_volume_ml))
            self.reset_peaks()

        return True

    def enter_sub_exhale(self, timestamp, prev_state):
        if prev_state == VentilationState.Exhale:
            # Update final expiration volume
            exp_volume_ml = self.expiration_volume.integrate() * 1000
            self.log.debug("TV exp: : %sml", exp_volume_ml)
            self._measurements.expiration_volume = exp_volume_ml
            self.expiration_volume.reset()
            self.exp_volumes.append((timestamp, exp_volume_ml))

            if self._config.volume_range.below(exp_volume_ml):
                self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_LOW,
                                                        timestamp)
                self.log.warning(
                    "volume too low %s, bottom threshold %s",
                    exp_volume_ml, self._config.volume_range.min)
            elif self._config.volume_range.over(exp_volume_ml):
                self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_HIGH,
                                                        timestamp)
                self.log.warning(
                    "volume too high %s, top threshold %s",
                    exp_volume_ml, self._config.volume_range.max)

            self.reset_min_values()

        else:
            insp_volume_ml = self.inspiration_volume.integrate() * 1000
            self.log.debug("TV insp: : %sml", insp_volume_ml)
            self._measurements.inspiration_volume = insp_volume_ml
            self.inspiration_volume.reset()
            self.insp_volumes.append((timestamp, insp_volume_ml))
            self.reset_peaks()
        return True

    def enter_peep(self, timestamp):
        print("etered peep")
        return True

    def reset_peaks(self):
        self._measurements.intake_peak_pressure = self.peak_pressure
        self._measurements.intake_peak_flow = self.peak_flow
        self.peak_pressure = 0
        self.peak_flow = 0

    def reset_min_values(self):
        self._measurements.peep_min_pressure = self.min_pressure
        self.min_pressure = sys.maxsize

    def update(self, pressure_cmh2o, flow_slm, o2_percentage, timestamp):
        if self.last_breath_timestamp is None:
            # First time initialization. Not done in __init__ to avoid reading
            # the time in this class, which improves its testability.
            self.last_breath_timestamp = timestamp
        # First - check how long it was since last breath
        seconds_from_last_breath = timestamp - self.last_breath_timestamp
        if seconds_from_last_breath >= self.NO_BREATH_ALERT_TIME_SECONDS:
            self.log.warning("No breath detected for the last 12 seconds")
            self._events.alerts_queue.enqueue_alert(AlertCodes.NO_BREATH,
                                                    timestamp)
            self.last_breath_timestamp = None
            self.reset()

        # We track inhale and exhale volume separately. Positive flow means
        # inhale, and negative flow means exhale.
        accumulator = self.inspiration_volume if flow_slm > 0 else self.expiration_volume
        # flow is measured in Liter/minute, so we convert it to liter/seconds
        # because this is our time unit
        accumulator.add_sample(timestamp, abs(flow_slm) / 60)
        self._measurements.set_pressure_value(pressure_cmh2o)
        self._measurements.set_flow_value(flow_slm)
        self._measurements.set_saturation_percentage(o2_percentage)

        # Update peak pressure/flow values
        self.peak_pressure = max(self.peak_pressure, pressure_cmh2o)
        self.min_pressure = min(self.min_pressure, pressure_cmh2o)
        self.peak_flow = max(self.peak_flow, flow_slm)

        # Publish alerts for Pressure
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

        # Publish alerts for Oxygen
        # Oxygen too high
        if self._config.o2_range.over(o2_percentage):
            self.log.warning(
                f"Oxygen percentage too high "
                f"({o2_percentage}% > {self._config.o2_range.max}%)")
            self._events.alerts_queue.enqueue_alert(
                AlertCodes.OXYGEN_HIGH, timestamp)

            # Oxygen too low
        elif self._config.o2_range.below(o2_percentage):
            # self.log.warning(
            #     f"Oxygen percentage too low "
            #     f"({o2_percentage}% < {self._config.o2_range.min}%)")
            self._events.alerts_queue.enqueue_alert(
                AlertCodes.OXYGEN_LOW, timestamp)

        self.check_transition(
            flow_slm=flow_slm,
            pressure_cmh2o=pressure_cmh2o,
            timestamp=timestamp)

    def check_transition(self, flow_slm, pressure_cmh2o, timestamp):
        pressure_slope = self.pressure_slope.add_sample(pressure_cmh2o, timestamp)
        flow_slop = self.flow_slope.add_sample(flow_slm, timestamp)
        if flow_slop is None or pressure_slope is None:
            return  # Not enough data

        next_state = self.infer_state(flow_slop, flow_slm, pressure_slope, pressure_cmh2o)
        print(timestamp - 11428.99634, self.current_state, next_state)
        if next_state != self.current_state:
            entry_handler = self.entry_handlers.get(next_state, None)
            # noinspection PyArgumentList
            if entry_handler(timestamp, self.current_state):
                self.current_state = next_state
                self.entry_points_ts[next_state].append(timestamp)
                self.log.debug("%s -> %s", self.current_state, next_state)

    def infer_state(self, flow_slope, flow_slm, pressure_slope, pressure_cmh2o):
        flow_positive_increasing = flow_slope > 3 and flow_slm > 2
        flow_negative_decreasing = flow_slope < -10 and flow_slm < -2
        print('\t',self.inspiration_volume.integrate() * 1000,
              self.expiration_volume.integrate() * 1000,
              flow_negative_decreasing and pressure_slope < self._config.max_pressure_slope_for_exhale,
              flow_positive_increasing and pressure_slope > self._config.min_pressure_slope_for_inhale)
        print('\t\t', flow_slope, pressure_slope)

        #  currently at a sub state
        if self.current_state == VentilationState.Sub_inhale:
            insp_volume = self.inspiration_volume.integrate() * 1000
            if insp_volume >= self._config.min_insp_volume_for_inhale:
                return VentilationState.Inhale

            elif flow_negative_decreasing and pressure_slope < self._config.max_pressure_slope_for_exhale:
                return VentilationState.Sub_exhale

        if self.current_state == VentilationState.Sub_exhale:
            exp_volume = self.expiration_volume.integrate() * 1000
            if exp_volume >= self._config.min_exp_volume_for_exhale:
                return VentilationState.Exhale

            elif flow_positive_increasing and pressure_slope > self._config.min_pressure_slope_for_inhale:
                return VentilationState.Sub_inhale

        #  currently at a inhale\exhale state
        if self.current_state != VentilationState.Exhale:
            if flow_negative_decreasing and pressure_slope < self._config.max_pressure_slope_for_exhale:
                return VentilationState.Sub_exhale

        if self.current_state != VentilationState.Inhale:
            if flow_positive_increasing and pressure_slope > self._config.min_pressure_slope_for_inhale:
                return VentilationState.Sub_inhale

        return self.current_state


class Sampler(object):

    def __init__(self, measurements, events, flow_sensor, pressure_sensor,
                 a2d, timer, average_window, save_sensor_values=False):
        super(Sampler, self).__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self._measurements = measurements  # type: Measurements
        self._flow_sensor = flow_sensor
        self._pressure_sensor = pressure_sensor
        self._a2d = a2d
        self._timer = timer
        self._config = Configurations.instance()
        self._events = events
        self.vsm = VentilationStateMachine(measurements, events)
        self.storage_handler = SamplesStorage()
        self.save_sensor_values = save_sensor_values
        self.flow_avg = RunningAvg(average_window)

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

        flow_avg_sample = self.flow_avg.process(flow_slm)

        pressure_cmh2o = self.read_single_sensor(
            self._pressure_sensor, AlertCodes.PRESSURE_SENSOR_ERROR, timestamp)

        try:
            o2_saturation_percentage = self._a2d.read_oxygen()
        except Exception as e:
            self._events.alerts_queue.enqueue_alert(AlertCodes.OXYGEN_SENSOR_ERROR)
            self.log.error(e)
            o2_saturation_percentage = 0

        try:
            battery_exists = self._a2d.read_battery_existence()
            if not battery_exists:
                self._events.alerts_queue.enqueue_alert(
                    AlertCodes.NO_BATTERY, timestamp
                )
        except Exception as e:
            self._events.alerts_queue.enqueue_alert(AlertCodes.NO_BATTERY, timestamp)
            self.log.error(e)

        try:
            battery_percentage = self._a2d.read_battery_percentage()
            self._measurements.set_battery_percentage(battery_percentage)
        except Exception as e:
            self._events.alerts_queue.enqueue_alert(AlertCodes.NO_BATTERY, timestamp)
            self.log.error(e)

        data = (flow_avg_sample, pressure_cmh2o, o2_saturation_percentage)
        return [x if x is not None else 0 for x in data]

    def sampling_iteration(self):
        ts = self._timer.get_time()

        # Read from sensors
        result = self.read_sensors(ts)
        flow_slm, pressure_cmh2o, o2_saturation_percentage = result

        if self.save_sensor_values:
            self.storage_handler.write(flow=flow_slm,
                                       pressure=pressure_cmh2o,
                                       oxygen=o2_saturation_percentage,
                                       pip=self._measurements.intake_peak_pressure,
                                       peep=self._measurements.peep_min_pressure,
                                       tv_insp=self._measurements.inspiration_volume,
                                       tv_exp=self._measurements.expiration_volume,
                                       bpm=self._measurements.bpm,
                                       ts=ts)

        self.vsm.update(
            pressure_cmh2o=pressure_cmh2o,
            flow_slm=flow_slm,
            o2_percentage=o2_saturation_percentage,
            timestamp=ts,
        )
