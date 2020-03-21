import spidev
import logging

from errors import HCEDriverInitError, HCEIOError

log = logging.getLogger(__name__)


class HcePressureSensor(object):
    SPI_BUS = 0x0
    SPI_DEV = 0x0
    SPI_CLK_SPEED_KHZ = 2500000  # 100-640khz
    SPI_MODE = 0x00  # Default CPOL-0 CPHA-0
    PERIPHERAL_MINIMAL_DELAY = 0.05  # 5 milli, but really is 5 micro
    MOSI_DATA = 0xFF  # HIGH values are needed, otherwise undefined behaviour
    SPI_READ_CMD = [MOSI_DATA] * 3
    MAX_PRESSURE = 0x00  # operating pressure? page 2
    MIN_PRESSURE = 0x00
    MAX_OUT_PRESSURE = 0x00  # Output? page 3
    MIN_OUT_PRESSURE = 0x00
    SENSITIVITY = (MAX_OUT_PRESSURE - MIN_OUT_PRESSURE) /\
        (MAX_PRESSURE - MIN_PRESSURE)

    def __init__(self):
        self._spi = spidev.SpiDev()

        try:
            self._spi.open(self.SPI_BUS, self.SPI_DEV)
        except IOError as e:
            log.error("Couldn't init spi device, \
                is the peripheral initialized?")
            raise HCEDriverInitError("spidev peripheral init error") from e

        try:
            self._spi.max_speed_hz = self.SPI_CLK_SPEED_KHZ
        except IOError as e:
            log.error("setting spi speed failed, \
                is speed in the correct range?")
            raise HCEDriverInitError("spidev peripheral init error") from e

        try:
            self._spi.mode = self.SPI_MODE
        except TypeError as e:
            log.error(e.strerror)
            raise HCEDriverInitError("spi mode error") from e

        log.info("HCE pressure sensor initialized")

    def _calculate_pressure(self, pressure_reading):
        return (((pressure_reading - self.MIN_OUT_PRESSURE) /
                self.SENSITIVITY) + self.MIN_PRESSURE)

    def read_pressure(self):
        try:
            pressure_raw = self._spi.xfer(self.SPI_READ_CMD,
                self.PERIPHERAL_MINIMAL_DELAY * 10)
        except IOError as e:
            log.error("check if peripheral is initialized correctly")
            raise HCEIOError("pressure read error") from e

        pressure_reading = (pressure_raw[1] << 16) | (pressure_raw[2])
        pressure_parsed = self._calculate_pressure(pressure_reading)
        return pressure_parsed
