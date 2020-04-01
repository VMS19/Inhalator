"""SFM3200 air flow sensor driver.

The use of this driver requires pigpio deamon:
'sudo pigpiod'
(sudo apt-get install pigpio)
"""
import pigpio
from time import sleep
import logging

from errors import PiGPIOInitError, I2CDeviceNotFoundError, \
                I2CReadError, I2CWriteError, FlowSensorCRCError
log = logging.getLogger(__name__)


class Sdp3(object):
    """Driver class for SFM3200 Flow sensor."""
    DP_FLOW_FACTOR = 1
    CRC_POLYNOMIAL = 0x131
    I2C_BUS = 1
    I2C_ADDRESS = 0x25
    STARTUP_DELAY = 0.01  # 10ms
    SCALE_FACTOR_FLOW = 120
    OFFSET_FLOW = 0x8000
    START_MEASURE_FLOW_CMD = b"\x36\x08"
    START_MEASURE_FLOW_AVG_CMD = b"\x36\x03"
    START_MEASURE_DIFF_PRESSURE_CMD = b"\x36\x1E"
    START_MEASURE_DIFF_PRESSURE_AVG_CMD = b"\x36\x15"
    SOFT_RST_CMD = b"\x00\x06"
    STOP_MEASURE_CMD = b"\x3F\xF9"
    SCALE_TEMP = 200
    PASCAL_TO_CMH2O = 98.066

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
            log.error("Could not open i2c connection to flow sensor."
                      "Is it connected?")
            raise I2CDeviceNotFoundError("i2c connection open failed")

        self._start_measure()

    def _start_measure(self):
        try:
            self._pig.i2c_write_device(self._dev, self.START_MEASURE_FLOW_AVG_CMD)
        except pigpio.error as e:
            log.error("Could not write start_measure cmd to flow sensor. "
                      "Is the flow sensor connected?.")
            raise I2CWriteError("i2c write failed")
        sleep(self.STARTUP_DELAY)

        log.info("Started flow sensor measurement")

    def _stop_measure(self):
        try:
            self._pig.i2c_write_device(self._dev, self.STOP_MEASURE_CMD)
        except pigpio.error as e:
            log.error("Could not write start_measure cmd to flow sensor. "
                      "Is the flow sensor connected?.")
            raise I2CWriteError("i2c write failed")

        log.info("Started flow sensor measurement")

    def soft_reset(self):
        try:
            self._pig.i2c_write_device(self._dev, self.SOFT_RST_CMD)
        except pigpio.error as e:
            log.error("Could not write soft reset cmd to flow sensor.")
            raise I2CWriteError("i2c write failed")

    def read_dp(self, retries=2):
        read_size, data = self._pig.i2c_read_device(self._dev, 9)
        if read_size == 9:
            raw_dp = data[0] << 8 | data[1]
            crc_dp = data[2]
            raw_temp = data[3] << 8 | data[4]
            crc_temp = data[5]
            raw_scale = data[6] << 8 | data[7]
            crc_scale = data[8]

            crc_calc_dp = self._crc8(data[:2])
            crc_calc_temp = self._crc8(data[3:5])
            crc_calc_scale = self._crc8(data[6:8])
            if not crc_calc_dp == crc_dp:
                log.error("CRC mismatch while reading differential pressure."
                          "{} - expected {}".format(crc_calc_dp, crc_dp))
                raise FlowSensorCRCError("CRC mismatch")

            if not crc_calc_temp == crc_temp:
                log.error(
                    "CRC mismatch while reading temperature."
                    "{} - expected {}".format(crc_calc_temp, crc_temp))
                raise FlowSensorCRCError("CRC mismatch")

            if not crc_calc_scale == crc_scale:
                log.error(
                    "CRC mismatch while reading scale."
                    "{} - expected {}".format(crc_calc_scale, crc_scale))
                raise FlowSensorCRCError("CRC mismatch")
            #
            # else:
            #     log.error("Too much data recieved, "
            #               "got {} expected 3. data: {}".format(len(data), data))
            #     raise I2CReadError("Too much data read, invalid state")


        elif read_size == 0:
            # Measurement not ready
            if not retries:
                log.error("Flow sensor's measure data consistently not ready")
                raise I2CReadError("Flow sensor measurement unavailable.")

            elif retries == 1:
                log.warning("Flow sensor read returns NA."
                            "This could be a result of voltage swings."
                            "Sending start_measure command to sensor")
                self._start_measure()

            else:
                log.warning("Flow sensor's measure data was not ready. "
                            "Retrying read after a short delay")

            sleep(0.1)
            flow = self.read_dp(retries=retries - 1)
            log.info("Flow Sensor successfully read data, after failed attempt")
            return flow

        elif read_size == pigpio.PI_raw_valueI2C_READ_FAILED:
            log.error("Could not read data from flow sensor."
                      "Is it connected?")
            raise I2CReadError("i2c read failed")

        # Normalize flow to slm units
        dp_pascal = float(raw_dp) / raw_scale
        log.debug("Flow sensor value: {} pascal. CRC correct".format(dp_pascal))
        temp_c = float(raw_temp) / self.SCALE_TEMP
        log.debug("Temparature value: {} C. CRC correct".format(temp_c))
        # dp_cmh2o = dp_pascal * self.PASCAL_TO_CMH2O
        # log.debug("dp sensor value: {} cmh2o. CRC correct".format(dp_pascal))
        return dp_pascal

    def read(self):
        dp_pascal = self.read_dp()
        flow = (abs(dp_pascal) ** 0.5) * self.DP_FLOW_FACTOR
        if dp_pascal < 0:
            flow = -flow

        log.debug("flow value: {} C. CRC correct".format(flow))
        return flow


    def _crc8(self, data):
        crc = 0xFF
        for b in data:
            crc = crc ^ b
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ self.CRC_POLYNOMIAL
                else:
                    crc = crc << 1
        return crc
