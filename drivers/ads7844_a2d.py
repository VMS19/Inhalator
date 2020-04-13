import spidev
import logging

from errors import SPIDriverInitError, SPIIOError, InvalidCalibrationError

log = logging.getLogger(__name__)


class Ads7844A2D(object):
    SPI_BUS = 0x0
    SPI_DEV = 0x1
    SPI_CLK_SPEED_KHZ = 100000  # 0-200khz
    SPI_MODE = 0x00  # Default CPOL-0 CPHA-0
    PERIPHERAL_MINIMAL_DELAY = 500  # 0.5 milli-sec = 500 micro-sec
    XFER_SPEED_HZ = 0  # Default to max supported speed
    INPUT_MODE_SHIFT = 0x2
    CHANNEL_SELECT_SHIFT = 0x4
    START_BIT_SHIFT = 0x7
    PD_ACTIVE = 0x0
    PD_DISABLED = 0x3
    MODE_DIF = 0x0
    MODE_SGL = 0x1
    DEFAULT_CTRL_BYTE = 0x1 << START_BIT_SHIFT
    VOLTAGE_REF = 2.5
    VOLTAGE_STEP_COUNT = 2 ** 12
    VOLTAGE_CALIBRATION = (VOLTAGE_REF / VOLTAGE_STEP_COUNT)
    FIRST_READING_BIT_SHIFT = 5
    SECOND_READING_BIT_SHIFT = 3

    OXYGEN_CHANNEL = 0
    BATTERY_PERCENTAGE_CHANNEL = 1
    BATTERY_EXISTENCE_CHANNEL = 2

    CHANNEL_MAP = [0, 4, 1, 5, 2, 6, 3, 7]
    FULL_BATTERY = 6.024644649924462
    A2D_BATTERY_RATIO = 0.0337359433

    def __init__(self):
        self._oxygen_calibration_offset = 0
        self._oxygen_calibration_scale = 0
        self._spi = spidev.SpiDev()

        try:
            self._spi.open(self.SPI_BUS, self.SPI_DEV)
        except IOError:
            log.error(
                "Couldn't init spi device. Is the peripheral initialized?")
            raise SPIDriverInitError("spidev peripheral init error")

        try:
            self._spi.max_speed_hz = self.SPI_CLK_SPEED_KHZ
        except IOError:
            log.error(
                "setting spi speed failed. Is speed in the correct range?")
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
            start_byte = self.DEFAULT_CTRL_BYTE | \
                         (self.CHANNEL_MAP[
                              channel] << self.CHANNEL_SELECT_SHIFT) | \
                         (input_mode << self.INPUT_MODE_SHIFT) | \
                         power_down_mode
            sample_raw = self._spi.xfer([start_byte, 0, 0],
                                        self.XFER_SPEED_HZ,
                                        self.PERIPHERAL_MINIMAL_DELAY)

            sample_reading = (
                ((sample_raw[1] & 0x7f) << self.FIRST_READING_BIT_SHIFT) |
                sample_raw[2] >> self.SECOND_READING_BIT_SHIFT)
        except IOError:
            log.error("Failed to read ads7844. "
                      "Check if peripheral is initialized correctly")
            raise SPIIOError("a2d spi read error")

        return self._calibrate_a2d(sample_reading)

    def set_oxygen_calibration(self, point1, point2):
        if point1["x"] > point2["x"]:
            left_p = point2
            right_p = point1
        elif point1["x"] < point2["x"]:
            left_p = point1
            right_p = point2
        else:
            raise InvalidCalibrationError(
                "Bad oxygen calibration.\n"
                "Two calibration points on same x value")

        new_scale = (right_p["y"] - left_p["y"]) / (
            right_p["x"] - left_p["x"])

        if new_scale <= 0:
            raise InvalidCalibrationError(
                f"Bad oxygen calibration.\nnegative slope."
                f"({left_p['x']}%,{left_p['y']}V),"
                f"({right_p['x']}%,{right_p['y']}V)")

        new_offset = point1["y"] - point1["x"] * new_scale

        self._oxygen_calibration_scale = new_scale
        self._oxygen_calibration_offset = new_offset

    def read_oxygen_raw(self):
        return self._sample_a2d(self.OXYGEN_CHANNEL)

    def convert_voltage_to_oxygen(self, volt):
        return volt * self._oxygen_calibration_scale + \
            self._oxygen_calibration_offset

    def read_oxygen(self):
        return self.convert_voltage_to_oxygen(self.read_oxygen_raw())

    def read_battery_percentage(self):
        raw_battery_value = self._sample_a2d(self.BATTERY_PERCENTAGE_CHANNEL)
        battery_value = raw_battery_value / self.A2D_BATTERY_RATIO
        return min(100, int(battery_value * 100 / self.FULL_BATTERY))

    def read_battery_existence(self):
        # According to what the hardware team said, if the battery exists
        # the read value should be around 1.6
        raw_existence_value = self._sample_a2d(self.BATTERY_EXISTENCE_CHANNEL)
        return 1.7 >= raw_existence_value >= 1.5

    def close(self):
        if self._spi is not None:
            self._spi.close()
