import logging
from math import copysign, sqrt

from logic.computations import RunningAvg
from .honeywell_pressure_sensor import HoneywellPressureSensor

log = logging.getLogger(__name__)

# the Honeywell differential pressure sensor is very noisy, so we've applied
# some averaging of the last samples to make the graph smoother
NOISY_DP_SENSOR_SAMPLES = 6


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
    DENSITY_AIR = 1.205  # Kg/m3. in 20 degrees celsius, 1 atm
    DENSITY_O2 = 1.331  # Kg/m3. in 20 degrees celsius, 1 atm
    O2_IN_AIR = 0.2095  # 20.95%
    DENSITY_REST_OF_GASSES = \
        (DENSITY_AIR - O2_IN_AIR * DENSITY_O2) / (1 - O2_IN_AIR)

    def __init__(self):
        super().__init__()
        self._calibration_offset = 0
        self._o2_compensation_ratio = 1
        self._o2_saturation = 21
        log.info("HSC pressure sensor initialized")

        self._avg_flow = RunningAvg(max_samples=NOISY_DP_SENSOR_SAMPLES)

    def set_calibration_offset(self, offset):
        self._calibration_offset = offset

    def get_calibration_offset(self):
        return self._calibration_offset

    def set_o2_compensation(self, o2_percentage):
        """Update oxygen saturation, for flow calculation correction.

        Calculate the density of air with updated oxygen saturation,
        and calculate gas density compensation ratio, to be used
        for correct flow calculation based on Bernoulli's law.
        """
        if abs(self._o2_saturation - o2_percentage) < 3:
            # Don't waste time on minor o2 saturation changes
            return

        self._o2_saturation = o2_percentage

        o2_percentage /= 100
        correct_density = \
            (o2_percentage * self.DENSITY_O2 +
             (1 - o2_percentage) * self.DENSITY_REST_OF_GASSES)

        self._o2_compensation_ratio = sqrt(self.DENSITY_AIR / correct_density)
        log.debug("HSC differential pressure sensor updated compensation ratio "
                  "for %d%% oxygen saturation: %f", self._o2_saturation,
                  self._o2_compensation_ratio)

    def pressure_to_flow(self, pressure_cmh2o):
        flow = (sqrt(abs(pressure_cmh2o))) * self.SYSTEM_RATIO_SCALE\
            * self._o2_compensation_ratio
        return copysign(flow, pressure_cmh2o)

    def flow_to_pressure(self, flow):
        return copysign((flow / self.SYSTEM_RATIO_SCALE) ** 2, flow)

    def read_differential_pressure(self):
        return super(HscPressureSensor, self).read()

    def read(self):
        dp_cmh2o = self.read_differential_pressure() - self._calibration_offset
        return self._avg_flow.process(self.pressure_to_flow(dp_cmh2o))
