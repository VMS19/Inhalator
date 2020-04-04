import logging

from data.alerts import AlertCodes
from data.configurations import Configurations
from logic.state_machine import VentilationStateMachine
from logic.utils import TRACE


class Sampler(object):

    def __init__(self, measurements, events, flow_sensor, pressure_sensor,
                 oxygen_a2d, timer):
        super(Sampler, self).__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self._measurements = measurements  # type: Measurements
        self._flow_sensor = flow_sensor
        self._pressure_sensor = pressure_sensor
        self._oxygen_a2d = oxygen_a2d
        self._timer = timer
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
        ts = self._timer.get_time()
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