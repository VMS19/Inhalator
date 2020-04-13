import logging
import sys
from time import sleep

import pigpio

from errors import I2CReadError, I2CWriteError
from .i2c_driver import I2cDriver


class SdpPressureSensor(I2cDriver):
    """Driver class for SDP8XXX Pressure sensor."""
    I2C_ADDRESS = 0x25
    MEASURE_BYTE_COUNT = 0x3
    CMD_TRIGGERED_DIFFERENTIAL_PRESSURE = b"\x36\x2f"
    CMD_CONT_DIFFERENTIAL_PRESSURE = b"\x36\x1e"
    CMD_STOP = b"\x3F\xF9"
    CRC_POLYNOMIAL = 0x31
    CRC_INIT_VALUE = 0xFF
    SCALE_FACTOR_PASCAL = 60
    CMH20_PASCAL_RATIO = 98.0665
    SYSTEM_RATIO = 46.24
    START_MEASURE_FLOW_CMD = b"\x36\x08"
    START_MEASURE_FLOW_AVG_CMD = b"\x36\x03"
    START_MEASURE_DIFF_PRESSURE_CMD = b"\x36\x1E"
    START_MEASURE_DIFF_PRESSURE_AVG_CMD = b"\x36\x15"

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)
        super().__init__()
        self._pig.i2c_write_device(self._dev, self.CMD_STOP)
        self._start_measure()
        self.log.info("SDP pressure sensor initialized")

    def _start_measure(self):
        try:
            self._pig.i2c_write_device(self._dev,
                                       self.START_MEASURE_FLOW_AVG_CMD)
        except pigpio.error:
            self.log.exception("Could not write start_measure cmd to flow "
                               "sensor. Is the flow sensor connected?")
            raise I2CWriteError("i2c write failed")

        sleep(0.1)

        self.log.info("Started flow sensor measurement")

    def _calculate_pressure(self, pressure_reading):
        differential_psi_pressure =\
            pressure_reading / (self.SCALE_FACTOR_PASCAL)
        differential_cmh2o_pressure =\
            differential_psi_pressure * (1 / self.CMH20_PASCAL_RATIO)
        return differential_cmh2o_pressure

    def pressure_to_flow(self, pressure):
        flow = (abs(pressure) ** 0.5) * self.SYSTEM_RATIO
        if pressure < 0:
            flow = -flow

        return flow

    def twos_complement(self, number):
        b = number.to_bytes(2, byteorder=sys.byteorder, signed=False)
        return int.from_bytes(b, byteorder=sys.byteorder, signed=True)

    def _crc8(self, data):
        crc = self.CRC_INIT_VALUE

        for b in data:
            crc = crc ^ b
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ self.CRC_POLYNOMIAL) & 0xFF
                else:
                    crc = crc << 1
        return crc

    def read(self):
        """ Returns pressure as flow """
        try:
            read_size, pressure_raw =\
                self._pig.i2c_read_device(self._dev, self.MEASURE_BYTE_COUNT)

            if read_size >= self.MEASURE_BYTE_COUNT:
                pressure_reading = (pressure_raw[0] << 8) | (pressure_raw[1])
                pressure_reading = self.twos_complement(pressure_reading)
                expected_crc = pressure_raw[2]
                crc_calc = self._crc8(pressure_raw[:2])
                if not crc_calc == expected_crc:
                    print('bad crc')
                return (self.pressure_to_flow(
                    self._calculate_pressure(pressure_reading)))
            else:
                self.log.error("Pressure sensor's measure data not ready")

        except pigpio.error:
            self.log.exception("Could not read from pressure sensor. "
                               "Is the pressure sensor connected?")
            raise I2CReadError("i2c write failed")
