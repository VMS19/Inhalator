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
    SYSTEM_RATIO_SCALE = 36.55
    SYSTEM_RATIO_OFFSET = -0.026

    def __init__(self):
        super().__init__()
        log.info("HSC pressure sensor initialized")

    def _pressure_to_flow(self, pressure_cmh2o):
        flow = (abs(pressure_cmh2o + self.SYSTEM_RATIO_OFFSET) ** 0.5) * self.SYSTEM_RATIO_SCALE
        if pressure_cmh2o < 0:
            flow = -flow
        return flow
