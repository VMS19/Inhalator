import spidev


class HcePressureSensor(object):
    SPI_BUS = 0x0
    SPI_DEV = 0x0
    SPI_CLK_SPEED_KHZ = 2500000  # 100-640khz
    SPI_MODE = 0x00  # Default CPOL-0 CPHA-0
    PERIPHERAL_MINIMAL_DELAY = 0.05  # 5 milli, but really is 5 micro
    MOSI_DATA = 0xFF  # HIGH values are needed, otherwise undefined behaviour
    SPI_READ_CMD = [MOSI_DATA] * 3
    # change names of these
    MAX_PRESSURE = None  # operating pressure? page 2
    MIN_PRESSURE = None
    MAX_OUT_PRESSURE = None  # Output? page 3
    MIN_OUT_PRESSURE = None
    SENSITIVITY = (MAX_OUT_PRESSURE - MIN_OUT_PRESSURE) /\
        (MAX_PRESSURE - MIN_PRESSURE)

    def __init__(self):
        self._spi = spidev.SpiDev()
        self._spi.open(self.SPI_BUS, self.SPI_DEV)
        self._spi.max_speed_hz = self.SPI_CLK_SPEED_KHZ
        self._spi.mode = self.SPI_MODE

    def _calculate_pressure(self, pressure_reading):
        return (((pressure_reading - self.MIN_OUT_PRESSURE) /
                self.SENSITIVITY) + self.MIN_PRESSURE)

    def read_pressure(self):
        pressure_raw = self._spi.xfer(self.SPI_READ_CMD,
            self.PERIPHERAL_MINIMAL_DELAY * 10)
        pressure_reading = (pressure_raw[1] << 16) | (pressure_raw[2])
        pressure_parsed = self._calculate_pressure(pressure_reading)
        return pressure_parsed
