import pigpio
import logging

from errors import PiGPIOInitError, I2CDeviceNotFoundError, I2CReadError

log = logging.getLogger(__name__)


class AbpPressureSensor(object):
    """Driver class for ABPMAND001PG2A3 Flow sensor."""
    I2C_BUS = 2
    I2C_ADDRESS = 0x28
    MEASURE_BYTE_COUNT = 0x2
    MAX_RANGE_PRESSURE = 0x1  # 1 psi
    MIN_RANGE_PRESSURE = 0x00  # 0 psi
    MAX_OUT_PRESSURE = 0x3FFF
    MIN_OUT_PRESSURE = 0x0
    SENSITIVITY = float(MAX_RANGE_PRESSURE - MIN_RANGE_PRESSURE) /\
        float(MAX_OUT_PRESSURE - MIN_OUT_PRESSURE)

    def __init__(self):
        try:
            self._pig = pigpio.pi()
        except pigpio.error as e:
            log.error("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise PiGPIOInitError("pigpio library init error")

        if self._pig is None:
            log.error("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise PiGPIOInitError("pigpio library init error")

        try:
            self._dev = self._pig.i2c_open(self.I2C_BUS, self.I2C_ADDRESS)
        except pigpio.error as e:
            log.error("Could not open i2c connection to pressure sensor."
                      "Is it connected?")
            raise I2CDeviceNotFoundError("i2c connection open failed")

        log.info("ABP pressure sensor initialized")

    def _calculate_pressure(self, pressure_reading):
        return (((pressure_reading - self.MIN_OUT_PRESSURE) *
                self.SENSITIVITY) + self.MIN_PRESSURE)

    def read_pressure(self):
        try:
            read_size, data = self._pig.i2c_read_device(self._dev, self.MEASURE_BYTE_COUNT)
            return (self._calculate_pressure(data))
        except pigpio.error as e:
            log.error("Could not read from pressure sensor. "
                      "Is the pressure sensor connected?.")
            raise I2CReadError("i2c write failed")
