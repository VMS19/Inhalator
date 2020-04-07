import logging

from .honeywell_pressure_sensor import HoneywellPressureSensor

log = logging.getLogger(__name__)


class AbpPressureSensor(HoneywellPressureSensor):
    """Driver class for ABPMAND001PG2A3 Flow sensor."""
    I2C_ADDRESS = 0x28
    MAX_RANGE_PRESSURE = 0x1  # 1 psi
    MIN_RANGE_PRESSURE = 0x00  # 0 psi
    MAX_OUT_PRESSURE = 0x399A
    MIN_OUT_PRESSURE = 0x666
    SENSITIVITY = float(MAX_RANGE_PRESSURE - MIN_RANGE_PRESSURE) /\
        float(MAX_OUT_PRESSURE - MIN_OUT_PRESSURE)
    PSI_CMH2O_RATIO = 70.307
    CMH2O_RATIO = PSI_CMH2O_RATIO

    def __init__(self):
        super().__init__()
        log.info("ABP pressure sensor initialized")
