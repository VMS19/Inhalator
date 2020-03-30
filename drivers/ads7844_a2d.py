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
    INPUT_MODE_SHIFT = 0x2
    CHANNEL_SELECT_SHIFT = 0x6
    START_BIT_SHIFT = 0x7
    PD_ACTIVE = 0x0
    PD_DISABLED = 0x3
    MODE_DIF = 0x0
    MODE_SGL = 0x1
    DEFAULT_CTRL_BYTE = 0x1 << START_BIT_SHIFT
    VOLTAGE_REF = 0.946
    VOLTAGE_STEP_COUNT = 2 ** 12
    VOLTAGE_CALIBRATION = (VOLTAGE_REF / VOLTAGE_STEP_COUNT)
    FIRST_READING_BIT_SHIFT = 5
    SAMPLE_CHANNELS = [0]

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

    def _calibrate_a2d(self, sample):
        return sample * self.VOLTAGE_CALIBRATION

    def _sample_a2d(self, channel, input_mode=MODE_SGL,
                    power_down_mode=PD_DISABLED):
        try:
            start_byte = self.DEFAULT_CTRL_BYTE |\
                (channel << self.CHANNEL_SELECT_SHIFT) |\
                (input_mode << self.INPUT_MODE_SHIFT) |\
                power_down_mode
            sample_raw = self._spi.xfer([start_byte, 0, 0],
                                        self.XFER_SPEED_HZ,
                                        self.PERIPHERAL_MINIMAL_DELAY)
            sample_reading = (sample_raw[0] << self.FIRST_READING_BIT_SHIFT) |\
                sample_raw[1]
        except IOError as e:
            log.error("Failed to read ads7844."
                      "check if peripheral is initialized correctly")
            raise SPIIOError("a2d spi read error")

        return self._calibrate_a2d(sample_reading)

    def read(self, input_mode=MODE_SGL, power_down_mode=PD_DISABLED):
        sample_res = []
        for channel in self.SAMPLE_CHANNELS:
            sample_res.append(self._sample_a2d(channel, input_mode,
                              power_down_mode))
        return sample_res
