import time
import logging
import threading
from enum import Enum
from statistics import mean
from collections import deque
from scipy.stats import linregress

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

    def __init__(self, max_samples):
        self.samples = deque(maxlen=max_samples)

    def reset(self):
        self.samples.clear()

    def process(self, pressure):
        self.samples.append(pressure)
        return mean(self.samples)


class VentilationState(Enum):
    Calibration = 0  # State unknown yet
    Inhale = 1  # Air is flowing to the lungs
    Hold = 2  # PIP is maintained
    Exhale = 3  # Pressure is relieved, air flowing out
    PEEP = 4  # Positive low pressure is maintained until next cycle.


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
        now = time.time()
        if timestamp is None:
            timestamp = now
        self.samples.append(timestamp)
        # Discard beats older than `self.time_span_seconds`
        while self.samples[0] < (now - self.time_span_seconds):
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
        interval = now - oldest
        # protect against division by zero
        if interval == 0:
            # Technically rate is infinity, but 0 will be more descriptive
            return 0

        # We subtract 1 because we have both 1st and last sentinels.
        rate = (len(self.samples) - 1) * (self.time_span_seconds / interval)
        return rate


class VentilationStateMachine(object):
    def __init__(self,
                 state_handlers,
                 peep_to_inhale_slope=8,
                 inhale_to_pip_slope=4,
                 hold_to_exhale_slope=-4,
                 exhale_to_peep_slope=-4):
        self.handlers = state_handlers
        self.log = logging.getLogger(self.__class__.__name__)
        self.peep_to_inhale_slope = peep_to_inhale_slope
        self.inhale_to_pip_slope = inhale_to_pip_slope
        self.pip_to_exhale_slope = hold_to_exhale_slope
        self.exhale_to_peep_slope = exhale_to_peep_slope
        self.rs = RunningSlope(num_samples=7)

        # Transition table:
        # The key is the current state, and the value is a tuple of:
        # 1. The compare func against the threshold (greater-than, less-than)
        # 2. The threshold to compare against
        # 3. The next state if the comparison evaluates to true.
        #
        # For each new sample we compute the current slope, and according to
        # the current state we perform the appropriate comparison against the
        # appropriate threshold. If the comparison returns True - we transition
        # to the next state according to the table.
        self.transitions = {
            VentilationState.PEEP: (float.__gt__, self.peep_to_inhale_slope, VentilationState.Inhale),
            VentilationState.Inhale: (float.__lt__, self.inhale_to_pip_slope, VentilationState.Hold),
            VentilationState.Hold: (float.__lt__, self.pip_to_exhale_slope, VentilationState.Exhale),
            VentilationState.Exhale: (float.__gt__, self.exhale_to_peep_slope, VentilationState.PEEP),
        }
        self.current_state = VentilationState.PEEP
        self.entry_points_ts = {
            VentilationState.PEEP: deque(maxlen=100),
            VentilationState.Inhale: deque(maxlen=100),
            VentilationState.Hold: deque(maxlen=100),
            VentilationState.Exhale: deque(maxlen=100)
        }

    def update(self, pressure_cmh2o, flow_slm, timestamp):
        slope = self.rs.add_sample(pressure_cmh2o, timestamp)
        if slope is None:
            return
        func, threshold, next_state = self.transitions.get(self.current_state)
        current_state_handler = self.handlers.get(self.current_state, None)
        if func(slope, threshold):
            if current_state_handler is not None:
                current_state_handler.exit(timestamp)
            self.rs.reset()
            self.log.debug("%s -> %s", self.current_state, next_state)
            self.current_state = next_state
            self.entry_points_ts[next_state].append(timestamp)
            new_state_handler = self.handlers.get(next_state, None)
            if new_state_handler is not None:
                new_state_handler.enter(timestamp)
        if current_state_handler is not None:
            current_state_handler.process(pressure_cmh2o, flow_slm, timestamp)


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


class StateHandler(object):

    def __init__(self, config, measurements, events):
        self._config = config
        self._measurements = measurements
        self._events = events
        self.log = logging.getLogger(self.__class__.__name__)

    def process(self, pressure_cmh2o, flow_slm, timestamp):
        pass

    def enter(self, timestamp):
        pass

    def exit(self, timestamp):
        pass


class InhaleStateHandler(StateHandler):

    def __init__(self, config, measurements, events):
        super(InhaleStateHandler, self).__init__(config, measurements, events)
        self.breathes_rate_meter = RateMeter(time_span_seconds=60, max_samples=4)

    def exit(self, timestamp):
        self._measurements.bpm = self.breathes_rate_meter.beat(timestamp)


class HoldStateHandler(StateHandler):

    def __init__(self, config, measurements, events):
        super(HoldStateHandler, self).__init__(config, measurements, events)
        self._inhale_max_pressure = 0
        self._inhale_max_flow = 0

    def enter(self, timestamp):
        self._inhale_max_flow = 0
        self._inhale_max_pressure = 0

    def process(self, pressure_cmh2o, flow_slm, timestamp):
        self._inhale_max_pressure = max(pressure_cmh2o, self._inhale_max_pressure)
        self._inhale_max_flow = max(flow_slm, self._inhale_max_flow)

    def exit(self, timestamp):
        self._measurements.intake_peak_flow = self._inhale_max_flow
        self._measurements.intake_peak_pressure = self._inhale_max_pressure


class PEEPHandler(StateHandler):
    def __init__(self, config, measurements, events, accumulator):
        super().__init__(config, measurements, events)
        self.accumulator = accumulator

    def enter(self, timestamp):
        self.log.info("Hold finished. Exhale starts")
        if (self._config.volume_threshold.min != "off" and
                self.accumulator.air_volume_liter <
                self._config.volume_threshold.min):
            self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_LOW)

        volume_ml = self.accumulator.air_volume_liter * 1000
        self.log.info("Volume: %s", volume_ml)
        self._measurements.volume = volume_ml
        # reset values of last intake
        self.accumulator.reset()


class Sampler(threading.Thread):
    SAMPLING_INTERVAL = 0.045  # sec
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
        # No good reason for 1000 max samples. Sounds enough.
        self.peep_avg_calculator = RunningAvg(max_samples=1000)

        self.accumulator = VolumeAccumulator()
        inhale_handler = InhaleStateHandler(
            self._config, self._measurements, self._events)
        hold_handler = HoldStateHandler(
            self._config, self._measurements, self._events)
        peep_handler = PEEPHandler(
            self._config, self._measurements, self._events, self.accumulator)
        self.vsm = VentilationStateMachine({
            VentilationState.Inhale: inhale_handler,
            VentilationState.Hold: hold_handler,
            VentilationState.PEEP: peep_handler})

    def run(self):
        while True:
            self.sampling_iteration()
            time.sleep(self.SAMPLING_INTERVAL)

    def sampling_iteration(self):
        # Read from sensors
        flow_slm = self._flow_sensor.read()
        pressure_cmh2o = self._pressure_sensor.read()
        ts = time.time()
        self.vsm.update(pressure_cmh2o, flow_slm, timestamp=ts)
        self.accumulator.accumulate(ts, flow_slm)
        self._measurements.set_pressure_value(pressure_cmh2o)

        if self._config.pressure_threshold.max != "off" and \
                pressure_cmh2o > self._config.pressure_threshold.max:
            # Above healthy lungs pressure
            self._events.alerts_queue.enqueue_alert(AlertCodes.PRESSURE_HIGH)

        if self._config.pressure_threshold.min != "off" and \
                pressure_cmh2o < self._config.pressure_threshold.min:
            # Below healthy lungs pressure
            self._events.alerts_queue.enqueue_alert(AlertCodes.PRESSURE_LOW)

        if (self._config.volume_threshold.max != 'off' and
                self.accumulator.air_volume_liter >
                self._config.volume_threshold.max):
            self._events.alerts_queue.enqueue_alert(AlertCodes.VOLUME_HIGH)

        self._measurements.set_flow_value(flow_slm)
