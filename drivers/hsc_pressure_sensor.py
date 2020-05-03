import logging
from math import copysign

from logic.computations import RunningAvg
from .honeywell_pressure_sensor import HoneywellPressureSensor

log = logging.getLogger(__name__)

# the Honeywell differential pressure sensor is very noisy, so we've applied
# some averaging of the last samples to make the graph smoother
NOISY_DP_SENSOR_SAMPLES = 6


class HscPressureSensor(HoneywellPressureSensor):
    """Driver class for HSCMRRD006MD2A3 differential pressure sensor.

    Returns data in mbar units, gets converted to inch of water.
    """
    MUX_PORT = 1
    I2C_ADDRESS = 0x28
    MAX_RANGE_PRESSURE = 6  # 6 millibar
    MIN_RANGE_PRESSURE = -6  # -6 millibar
    MAX_OUT_PRESSURE = 0x399A
    MIN_OUT_PRESSURE = 0x666
    SENSITIVITY = float(MAX_RANGE_PRESSURE - MIN_RANGE_PRESSURE) /\
        float(MAX_OUT_PRESSURE - MIN_OUT_PRESSURE)
    MBAR_CMH2O_RATIO = 1.0197162129779
    MBAR_INH2O_RATIO = 0.40146307866177
    CONVERTION_RATIO = MBAR_INH2O_RATIO
    SYSTEM_RATIO_SCALE = 36.55

    def __init__(self):
        super().__init__()
        self._calibration_offset = 0
        log.info("HSC pressure sensor initialized")

        self._avg_flow = RunningAvg(max_samples=NOISY_DP_SENSOR_SAMPLES)

    def set_calibration_offset(self, offset):
        self._calibration_offset = offset

    def get_calibration_offset(self):
        return self._calibration_offset

    def pressure_to_flow(self, pressure_inh2o):
        flow = (abs(pressure_inh2o) ** 0.5) * self.SYSTEM_RATIO_SCALE
        return copysign(flow, pressure_inh2o)

    def flow_to_pressure(self, flow):
        return copysign((flow / self.SYSTEM_RATIO_SCALE) ** 2, flow)

    def read_differential_pressure(self):
        return super(HscPressureSensor, self).read()

    def read(self):
        dp_inh2o = self.read_differential_pressure() - self._calibration_offset
        return self._avg_flow.process(self.pressure_to_flow(dp_inh2o))
