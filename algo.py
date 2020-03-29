import time
import logging
import threading

from data.alerts import Alert, AlertCodes

log = logging.getLogger(__name__)


class Sampler(threading.Thread):
    SAMPLING_INTERVAL = 0.02  # sec
    MS_IN_MIN = 60 * 1000
    ML_IN_LITER = 1000

    def __init__(self, data_store, flow_sensor, pressure_sensor):
        super(Sampler, self).__init__()
        self.daemon = True
        self._data_store = data_store  # type: DataStore
        self._flow_sensor = flow_sensor
        self._pressure_sensor = pressure_sensor

        # State
        self._current_intake_volume = 0
        self._intake_max_flow = 0
        self._intake_max_pressure = 0
        self._has_crossed_first_cycle = False
        self._is_during_intake = False
        self._last_intake_time = 0

        # Alerts related
        self.breathing_alert = AlertCodes.OK
        self.pressure_alert = AlertCodes.OK

    def _handle_intake(self, flow, pressure):
        """We are giving patient air."""
        sampling_interval_in_minutes = self.SAMPLING_INTERVAL / self.MS_IN_MIN
        self._current_intake_volume += \
            (flow * self.ML_IN_LITER * sampling_interval_in_minutes)
        logging.debug("Current Intake volume: %s" % self._current_intake_volume)

        if self._data_store.volume_threshold.max != 'off' and \
                self._current_intake_volume >\
           self._data_store.volume_threshold.max:
            self.breathing_alert = AlertCodes.BREATHING_VOLUME_HIGH

        if pressure <= self._data_store.breathing_threshold:
            self._has_crossed_first_cycle = True

        self._intake_max_pressure = max(pressure, self._intake_max_pressure)
        self._intake_max_flow = max(flow, self._intake_max_flow)

    def _handle_intake_finished(self, flow, pressure):
        """We are not giving patient air anymore."""
        if self._data_store.volume_threshold.min != "off" and \
                self._current_intake_volume <\
           self._data_store.volume_threshold.min and \
                self._has_crossed_first_cycle:

            self.breathing_alert = AlertCodes.BREATHING_VOLUME_LOW

        self._data_store.set_intake_peaks(self._intake_max_pressure,
                                          self._intake_max_pressure,
                                          self._current_intake_volume)

        # reset values of last intake
        self._current_intake_volume = 0
        self._intake_max_flow = 0
        self._intake_max_pressure = 0

    def run(self):
        while True:
            self.sampling_iteration()
            time.sleep(self.SAMPLING_INTERVAL)

    def sampling_iteration(self):
        # Clear alerts calculation
        self.breathing_alert = AlertCodes.OK
        self.pressure_alert = AlertCodes.OK

        # Read from sensors
        flow_value = self._flow_sensor.read()
        pressure_value_cmh2o = self._pressure_sensor.read()

        self._data_store.set_pressure_value(pressure_value_cmh2o)

        if self._data_store.pressure_threshold.max != "off" and \
                pressure_value_cmh2o > self._data_store.pressure_threshold.max:
            # Above healthy lungs pressure
            self.pressure_alert = AlertCodes.PRESSURE_HIGH

        if self._data_store.pressure_threshold.min != "off" and \
                pressure_value_cmh2o < self._data_store.pressure_threshold.min:
            # Below healthy lungs pressure
            self.pressure_alert = AlertCodes.PRESSURE_LOW

        logging.debug("Breathed: %s" % self._current_intake_volume)
        logging.debug("Flow: %s" % flow_value)
        logging.debug("Pressure: %s" % pressure_value_cmh2o)

        if pressure_value_cmh2o <= self._data_store.breathing_threshold and\
           self._is_during_intake:
            logging.debug("-----------is_during_intake=False----------")
            self._handle_intake_finished(flow=flow_value,
                                         pressure=pressure_value_cmh2o)
            self._is_during_intake = False

        if pressure_value_cmh2o > self._data_store.breathing_threshold:
            logging.debug("-----------is_during_intake=True-----------")
            self._handle_intake(flow=flow_value, pressure= pressure_value_cmh2o)

            if not self._is_during_intake:
                # Beginning of intake
                # Calculate breaths per minute:
                curr_time = time.time()
                self._data_store.bpm = 1.0 / (
                curr_time - self._last_intake_time) * 60
                self._last_intake_time = curr_time

            self._is_during_intake = True

        self._data_store.set_flow_value(flow_value)

        alert = Alert(self.breathing_alert | self.pressure_alert)
        if alert != AlertCodes.OK and\
           self._data_store.alerts_queue.last_alert != alert:
                self._data_store.alerts_queue.enqueue_alert(alert)
