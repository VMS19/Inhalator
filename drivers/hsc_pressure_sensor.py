import logging

from computation import RunningAvg
from tail_detection import TailDetector
from .driver_factory import DriverFactory
from .honeywell_pressure_sensor import HoneywellPressureSensor
from .timer import Timer

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

    def __init__(self):
        super().__init__()
        self._calibration_offset = 0
        self.tail_detector = TailDetector()
        self._avg_dp_cmh2o = RunningAvg(max_samples=NOISY_DP_SENSOR_SAMPLES)
        log.info("HSC pressure sensor initialized")

    def set_calibration_offset(self, offset):
        self._calibration_offset = offset

    def pressure_to_flow(self, pressure_cmh2o):
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
        avg_dp_chmh2o = self._avg_dp_cmh2o.process(dp_cmh2o)
        ts = DriverFactory(simulation_mode=True).acquire_driver("timer").get_current_time()
        offset = self.tail_detector.process(avg_dp_chmh2o - self._calibration_offset, ts)
        return self.pressure_to_flow(avg_dp_chmh2o - offset)
