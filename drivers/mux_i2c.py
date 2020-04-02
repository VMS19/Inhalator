"""SFM3200 air flow sensor driver.

The use of this driver requires pigpio deamon:
'sudo pigpiod'
(sudo apt-get install pigpio)
"""
from time import sleep
import logging

import pigpio

from errors import (I2CReadError,
                    I2CWriteError,
                    PiGPIOInitError,
                    FlowSensorCRCError,
                    I2CDeviceNotFoundError)

log = logging.getLogger(__name__)


class MuxI2C(object):

    I2C_BUS = 1
    I2C_ADDRESS = 0x70

    def __init__(self):
        try:
            self._pig = pigpio.pi()
        except pigpio.error as e:
            log.error("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise PiGPIOInitError("pigpio library init error") from e

        if self._pig is None:
            log.error("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise PiGPIOInitError("pigpio library init error")

        try:
            self._dev = self._pig.i2c_open(self.I2C_BUS, self.I2C_ADDRESS)
        except AttributeError as e:
            log.error("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise PiGPIOInitError("pigpio library init error") from e

        except pigpio.error as e:
            log.error("Could not open i2c connection to flow sensor."
                      "Is it connected?")
            raise I2CDeviceNotFoundError("i2c connection open failed") from e

    def switch_port(self, port):

        try:
            self._pig.i2c_write_device(self._dev, 0b1 << port)
        except pigpio.error as e:
            log.error("Could not switch cmd to mux. "
                      "Is the mux connected?.")
            raise I2CWriteError("i2c write failed") from e

        log.info("Switch to port {}".format(port))
