import spidev
import logging

from errors import SPIDriverInitError, SPIIOError

log = logging.getLogger(__name__)


class Ads7844A2D(object):
    SPI_BUS = 0x0
    SPI_DEV = 0x1
    SPI_CLK_SPEED_KHZ = 100000  # 0-200khz
    SPI_MODE = 0x00  # Default CPOL-0 CPHA-0
    PERIPHERAL_MINIMAL_DELAY = 500  # 0.5 milli-sec = 500 micro-sec
    XFER_SPEED_HZ = 0  # Default to max supported speed
    PD_SHIFT = 0x1
    INPUT_MODE_SHIFT = 0x2
    CHANNEL_SELECT_SHIFT = 0x4
    START_BIT_SHIFT = 0x7
    PD_ACTIVE = 0x0
    PD_DISABLED = 0x1
    MODE_DIF = 0x0
    MODE_SGL = 0x1
    DEFAULT_CTRL_BYTE = 0x1 << START_BIT_SHIFT

    def __init__(self):
        self._spi = spidev.SpiDev()

        try:
            self._spi.open(self.SPI_BUS, self.SPI_DEV)
        except IOError as e:
            log.error("Couldn't init spi device, \
                is the peripheral initialized?")
            raise SPIDriverInitError("spidev peripheral init error")

        try:
            self._spi.max_speed_hz = self.SPI_CLK_SPEED_KHZ
        except IOError as e:
            log.error("setting spi speed failed, \
                is speed in the correct range?")
            raise SPIDriverInitError("spidev peripheral init error")

        try:
            self._spi.mode = self.SPI_MODE
        except TypeError as e:
            log.error(e.strerror)
            raise SPIDriverInitError("spi mode error")

        log.info("ads7844 driver initialized")

    def _calibrate_a2d(self, pressure_value_m_bar):
        pass

    def _sample_a2d(self, channel, input_mode=MODE_SGL,
                    power_down_mode=PD_DISABLED):
        try:
            start_byte = self.DEFAULT_CTRL_BYTE |\
                (channel << self.CHANNEL_SELECT_SHIFT) |\
                (input_mode << self.INPUT_MODE_SHIFT) |\
                (power_down_mode << self.PD_SHIFT)
            sample_raw = self._spi.xfer(start_byte,
                                        self.XFER_SPEED_HZ,
                                        self.PERIPHERAL_MINIMAL_DELAY)
        except IOError as e:
            log.error("Failed to read ads7844."
                      "check if peripheral is initialized correctly")
            raise SPIIOError("a2d spi read error")

        return self._calibrate_a2d(sample_raw)

    def sample_a2d_channels(self, channels, input_mode=MODE_SGL,
                            power_down_mode=PD_DISABLED):
        for channel in channels:
            self._sample_a2d(channel, input_mode, power_down_mode)
