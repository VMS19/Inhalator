from data.configurations import Configurations
from drivers.mocks.sensor import MockSensor


class MockDifferentialPressureSensor(MockSensor):
    SYSTEM_RATIO_SCALE = 36.55
    SYSTEM_RATIO_OFFSET = -0.026

    def _pressure_to_flow(self, pressure_cmh2o):
        flow = (abs(pressure_cmh2o + self.SYSTEM_RATIO_OFFSET) ** 0.5) * self.SYSTEM_RATIO_SCALE
        if pressure_cmh2o < 0:
            flow = -flow
        return flow

    def read_differential_pressure(self):
        """This is kind of weird.

        We read the sinus value in flow, we transfer it back to differential pressure,
        then we add the offset, and the read() function which shows flow, casts once again to flow.
        """
        flow = super(MockDifferentialPressureSensor, self).read()
        # We have to deal with the absolute value
        if flow > 0:
            pressure_cmh2o = (flow / self.SYSTEM_RATIO_SCALE) ** 2 - self.SYSTEM_RATIO_OFFSET

        else:
            pressure_cmh2o = (flow / self.SYSTEM_RATIO_SCALE) ** 2 + self.SYSTEM_RATIO_OFFSET
            pressure_cmh2o *= -1

        return pressure_cmh2o + Configurations.instance().dp_offset


    def read(self):
        return self._pressure_to_flow(self.read_differential_pressure())
