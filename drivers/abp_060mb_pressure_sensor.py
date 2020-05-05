import logging

from .honeywell_pressure_sensor import HoneywellPressureSensor

log = logging.getLogger(__name__)


class AbpPressureSensor(HoneywellPressureSensor):
    """Driver class for ABPMJNN060MG2A3 Flow sensor."""
    MUX_PORT = 0
    I2C_ADDRESS = 0x28
    MAX_RANGE_PRESSURE = 60  # 60 mbar
    MIN_RANGE_PRESSURE = 00  # 0 mbar
    MAX_OUT_PRESSURE = 0x399A
    MIN_OUT_PRESSURE = 0x666
    SENSITIVITY = float(MAX_RANGE_PRESSURE - MIN_RANGE_PRESSURE) /\
        float(MAX_OUT_PRESSURE - MIN_OUT_PRESSURE)
    MBAR_CMH2O_RATIO = 1.0197162129779
    CMH2O_RATIO = MBAR_CMH2O_RATIO

    def __init__(self):
        super().__init__()
        log.info("ABP pressure sensor initialized")
