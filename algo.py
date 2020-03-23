import time
import logging
import threading

import alerts

log = logging.getLogger(__name__)


class Sampler(threading.Thread):
    SAMPLING_INTERVAL = 0.02  # sec
    MS_IN_MIN = 60 * 1000

    def __init__(self, data_store, flow_sensor, pressure_sensor, alert_cb):
        super(Sampler, self).__init__()
        self.daemon = True
        self._data_store = data_store  # type: DataStore
        self._flow_sensor = flow_sensor
        self._alert_cb = alert_cb
        self._pressure_sensor = pressure_sensor

        # State
        self._currently_breathed_volume = 0
        self._is_during_intake = False
        self._has_crossed_first_cycle = False

    def _handle_intake(self, flow, pressure):
        """We are giving patient air."""
        sampling_interval_in_minutes = self.SAMPLING_INTERVAL / self.MS_IN_MIN
        self._currently_breathed_volume += \
            (flow * sampling_interval_in_minutes)

        if self._currently_breathed_volume > self._data_store.flow_max_threshold:
            self._data_store.set_alert((alerts.alerts.BREATHING_VOLUME_HIGH,
                                        self._currently_breathed_volume))

        if pressure <= self._data_store.BREATHING_THRESHOLD:
            self._has_crossed_first_cycle = True

    def _handle_intake_finished(self, flow, pressure):
        """We are not giving patient air anymore."""

        if self._currently_breathed_volume < self._data_store.flow_min_threshold and \
                self._has_crossed_first_cycle:
            self._data_store.set_alert((alerts.alerts.BREATHING_VOLUME_LOW, self._currently_breathed_volume))

        self._currently_breathed_volume = 0

    def run(self):
        while True:
            self.sampling_iteration()

            time.sleep(self.SAMPLING_INTERVAL)

    def sampling_iteration(self):
        # Read from sensors
        alert_no = alerts.alerts.OK
        flow_value = self._flow_sensor.read_flow_slm()
        pressure_value = self._pressure_sensor.read_pressure()
        self._data_store.update_pressure_values(pressure_value)
        if pressure_value > self._data_store.pressure_max_threshold:
            # Above healthy lungs pressure
            alert_no = alerts.alerts.PRESSURE_HIGH
        if pressure_value < self._data_store.pressure_min_threshold:
            # Below healthy lungs pressure
            alert_no = alerts.alerts.PRESSURE_LOW

        if alert_no != alerts.alerts.OK:
            self._data_store.set_alert((alert_no, pressure_value))

        logging.debug("Breathed: %s" % self._currently_breathed_volume)
        logging.debug("Flow: %s" % flow_value)
        logging.debug("Pressure: %s" % pressure_value)

        if pressure_value <= self._data_store.BREATHING_THRESHOLD:
            logging.debug("-----------is_during_intake=False----------")
            self._is_during_intake = False

        if pressure_value > self._data_store.BREATHING_THRESHOLD:
            logging.debug("-----------is_during_intake=True-----------")
            self._is_during_intake = True

        if self._is_during_intake:
            self._handle_intake(flow=flow_value, pressure=pressure_value)

        else:
            self._handle_intake_finished(flow=flow_value,
                                         pressure=pressure_value)
        self._data_store.update_flow_values(self._currently_breathed_volume * 10000)
