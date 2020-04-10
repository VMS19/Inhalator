import logging

from data.configurations import Configurations
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
    SYSTEM_RATIO_SCALE = 36.55

    def __init__(self):
        super().__init__()
        self._calibration_offset = 0
        log.info("HSC pressure sensor initialized")

    def set_calibration_offset(self, offset):
        self._calibration_offset = offset

    def _pressure_to_flow(self, pressure_cmh2o):
        # Add offset
        pressure_cmh2o -= self._calibration_offset

        # Convert to flow value
        flow = (abs(pressure_cmh2o) ** 0.5) * self.SYSTEM_RATIO_SCALE

        # Add sign for flow direction
        if pressure_cmh2o < 0:
            flow = -flow

        return flow

    def read_differential_pressure(self):
        return super(HscPressureSensor, self).read()

    def read(self):
        dp_cmh2o = self.read_differential_pressure()
        return self._pressure_to_flow(dp_cmh2o)
