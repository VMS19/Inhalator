import pigpio
import logging

from errors import PiGPIOInitError, I2CDeviceNotFoundError, I2CReadError

log = logging.getLogger(__name__)


class AbpPressureSensor(object):
    """Driver class for ABPMAND001PG2A3 Flow sensor."""
    I2C_ADDRESS = 0x28
    MEASURE_BYTE_COUNT = 0x2
    MAX_RANGE_PRESSURE = 0x1  # 1 psi
    MIN_RANGE_PRESSURE = 0x00  # 0 psi
    MAX_OUT_PRESSURE = 0x399A
    MIN_OUT_PRESSURE = 0x666
    SENSITIVITY = float(MAX_RANGE_PRESSURE - MIN_RANGE_PRESSURE) /\
        float(MAX_OUT_PRESSURE - MIN_OUT_PRESSURE)

    def __init__(self, i2c_bus):
        try:
            self._pig = pigpio.pi()
        except pigpio.error as e:
            log.error("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise PiGPIOInitError("pigpio library init error")

        if self._pig is None:
            log.error("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise PiGPIOInitError("pigpio library init error")

        try:
            self._dev = self._pig.i2c_open(i2c_bus, self.I2C_ADDRESS)
        except pigpio.error as e:
            log.error("Could not open i2c connection to pressure sensor."
                      "Is it connected?")
            raise I2CDeviceNotFoundError("i2c connection open failed")

        log.info("ABP pressure sensor initialized")

    def _calculate_pressure(self, pressure_reading):
        return (((pressure_reading - self.MIN_OUT_PRESSURE) *
                self.SENSITIVITY) + self.MIN_RANGE_PRESSURE)

    def read_pressure(self):
        try:
            read_size, pressure_raw = self._pig.i2c_read_device(self._dev, self.MEASURE_BYTE_COUNT)
            if read_size >= self.MEASURE_BYTE_COUNT:
                pressure_reading = ((pressure_raw[0] & 0x3F) << 8) | (pressure_raw[1])
                return (self._calculate_pressure(pressure_reading))
            else
                log.error("Pressure sensor's measure data not ready")
                raise I2CReadError("Pressure sensor measurement unavailable."):
        except pigpio.error as e:
            log.error("Could not read from pressure sensor. "
                      "Is the pressure sensor connected?.")
            raise I2CReadError("i2c write failed")
