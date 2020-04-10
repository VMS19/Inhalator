import pigpio
import logging

from errors import I2CReadError

from .i2c_driver import I2cDriver
from .mux_i2c import MuxI2C

log = logging.getLogger(__name__)

mux = MuxI2C()


class HoneywellPressureSensor(I2cDriver):
    """Driver class for ABPMAND001PG2A3 Flow sensor."""
    MUX_PORT = NotImplemented
    I2C_ADDRESS = 0x28
    MEASURE_BYTE_COUNT = 0x2
    MAX_RANGE_PRESSURE = NotImplemented
    MIN_RANGE_PRESSURE = NotImplemented
    MAX_OUT_PRESSURE = NotImplemented
    MIN_OUT_PRESSURE = NotImplemented
    SENSITIVITY = NotImplemented
    CMH2O_RATIO = NotImplemented

    def _calculate_pressure(self, pressure_reading):
        pressure = (self.MIN_RANGE_PRESSURE +
                    self.SENSITIVITY * (pressure_reading - self.MIN_OUT_PRESSURE))
        cmh2o_pressure = pressure * self.CMH2O_RATIO
        return cmh2o_pressure

    def read(self):
        """ Returns pressure as cmh2o """
        try:
            with mux.lock(self.MUX_PORT):
                read_size, pressure_raw = \
                    self._pig.i2c_read_device(self._dev, self.MEASURE_BYTE_COUNT)
            if read_size >= self.MEASURE_BYTE_COUNT:
                pressure_reading = ((pressure_raw[0] & 0x3F) << 8) | (pressure_raw[1])
                return self._calculate_pressure(pressure_reading)

            else:
                log.warning("Pressure sensor's measure data not ready")
        except pigpio.error as e:
            log.error("Could not read from pressure sensor. "
                      "Is the pressure sensor connected?.")
            raise I2CReadError("i2c write failed") from e
