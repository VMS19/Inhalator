import sys
import time
import logging
from enum import Enum
from collections import deque

from data.alerts import AlertCodes
from data.configurations import ConfigurationManager
from sample_storage import SamplesStorage
from errors import UnavailableMeasurmentError
from logic.auto_calibration import AutoFlowCalibrator
from logic.computations import RunningAvg, Accumulator, RunningSlope

TRACE = logging.DEBUG - 1
logging.addLevelName(TRACE, 'TRACE')

BYTES_IN_GB = 2 ** 30


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


class VentilationState(Enum):
    Unknown = 0  # State unknown yet
    Inhale = 1  # Air is flowing to the lungs
    Hold = 2  # PIP is maintained
    PreExhale = 3  # Pressure is relieved
    Exhale = 4  # Pressure is relieved, air flowing out
    PEEP = 5  # Positive low pressure is maintained until next cycle.
    PreInhale = 6  # Pressure is accumulated


class VentilationStateMachine(object):
    TELEMETRY_REPORT_MAX_INTERVAL_SEC = 5
    NO_BREATH_ALERT_TIME_SECONDS = 12

    def __init__(self, measurements, events, telemetry_sender=None):
        self._measurements = measurements
        self._events = events
        self.telemetry_sender = telemetry_sender
        self.log = logging.getLogger(self.__class__.__name__)
        self.flow_slope = RunningSlope(num_samples=7)
        self.pressure_slope = RunningSlope(num_samples=7)
        self._config = ConfigurationManager.config()
        self.last_breath_timestamp = None
        self.last_telemetry_report = None
        self.last_state = None
        self.current_state = VentilationState.PEEP

        # Data structure to record last 100 entry timestamp for each state.
        # Useful for debugging and plotting.
        self.entry_points_ts = {
            VentilationState.Unknown: deque(maxlen=100),
            VentilationState.PEEP: deque(maxlen=100),
            VentilationState.Inhale: deque(maxlen=100),
            VentilationState.Hold: deque(maxlen=100),
            VentilationState.Exhale: deque(maxlen=100),
            VentilationState.PreInhale: deque(maxlen=100),
            VentilationState.PreExhale: deque(maxlen=100),
        }

        # Function to call when entering a state.
        self.entry_handlers = {
            VentilationState.Inhale: self.enter_inhale,
            VentilationState.Exhale: self.enter_exhale,
            VentilationState.PreInhale: self.enter_pre_inhale,
            VentilationState.PreExhale: self.enter_pre_exhale,
            VentilationState.PEEP: self.enter_peep,
        }
        self.exit_handlers = {
            VentilationState.Inhale: self.exit_inhale,
            VentilationState.Exhale: self.exit_exhale,
            VentilationState.PreInhale: self.exit_pre_inhale,
            VentilationState.PreExhale: self.exit_pre_exhale,
            VentilationState.PEEP: self.exit_peep,
        }
        self.peak_pressure = 0
        self.min_pressure = sys.maxsize
        self.peak_flow = 0
        self.breathes_rate_meter = RateMeter(time_span_seconds=60,
                                             max_samples=4)
        self.inspiration_volume = Accumulator()
        self.expiration_volume = Accumulator()
        self.avg_exp_volume = RunningAvg(max_samples=4)
        self.avg_insp_volume = RunningAvg(max_samples=4)
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
        self.last_state = None
        self.current_state = VentilationState.PEEP

    def enter_inhale(self, timestamp):
        if self.last_state == VentilationState.Inhale:
            self.inspiration_volume.reset()
            return

        self.last_state = VentilationState.Inhale
        self.last_breath_timestamp = timestamp
        self._measurements.bpm = self.breathes_rate_meter.beat(timestamp)

        if self.breathes_rate_meter.is_stable():
            # Check bpm thresholds
            if self._config.thresholds.respiratory_rate.over(self._measurements.bpm):
                self.log.warning(
                    "BPM too high %s, top threshold %s",
                    self._measurements.bpm, self._config.thresholds.respiratory_rate.max)
                self._events.alerts_queue.enqueue_alert(AlertCodes.BPM_HIGH,
                                                        timestamp)
            elif self._config.thresholds.respiratory_rate.below(self._measurements.bpm):
                self.log.warning(
                    "BPM too low %s, bottom threshold %s",
                    self._measurements.bpm, self._config.thresholds.respiratory_rate.min)
                self._events.alerts_queue.enqueue_alert(AlertCodes.BPM_LOW,
                                                        timestamp)
        return True

    def exit_inhale(self, timestamp):
        insp_volume_ml = self.inspiration_volume.integrate() * 1000
        self.log.debug("TV insp: : %sml", insp_volume_ml)
        self._measurements.avg_insp_volume = self.avg_insp_volume.process(insp_volume_ml)
        self._measurements.inspiration_volume = insp_volume_ml
        self.inspiration_volume.reset()
        self.insp_volumes.append((timestamp, insp_volume_ml))
        self.reset_peaks()
        return True

    def enter_exhale(self, timestamp):
        if self.last_state == VentilationState.Exhale:
            self.expiration_volume.reset()
            return

        self.last_state = VentilationState.Exhale
        return True

    def exit_exhale(self, timestamp):
        # Update final expiration volume
        exp_volume_ml = self.expiration_volume.integrate() * 1000
        self.log.debug("TV exp: : %sml", exp_volume_ml)
        self._measurements.avg_exp_volume = self.avg_exp_volume.process(exp_volume_ml)
        self._measurements.expiration_volume = exp_volume_ml
        self.expiration_volume.reset()
        self.exp_volumes.append((timestamp, exp_volume_ml))

        if self._config.thresholds.volume.below(self._measurements.avg_exp_volume):
            self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_LOW, timestamp)
            self.log.warning(
                "average volume too low %s, bottom threshold %s",
                self._measurements.avg_exp_volume, self._config.thresholds.volume.min)
        elif self._config.thresholds.volume.over(self._measurements.avg_exp_volume):
            self._events.alerts_queue.enqueue_alert(
                AlertCodes.VOLUME_HIGH, timestamp)
            self.log.warning(
                "average volume too high %s, top threshold %s",
                self._measurements.avg_exp_volume, self._config.thresholds.volume.max)

        self.reset_min_values()
        return True

    def enter_pre_inhale(self, timestamp):
        return True

    def exit_pre_inhale(self, timestamp):
        return True

    def enter_pre_exhale(self, timestamp):
        return True

    def exit_pre_exhale(self, timestamp):
        return True

    def enter_peep(self, timestamp):
        return True

    def exit_peep(self, timestamp):
        return True

    def send_telemetry(self, timestamp):
        if self.telemetry_sender is not None:
            self.telemetry_sender.enqueue(
                timestamp=timestamp,
                inspiration_volume=self._measurements.inspiration_volume,
                expiration_volume=self._measurements.expiration_volume,
                avg_inspiration_volume=self._measurements.avg_insp_volume,
                avg_expiration_volume=self._measurements.avg_exp_volume,
                peak_flow=self._measurements.intake_peak_flow,
                peak_pressure=self._measurements.intake_peak_pressure,
                min_pressure=self._measurements.peep_min_pressure,
                bpm=self._measurements.bpm,
                o2_saturation_percentage=self._measurements.o2_saturation_percentage,
                current_state=self.current_state,
                alerts=list(self._events.alerts_queue.active_alerts),
                battery_percentage=self._measurements.battery_percentage
            )
        self.last_telemetry_report = timestamp

    def reset_peaks(self):
        self._measurements.intake_peak_pressure = self.peak_pressure
        self._measurements.intake_peak_flow = self.peak_flow
        self.peak_pressure = 0
        self.peak_flow = 0

    def reset_min_values(self):
        self._measurements.peep_min_pressure = self.min_pressure
        self.min_pressure = sys.maxsize

    def update(self, pressure_cmh2o, flow_slm, o2_percentage, timestamp):
        # First time initialization. Not done in __init__ to avoid reading
        # the time in this class, which improves its testability.
        if self.last_breath_timestamp is None:
            self.last_breath_timestamp = timestamp
        if self.last_telemetry_report is None:
            self.last_telemetry_report = timestamp

        # First - check how long it was since last breath
        seconds_from_last_breath = timestamp - self.last_breath_timestamp
        if seconds_from_last_breath >= self.NO_BREATH_ALERT_TIME_SECONDS:
            self.log.warning("No breath detected for the last 12 seconds")
            self._events.alerts_queue.enqueue_alert(AlertCodes.NO_BREATH,
                                                    timestamp)
            self.last_breath_timestamp = None
            self.reset()

        # Flow is measured in Liter/minute, so we convert it to liter/seconds
        # because this is our time unit
        flow_lps = flow_slm / 60  # Liter/sec
        # We track inhale and exhale volume separately. Positive flow means
        # inhale, and negative flow means exhale. But in order to keep our time
        # series monotonic we add 0 samples instead of negative/positive sample
        # for inhale/exhale integrator respectively.
        self.inspiration_volume.add_sample(timestamp, max(0, flow_lps))
        self.expiration_volume.add_sample(timestamp, abs(min(0, flow_lps)))
        self._measurements.set_pressure_value(pressure_cmh2o)
        self._measurements.set_flow_value(flow_slm)
        self._measurements.set_saturation_percentage(o2_percentage)

        # Update peak pressure/flow values
        self.peak_pressure = max(self.peak_pressure, pressure_cmh2o)
        self.min_pressure = min(self.min_pressure, pressure_cmh2o)
        self.peak_flow = max(self.peak_flow, flow_slm)

        # Publish alerts for Pressure
        if self._config.thresholds.pressure.over(pressure_cmh2o):
            self.log.warning(
                "pressure too high %s, top threshold %s",
                pressure_cmh2o, self._config.thresholds.pressure.max)
            self._events.alerts_queue.enqueue_alert(AlertCodes.PRESSURE_HIGH, timestamp)
        elif self._config.thresholds.pressure.below(pressure_cmh2o):
            self.log.warning(
                "pressure too low %s, bottom threshold %s",
                pressure_cmh2o, self._config.thresholds.pressure.min)
            self._events.alerts_queue.enqueue_alert(AlertCodes.PRESSURE_LOW, timestamp)

        # Publish alerts for Oxygen
        # Oxygen too high
        if self._config.thresholds.o2.over(o2_percentage):
            self.log.warning(
                f"Oxygen percentage too high "
                f"({o2_percentage}% > {self._config.thresholds.o2.max}%)")
            self._events.alerts_queue.enqueue_alert(
                AlertCodes.OXYGEN_HIGH, timestamp)

            # Oxygen too low
        elif self._config.thresholds.o2.below(o2_percentage):
            self.log.warning(
                f"Oxygen percentage too low "
                f"({o2_percentage}% < {self._config.thresholds.o2.min}%)")
            self._events.alerts_queue.enqueue_alert(
                AlertCodes.OXYGEN_LOW, timestamp)

        self.check_transition(
            flow_slm=flow_slm,
            pressure_cmh2o=pressure_cmh2o,
            timestamp=timestamp)

        since_last_telem = timestamp - self.last_telemetry_report
        if since_last_telem > self.TELEMETRY_REPORT_MAX_INTERVAL_SEC:
            self.send_telemetry(timestamp)

    def check_transition(self, flow_slm, pressure_cmh2o, timestamp):
        pressure_slope = self.pressure_slope.add_sample(pressure_cmh2o, timestamp)
        flow_slop = self.flow_slope.add_sample(flow_slm, timestamp)
        if flow_slop is None or pressure_slope is None:
            return  # Not enough data

        next_state = self.infer_state(flow_slop, flow_slm, pressure_slope, pressure_cmh2o)
        if next_state != self.current_state:
            exit_handler = self.exit_handlers.get(self.current_state, None)
            entry_handler = self.entry_handlers.get(next_state, None)
            if exit_handler(timestamp) and entry_handler(timestamp):
                self.current_state = next_state
                self.entry_points_ts[next_state].append(timestamp)
                self.log.debug("%s -> %s", self.current_state, next_state)

    def infer_state(self, flow_slope, flow_slm, pressure_slope, pressure_cmh2o):
        flow_positive_increasing = flow_slope > 3 and flow_slm > 2
        flow_negative_decreasing = flow_slope < -10 and flow_slm < -2

        # either waiting for enough volume for inhale
        # or it's noise and switching to pre exhale
        state_config = self._config.state_machine
        if self.current_state == VentilationState.PreInhale:
            insp_volume = self.inspiration_volume.integrate() * 1000
            if insp_volume >= state_config.min_insp_volume_for_inhale:
                return VentilationState.Inhale

            elif (flow_negative_decreasing and
                  pressure_slope < state_config.max_pressure_slope_for_exhale):
                return VentilationState.PreExhale

        # either waiting for enough volume for exhale
        # or it's noise and switching to pre inhale
        if self.current_state == VentilationState.PreExhale:
            exp_volume = self.expiration_volume.integrate() * 1000
            if exp_volume >= state_config.min_exp_volume_for_exhale:
                return VentilationState.Exhale

            elif (flow_positive_increasing and
                  pressure_slope > state_config.min_pressure_slope_for_inhale):
                return VentilationState.PreInhale

        # currently at a inhale\exhale state switching reverse pre state
        if self.current_state != VentilationState.Exhale:
            if flow_negative_decreasing and pressure_slope < state_config.max_pressure_slope_for_exhale:
                return VentilationState.PreExhale

        if self.current_state != VentilationState.Inhale:
            if flow_positive_increasing and pressure_slope > state_config.min_pressure_slope_for_inhale:
                return VentilationState.PreInhale

        return self.current_state


class Sampler(object):
    def __init__(self, measurements, events, flow_sensor, pressure_sensor,
                 a2d, timer, telemetry_sender=None,
                 save_sensor_values=False):
        self.log = logging.getLogger(self.__class__.__name__)
        self._measurements = measurements
        self._flow_sensor = flow_sensor
        self._pressure_sensor = pressure_sensor
        self._a2d = a2d
        self._timer = timer
        self._config = ConfigurationManager.config()
        self._events = events
        self.vsm = VentilationStateMachine(measurements, events, telemetry_sender)
        self.storage_handler = SamplesStorage()
        self.save_sensor_values = save_sensor_values

        auto_calibration = self._config.calibration.auto_calibration
        self.auto_calibrator = AutoFlowCalibrator(
            dp_driver=self._flow_sensor,
            interval_length=auto_calibration.interval,
            iterations=auto_calibration.iterations,
            iteration_length=auto_calibration.iteration_length,
            sample_threshold=auto_calibration.sample_threshold,
            slope_threshold=auto_calibration.slope_threshold,
            min_tail_length=auto_calibration.min_tail,
            grace_length=auto_calibration.grace_length,
        )

    def read_single_sensor(self, sensor, alert_code, timestamp):
        try:
            return sensor.read()
        except UnavailableMeasurmentError as e:
            self.log.error(e)
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

        data = (flow_slm, pressure_cmh2o, o2_saturation_percentage)
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
                                       state=self.vsm.current_state,
                                       tv_insp_displayed=self._measurements.avg_insp_volume,
                                       tv_exp_displayed=self._measurements.avg_exp_volume)

        o2_saturation_percentage = max(0,
                                       min(o2_saturation_percentage, 100))

        if getattr(self._flow_sensor, "set_o2_compensation", None):
            # Update o2 compensation only for relevant DP sensor drivers
            self._flow_sensor.set_o2_compensation(o2_saturation_percentage)

        if self._config.calibration.auto_calibration.enable:
            offset = self.auto_calibrator.get_offset(flow_slm=flow_slm,
                                                     timestamp=ts)

            if offset is not None:
                self.log.info("Writing DP offset of %f to config", offset)
                self._config.calibration.dp_offset = offset
                ConfigurationManager.instance().save()

        self.vsm.update(
            pressure_cmh2o=pressure_cmh2o,
            flow_slm=flow_slm,
            o2_percentage=o2_saturation_percentage,
            timestamp=ts,
        )
