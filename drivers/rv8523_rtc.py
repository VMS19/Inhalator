import pigpio
import logging
from datetime import date

from errors import PiGPIOInitError, I2CDeviceNotFoundError, \
                I2CReadError, I2CWriteError

log = logging.getLogger(__name__)


class Rv8523Rtc(object):
    """Driver class for rv8523 rtc."""
    I2C_BUS = 1
    I2C_ADDRESS = 0xD0
    BCD_TENS_SHIFT = 0x4
    BCD_NIBBLE_MASK = 0xF
    REG_CONTROL_1 = 0x0
    REG_SECONDS = 0x3
    REG_MINUTES = 0x4
    REG_HOURS = 0x5
    REG_DAYS = 0x6
    REG_MONTHS = 0x8
    REG_YEARS = 0x9
    ERR_FAIL = -1
    REG_YEARS_OFFSET = 2000

    def __init__(self):
        try:
            self._pig = pigpio.pi()
        except pigpio.error as e:
            log.error("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise PiGPIOInitError("pigpio library init error")

        if self._pig is None:
            log.error("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise PiGPIOInitError("pigpio library init error")

        try:
            self._dev = self._pig.i2c_open(self.I2C_BUS, self.I2C_ADDRESS)
        except AttributeError:
            log.error("Could not init pigpio lib. Did you run 'sudo pigpiod'?")
            raise PiGPIOInitError("pigpio library init error")

        except pigpio.error:
            log.error("Could not open i2c connection to rtc."
                      "Is it connected?")
            raise I2CDeviceNotFoundError("i2c connection open failed")

        # Start RTC
        try:
            self._rtc_start()
        except pigpio.error as e:
            raise e

        log.info("rtc initialized")

    def set_24h_mode(self):
        pass

    def _rtc_start(self):

        try:
            self._pig.i2c_write_device(self._dev, self.REG_CONTROL_1)
            read_size, ctrl_1 = self._pig.i2c_read_device(self._dev, 1)
            if read_size != 1:
                log.error("control 1 reg data not ready")
                raise I2CReadError("rtc data unavailable.")
        except pigpio.error as e:
            log.error("Could not write control 1 reg to RTC. "
                      "Is the RTC connected?.")
            raise I2CWriteError("i2c write failed")

        # Disable stop bit
        ctrl_1 |= 0x20

        try:
            self._pig.i2c_write_device(self._dev, self.REG_CONTROL_1)
            self._pig.i2c_write_device(self._dev, ctrl_1)
        except pigpio.error as e:
            log.error("Could not write control 1 reg to RTC. "
                      "Is the RTC connected?.")
            raise I2CWriteError("i2c write failed")

    def bcd_to_int(self, bcd):
        units = bcd & self.NIBBLE_MASK
        tens = (bcd >> self.BCD_TENS_SHIFT) & self.NIBBLE_MASK
        return (tens * 10 + units)

    def int_to_bcd(self, number):
        units = (number % 10)
        tens = (number / 10) << self.BCD_TENS_SHIFT
        return (tens + units)

    def _set_clock_unit(self, reg, value):
        try:
            self._pig.i2c_write_device(self._dev, reg)
            self._pig.i2c_write_device(self._dev, value)
        except pigpio.error as e:
            raise e

    def _get_clock_unit(self, reg):
        self._pig.i2c_write_device(self._dev, reg)
        read_size, clock_unit_bcd = self._pig.i2c_read_device(self._dev, 1)

        if read_size == 1:
            return self.bcd_to_int(clock_unit_bcd)

        return self.ERR_FAIL

    def _get_time(self):
        seconds = self._get_clock_unit(self.REG_SECONDS)
        minutes = self._get_clock_unit(self.REG_MINUTES)
        hours = self._get_clock_unit(self.REG_HOURS)
        days = self._get_clock_unit(self.REG_DAYS)
        months = self._get_clock_unit(self.REG_MONTHS)
        years = self._get_clock_unit(self.REG_YEARS) + self.REG_YEARS_OFFSET

        return date(years, months, days, hours, minutes, seconds)

    def set_time(self, date):
        try:
            self._set_clock_unit(self.REG_SECONDS, date.second)
            self._set_clock_unit(self.REG_MINUTES, date.minute)
            self._set_clock_unit(self.REG_HOURS, date.hour)
            self._set_clock_unit(self.REG_DAYS, date.day)
            self._set_clock_unit(self.REG_MONTHS, date.month)
            self._set_clock_unit(self.REG_YEARS,
                                 date.year - self.REG_YEARS_OFFSET)
        except pigpio.error as e:
            log.error("Could not set RTC time. "
                      "Is the RTC connected?.")
            raise I2CWriteError("i2c write failed")

    def read(self):
        """ Returns date years to seconds """
        try:
            time = self._get_time()
            if time != self.ERR_FAIL:
                return time
            else:
                log.error("rtc read error")
                raise I2CReadError("RTC get time unavailable.")
        except pigpio.error as e:
            log.error("Could not read from RTC. "
                      "Is the RTC connected?.")
            raise I2CReadError("i2c write failed")
