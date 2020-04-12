import pigpio
import logging
from datetime import datetime
import subprocess

from errors import I2CReadError, I2CWriteError
from .i2c_driver import I2cDriver

log = logging.getLogger(__name__)


class Rv8523Rtc(I2cDriver):
    """Driver class for rv8523 rtc."""
    I2C_BUS = 1
    I2C_ADDRESS = 0x68
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
        super().__init__()

        # Start RTC
        self._rtc_start()

        log.debug("rtc initialized")

    def _rtc_start(self):
        try:
            self._pig.i2c_write_device(self._dev, [self.REG_CONTROL_1])
            read_size, ctrl_1 = self._pig.i2c_read_device(self._dev, 1)
            if read_size != 1:
                log.error("control 1 reg data not ready")
                raise I2CReadError("rtc data unavailable")
        except pigpio.error:
            log.error("Could not write control 1 reg to RTC "
                      "Is the RTC connected?")
            raise I2CWriteError("i2c write failed")

        # Disable stop bit
        ctrl_1[0] &= 0xDF

        # Set 24 hr mode
        ctrl_1[0] &= 0xF7

        try:
            self._pig.i2c_write_device(self._dev,
                                       [self.REG_CONTROL_1, ctrl_1[0]])
        except pigpio.error:
            log.error("Could not write control 1 reg to RTC "
                      "Is the RTC connected?")
            raise I2CWriteError("i2c write failed")

    def bcd_to_int(self, bcd):
        units = bcd & self.BCD_NIBBLE_MASK
        tens = (bcd >> self.BCD_TENS_SHIFT) & self.BCD_NIBBLE_MASK
        return tens * 10 + units

    def int_to_bcd(self, number):
        units = number % 10
        tens = int(number / 10) << self.BCD_TENS_SHIFT
        return tens + units

    def _set_clock_unit(self, value, reg):
        value = self.int_to_bcd(value)
        self._pig.i2c_write_device(self._dev, [reg, value])

    def _get_clock_unit(self, mask, reg=None):
        if reg is not None:
            self._pig.i2c_write_device(self._dev, [reg])
        read_size, clock_unit_bcd = self._pig.i2c_read_device(self._dev, 1)

        if read_size == 1:
            return self.bcd_to_int(clock_unit_bcd[0] & mask)

        return self.ERR_FAIL

    def get_rtc_time(self):
        seconds = self._get_clock_unit(0x7F, self.REG_SECONDS)
        minutes = self._get_clock_unit(0x7F)
        hours = self._get_clock_unit(0x3F)
        days = self._get_clock_unit(0x1F)
        months = self._get_clock_unit(0x1F, self.REG_MONTHS)
        years = self._get_clock_unit(0x7F) + self.REG_YEARS_OFFSET
        try:
            return datetime(years, months, days, hours, minutes, seconds)
        except ValueError as e:
            log.error("RTC invalid time, please set RTC")
            self.set_rtc_time(datetime.now())
            raise e

    def set_rtc_time(self, date):
        try:
            self._set_clock_unit(date.second, self.REG_SECONDS)
            self._set_clock_unit(date.minute, self.REG_MINUTES)
            self._set_clock_unit(date.hour, self.REG_HOURS)
            self._set_clock_unit(date.day, self.REG_DAYS)
            self._set_clock_unit(date.month, self.REG_MONTHS)
            self._set_clock_unit(date.year - self.REG_YEARS_OFFSET,
                                 self.REG_YEARS)
        except pigpio.error:
            log.error("Could not set RTC time. Is the RTC connected?")
            raise I2CWriteError("i2c write failed")

    def set_system_time(self):
        ''' Read RTC and set as system time '''
        try:
            dt = self.read()
        except Exception as e:
            raise e

        second = str(dt.second)
        minute = str(dt.minute)
        hour = str(dt.hour)
        day = str(dt.day)
        month = str(dt.month)
        year = str(dt.year)
        subprocess.call("sudo date -s '{}-{}-{} {}:{}:{}' > /dev/null".
                        format(year, month, day, hour, minute, second),
                        shell=True)

    def read(self):
        """ Returns date years to seconds """
        try:
            time = self.get_rtc_time()
            if time != self.ERR_FAIL:
                return time
            else:
                log.error("rtc read error")
                raise I2CReadError("RTC get time unavailable")
        except pigpio.error:
            log.error("Could not read from RTC. Is the RTC connected?")
            raise I2CReadError("i2c write failed")
