import pigpio
import logging

from errors import I2CReadError, UnavailableMeasurmentError, \
    SensorDiagnosticError

from .i2c_driver import I2cDriver
from .mux_i2c import MuxI2C

log = logging.getLogger(__name__)

mux = MuxI2C()


class HoneywellPressureSensor(I2cDriver):
    """Driver class for Honeywell pressure and DP sensors."""
    MUX_PORT = NotImplemented
    I2C_ADDRESS = 0x28
    MEASURE_BYTE_COUNT = 0x2
    MAX_RANGE_PRESSURE = NotImplemented
    MIN_RANGE_PRESSURE = NotImplemented
    MAX_OUT_PRESSURE = NotImplemented
    MIN_OUT_PRESSURE = NotImplemented
    SENSITIVITY = NotImplemented
    CMH2O_RATIO = NotImplemented
    STATUS_NORMAL = 0
    STATUS_CMD_MODE = 1
    STATUS_STALE_DATA = 2
    STATUS_DIAGNOSTIC_COND = 3

    def _calculate_pressure(self, pressure_reading):
        pressure = (self.MIN_RANGE_PRESSURE +
                    self.SENSITIVITY * (pressure_reading - self.MIN_OUT_PRESSURE))
        cmh2o_pressure = pressure * self.CMH2O_RATIO
        return cmh2o_pressure

    def read(self):
        """ Returns pressure as cmh2o """
        try:
            with mux.lock(self.MUX_PORT):
                read_size, pressure_raw = self._pig.i2c_read_device(self._dev,
                        self.MEASURE_BYTE_COUNT)

            if read_size >= self.MEASURE_BYTE_COUNT:
                status_reading = (pressure_raw[0] >> 6) & 0x03
                self._check_sensor_status(status_reading)
                pressure_reading = ((pressure_raw[0] & 0x3F) << 8) | (pressure_raw[1])
                return self._calculate_pressure(pressure_reading)

            else:
                log.warning(f"Sensor sent only {read_size} out of "
                            f"{self.MEASURE_BYTE_COUNT} bytes")
                raise I2CReadError("read too few bytes")

        except pigpio.error as e:
            log.error("Could not read from honeywell sensor. "
                      "Is the sensor connected?.")
            raise I2CReadError("i2c read failed") from e

    def _check_sensor_status(self, status):
        if status == self.STATUS_NORMAL:
            return

        elif status == self.STATUS_STALE_DATA:
            log.warning("Sensor's measure data not ready. sampling too fast?")
            raise UnavailableMeasurmentError("Sensor data unavailable")

        elif status == self.STATUS_DIAGNOSTIC_COND:
            log.error("Sensor diagnostic fault indicated")
            raise SensorDiagnosticError("Sensor diagnostic fault indicated")

        elif status == self.STATUS_CMD_MODE:
            log.warning("Sensor unexpectedly in command mode")

        else:
            log.warning("Invalid sensor status code")
