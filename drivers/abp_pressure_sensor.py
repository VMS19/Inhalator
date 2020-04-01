import pigpio
import logging

from errors import PiGPIOInitError, I2CDeviceNotFoundError, I2CReadError

from i2c_driver import I2cDriver

log = logging.getLogger(__name__)


class AbpPressureSensor(I2cDriver):
    """Driver class for ABPMAND001PG2A3 Flow sensor."""
    I2C_ADDRESS = 0x28
    MEASURE_BYTE_COUNT = 0x2
    MAX_RANGE_PRESSURE = 0x1  # 1 psi
    MIN_RANGE_PRESSURE = 0x00  # 0 psi
    MAX_OUT_PRESSURE = 0x399A
    MIN_OUT_PRESSURE = 0x666
    SENSITIVITY = float(MAX_RANGE_PRESSURE - MIN_RANGE_PRESSURE) /\
        float(MAX_OUT_PRESSURE - MIN_OUT_PRESSURE)
    PSI_CMH2O_RATIO = 70.307

    def __init__(self):
        super().__init__(self)
        log.info("ABP pressure sensor initialized")

    def _calculate_pressure(self, pressure_reading):
        psi_pressure = (((pressure_reading - self.MIN_OUT_PRESSURE) *
                self.SENSITIVITY) + self.MIN_RANGE_PRESSURE)
        cmh2o_pressure = psi_pressure * self.PSI_CMH2O_RATIO
        return (cmh2o_pressure)

    def read(self):
        """ Returns pressure as cmh2o """
        try:
            read_size, pressure_raw = self._pig.i2c_read_device(self._dev, self.MEASURE_BYTE_COUNT)
            if read_size >= self.MEASURE_BYTE_COUNT:
                pressure_reading = ((pressure_raw[0] & 0x3F) << 8) | (pressure_raw[1])
                return (self._calculate_pressure(pressure_reading))
            else:
                # Todo: Do we need to retry reading after a little sleep? (see flow sensor logic)
                log.error("Pressure sensor's measure data not ready")
                raise I2CReadError("Pressure sensor measurement unavailable.")
        except pigpio.error as e:
            log.error("Could not read from pressure sensor. "
                      "Is the pressure sensor connected?.")
            raise I2CReadError("i2c write failed") from e
