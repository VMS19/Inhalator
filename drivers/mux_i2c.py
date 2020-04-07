import logging

import pigpio

from errors import I2CWriteError
from .i2c_driver import I2cDriver

log = logging.getLogger(__name__)

#Todo: close this driver!! init it via driver_factory!!!
class MuxI2C(I2cDriver):
    I2C_ADDRESS = 0x70

    def switch_port(self, port):
        port = int(port)
        if port not in range(5):
            raise ValueError("Port should be between 0 and 4 - got {}".format(port))

        try:
            # First, reset the switch
            self._pig.i2c_write_device(self._dev, "\x00")
            self._pig.i2c_write_device(self._dev, str(0b1 << port))
        except pigpio.error:
            log.error("Could not switch cmd to mux. Is the mux connected?")
            raise I2CWriteError("i2c write failed")

        log.info("Switch to port {}".format(port))
