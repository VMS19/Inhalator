import pigpio
import logging
import time
from errors import PiGPIOInitError, I2CDeviceNotFoundError, I2CReadError

log = logging.getLogger(__name__)


class DspPressureSensor(object):
    """Driver class for ABPMAND001PG2A3 Flow sensor."""
    I2C_BUS = 1
    I2C_ADDRESS = 0x25
    MEASURE_BYTE_COUNT = 0x2
    CMD_TRIGGERED_DIFFERENTIAL_PRESSURE = b"\x36\x2f"
    CMD_CONT_DIFFERENTIAL_PRESSURE = b"\x36\x1e"
    CMD_STOP = b"\x3F\xF9"
    CRC_POLYNOMIAL = 0x31
    CRC_INIT_VALUE = 0xFF
    SCALE_FACTOR_PASCAL = 60
    CMH20_PASCAL_RATIO = 98.0665

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
            log.error("Could not open i2c connection to pressure sensor."
                      "Is it connected?")
            raise I2CDeviceNotFoundError("i2c connection open failed")
            #self._pig.i2c_write_device(self._dev, self.CMD_STOP)
            time.sleep(1)

        log.info("ABP pressure sensor initialized")

    def _calculate_pressure(self, pressure_reading):
        differential_psi_pressure = pressure_reading / (self.SCALE_FACTOR_PASCAL)
        differential_cmh2o_pressure = psi_pressure * (1 / self.CMH20_PASCAL_RATIO)
        return (differential_cmh2o_pressure)

    def _pressure_to_airflow(self, pressure):
        return ***

    def twos_complement(self, number):
        import sys
        b = number.to_bytes(2, byteorder=sys.byteorder, signed=False)
        return int.from_bytes(b, byteorder=sys.byteorder, signed=True)

    def read(self):
        """ Returns pressure as cmh2o """
        try:
            self._pig.i2c_write_device(self._dev, self.CMD_TRIGGERED_DIFFERENTIAL_PRESSURE)
            time.sleep(0.1)
            read_size, pressure_raw = self._pig.i2c_read_device(self._dev, self.MEASURE_BYTE_COUNT)
            #print('read_size',read_size)
            if read_size >= self.MEASURE_BYTE_COUNT:
                pressure_reading = (pressure_raw[0] << 8) | (pressure_raw[1])
                pressure_reading = self.twos_complement(pressure_reading)
                expected_crc = 0  #pressure_raw[2]
                crc_calc = expected_crc  #self._crc8(pressure_reading)
                if not crc_calc == expected_crc:
                    print('bad crc')
                return (self._pressure_to_airflow(
                        self._calculate_pressure(pressure_reading)))
            else:
                # Todo: Do we need to retry reading after a little sleep? (see flow sensor logic)
                log.error("Pressure sensor's measure data not ready")
                raise I2CReadError("Pressure sensor measurement unavailable.")
        except pigpio.error as e:
            log.error("Could not read from pressure sensor. "
                      "Is the pressure sensor connected?.")
            raise I2CReadError("i2c write failed")

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
