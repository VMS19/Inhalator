import logging

from .honeywell_pressure_sensor import HoneywellPressureSensor

log = logging.getLogger(__name__)


class HscPressureSensor(HoneywellPressureSensor):
    """Driver class for HSC differential pressure sensor."""
    MUX_PORT = 1
    I2C_ADDRESS = 0x28
    MAX_RANGE_PRESSURE = 6  # 6 millibar
    MIN_RANGE_PRESSURE = -6  # -6 millibar
    MAX_OUT_PRESSURE = 0x399A
    MIN_OUT_PRESSURE = 0x666
    SENSITIVITY = float(MAX_RANGE_PRESSURE - MIN_RANGE_PRESSURE) /\
        float(MAX_OUT_PRESSURE - MIN_OUT_PRESSURE)
    MBAR_CMH2O_RATIO = 1.0197162129779
    CMH2O_RATIO = MBAR_CMH2O_RATIO
    SYSTEM_RATIO_SCALE = 33.2
    SYSTEM_RATIO_OFFSET = -6

    def __init__(self):
        super().__init__()
        log.info("HSC pressure sensor initialized")

    def _pressure_to_flow(self, pressure_cmh2o):
        flow = (abs(pressure_cmh2o) ** 0.5) * self.SYSTEM_RATIO_SCALE
        if pressure_cmh2o < 0:
            flow = -flow
        flow += self.SYSTEM_RATIO_OFFSET
        return flow

    def _raw_reading_to_temp(self, raw_temp):
        return (raw_temp * 200/2047) - 50

    def read(self):
        """ Returns pressure as cmh2o """
        try:
            with mux.lock(self.MUX_PORT):
                read_size, pressure_raw = \
                    self._pig.i2c_read_device(self._dev, self.MEASURE_BYTE_COUNT)
            if read_size >= self.MEASURE_BYTE_COUNT:
                pressure_reading = ((pressure_raw[0] & 0x3F) << 8) | (pressure_raw[1])
                dp_cmh2o = self._calculate_pressure(pressure_reading)

                return self._pressure_to_flow(dp_cmh2o)
            else:
                log.warning("Pressure sensor's measure data not ready")
        except pigpio.error as e:
            log.error("Could not read from pressure sensor. "
                      "Is the pressure sensor connected?.")
            raise I2CReadError("i2c write failed") from e

    def read_temperature(self):
        """ Returns temperature """
        try:
            with mux.lock(self.MUX_PORT):
                read_size, pressure_raw = \
                    self._pig.i2c_read_device(self._dev, self.MEASURE_BYTE_COUNT + 2)
            if read_size >= self.MEASURE_BYTE_COUNT:
                temp = (pressure_raw[2] << 3) | ((pressure_raw[3] & 0xE0) >> 5)

                return self._raw_reading_to_temp(temp)
            else:
                log.warning("Pressure sensor's measure data not ready")
        except pigpio.error as e:
            log.error("Could not read from pressure sensor. "
                      "Is the pressure sensor connected?.")
            raise I2CReadError("i2c write failed") from e
