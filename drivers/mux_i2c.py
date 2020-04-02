import logging

import pigpio

from errors import (I2CWriteError,
                    PiGPIOInitError,
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
            raise PiGPIOInitError("pigpio library init error")

        if self._pig is None:
            log.error("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise PiGPIOInitError("pigpio library init error")

        try:
            self._dev = self._pig.i2c_open(self.I2C_BUS, self.I2C_ADDRESS)
        except AttributeError as e:
            log.error("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise PiGPIOInitError("pigpio library init error")

        except pigpio.error as e:
            log.error("Could not open i2c connection to flow sensor."
                      "Is it connected?")
            raise I2CDeviceNotFoundError("i2c connection open failed")

    def switch_port(self, port):
        int_port = int(port)
        if int_port > 4 or int_port < 0:
            raise ValueError("Bad Port sent to switch.")
    
        try:
            # First, reset the switch
            self._pig.i2c_write_device(self._dev, "\x00")
            self._pig.i2c_write_device(self._dev, str(0b1 << int_port))
        except pigpio.error as e:
            log.error("Could not switch cmd to mux. "
                      "Is the mux connected?.")
            raise I2CWriteError("i2c write failed")

        log.info("Switch to port {}".format(port))
