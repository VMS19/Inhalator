import smbus

class Sfm3200:
    I2C_ADDRESS = 0x40
    SCALE_FACTOR_FLOW = 120
    OFFSET_FLOW = 0x8000
    def __init__(self):
        self._bus = smbus.SMBus(1)

    def _read_byte(self):
        return self._bus.read_byte(self.I2C_ADDRESS)

    def read_pressure(self):
        raw_value_a = self._read_byte()
        raw_value_b = self._read_byte()
        raw_value_c = self._read_byte()



