"""SFM3200 air flow sensor driver.

The use of this driver requires pigpio deamon:
'sudo pigpiod'
(sudo apt-get install pigpio)
"""
import pigpio

class Sfm3200:
    I2C_BUS = 1
    I2C_ADDRESS = 0x40
    SCALE_FACTOR_FLOW = 120
    OFFSET_FLOW = 0x8000
    START_MEASURE_CMD = b"\x10\x00"
    SOFT_RST_CMD = b"\x20\x00"

    def __init__(self):
        self._pig = pigpio.pi()
        self._dev = self._pig.i2c_open(self.I2C_BUS, self.I2C_ADDRESS)

        self._start_measure()
        # Dummy read - first read values are invalid
        _ = self._pig.i2c_read_device(self._dev, 3)


    # Todo: Recognize nacks from slave, and call _start_measure after

    # Todo: catch read/write fail errors. notify device not found

    def _start_measure(self):
        self._pig.i2c_write_device(self._dev, self.START_MEASURE_CMD)

    def soft_reset(self):
        self._pig.i2c_write_device(self._dev, self.SOFT_RST_CMD)

    def read_pressure_slm(self):
        read_size, data = self._pig.i2c_read_device(self._dev, 3)
        if read_size == 3:
            # Todo: combine 2 first byes, & little endian fix?
            # Todo: Calc & compare CRC
        elif read_size == 2:
            # Todo: read without crc
        elif  read_size == 0:
            # Measurement not ready
            pass

        # Normalize flow to slm units
        flow = float(raw_value - self.OFFSET_FLOW) / self.SCALE_FACTOR_FLOW
        return flow

