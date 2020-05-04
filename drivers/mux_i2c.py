import logging
from contextlib import contextmanager

import pigpio

from errors import I2CWriteError
from .i2c_driver import I2cDriver

log = logging.getLogger(__name__)


class MuxI2C(I2cDriver):

    MUX_INSTANCE = None

    @classmethod
    def get_instance(cls):
        return cls.MUX_INSTANCE

    def __new__(cls, *args, **kwargs):
        cls.opened_port = None
        if cls.MUX_INSTANCE is None:
            cls.MUX_INSTANCE = object.__new__(cls)

        return cls.MUX_INSTANCE

    I2C_ADDRESS = 0x70

    def switch_port(self, port):
        port = int(port)
        if self.opened_port is not None and self.opened_port == port:
            return

        if port not in range(5):
            raise ValueError("Port should be between 0 and 4 - got {}".format(port))

        try:
            # First, reset the switch
            self._pig.i2c_write_device(self._dev, "\x00")
            self._pig.i2c_write_device(self._dev, str(0b1 << port))
            self.opened_port = port
        except pigpio.error:
            log.error("Could not switch cmd to mux. Is the mux connected?")
            raise I2CWriteError("i2c write failed")

    @contextmanager
    def lock(self, port):
        self.switch_port(port)
        yield
