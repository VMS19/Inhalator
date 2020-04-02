import pigpio
import logging

import errors

log = logging.getLogger(__name__)


class I2cDriver(object):
    I2C_BUS = 1
    I2C_ADDRESS = NotImplemented

    def __init__(self):
        self._dev = None
        self._pig = None
        try:
            self._pig = pigpio.pi()
        except pigpio.error as e:
            log.exception("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise errors.PiGPIOInitError("pigpio library init error") from e

        if self._pig is None:
            log.exception("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise errors.PiGPIOInitError("pigpio library init error")

        try:
            self._dev = self._pig.i2c_open(self.I2C_BUS, self.I2C_ADDRESS)
        except AttributeError as e:
            log.exception("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise errors.PiGPIOInitError("pigpio library init error") from e

        except pigpio.error as e:
            log.exception("Could not open i2c connection to sensor."
                          "Is it connected?")
            raise errors.I2CDeviceNotFoundError("i2c connection open failed") from e

    def close(self):
        if self._pig is not None and self._dev is not None:
            self._pig.i2c_close(self._dev)
