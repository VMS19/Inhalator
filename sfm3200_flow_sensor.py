import smbus

class Sfm3200:
    I2C_ADDRESS = 0x40
    SCALE_FACTOR_FLOW = 120
    OFFSET_FLOW = 0x8000
    START_MEASURE_CMD = 0x1000
    READ_SERIAL_CMD = 0x31AE
    SOFT_RST_CMD = 0x2000

    def __init__(self):
        self._bus = smbus.SMBus(1)
        self._start_measure()
        # Dummy read

    def _read_byte(self):
        return self._bus.read_byte(self.I2C_ADDRESS)

    def _write_cmd(self, cmd):
        cmd_high = cmd >> 8
        cmd_low = cmd & 0xff
        self._bus.write_byte(self.I2C_ADDRESS, cmd_high)
        self._bus.write_byte(self.I2C_ADDRESS, cmd_low)

    def _start_measure(self):
        self._write_cmd(self.START_MEASURE_CMD)

    def soft_reset(self):
        self._write_cmd(self.SOFT_RST_CMD)

    def read_pressure(self):
        raw_value_high = self._read_byte()
        raw_value_low = self._read_byte()
        crc_value = self._read_byte()
        raw_value = raw_value_high << 8 | raw_value_low;
        # Calc & compare CRC
        flow = float(raw_value - self.OFFSET_FLOW) / self.SCALE_FACTOR_FLOW
        return flow



