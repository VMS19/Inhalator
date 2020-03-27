from drivers.mocks.sinus import sinus, truncate, add_noise


class DriverFactory(object):
    MOCK_SAMPLE_RATE_HZ = 50  # 20ms between reads assumed
    MOCK_BPM = 15  # Breathes per minutes to simulate
    MOCK_NOISE_SIGMA = 0.5  # Play with it to get desired result
    MOCK_AIRFLOW_AMPLITUDE = 20
    MOCK_PRESSURE_AMPLITUDE = 0.25
    MOCK_PIP = 25  # Peak Intake Pressure
    MOCK_PEEP = 3  # Positive End-Expiratory Pressure

    def __init__(self, simulation_mode):
        self.simulation_mode = simulation_mode

    def get_driver(self, driver_name):
        if self.simulation_mode:
            return MOCK_DRIVERS_DICT[driver_name]()
        else:
            return REAL_DRIVERS_DICT[driver_name]()

    @classmethod
    def generate_mock_pressure_data(cls):
        samples = sinus(
            sample_rate=cls.MOCK_SAMPLE_RATE_HZ,
            amplitude=cls.MOCK_PRESSURE_AMPLITUDE,
            freq=cls.MOCK_BPM / 60.0)

        # upper limit is `PIP - PEEP` and not simply PIP because we will raise
        # the entire signal by PEEP later
        samples = truncate(
            samples, lower_limit=0, upper_limit=cls.MOCK_PIP - cls.MOCK_PEEP)

        # Raise by PEEP so it will be the baseline
        samples = [s + cls.MOCK_PEEP for s in samples]
        return add_noise(samples, cls.MOCK_NOISE_SIGMA)

    @classmethod
    def generate_mock_air_flow_data(cls):
        samples = sinus(
            cls.MOCK_SAMPLE_RATE_HZ,
            cls.MOCK_AIRFLOW_AMPLITUDE,
            cls.MOCK_BPM / 60)
        samples = truncate(
            samples, lower_limit=0, upper_limit=cls.MOCK_AIRFLOW_AMPLITUDE)
        return add_noise(samples, cls.MOCK_NOISE_SIGMA)

    @classmethod
    def get_pressure_driver(cls):
        from drivers.abp_pressure_sensor import AbpPressureSensor
        return AbpPressureSensor()

    @classmethod
    def get_flow_driver(cls):
        from drivers.sfm3200_flow_sensor import Sfm3200
        return Sfm3200()

    @classmethod
    def get_wd_driver(cls):
        from drivers.wd_driver import WdDriver
        return WdDriver()

    @classmethod
    def get_mock_pressure_driver(cls):
        from drivers.mocks.sensor import MockSensor
        return MockSensor(cls.generate_mock_pressure_data())

    @classmethod
    def get_mock_flow_driver(cls):
        from drivers.mocks.sensor import MockSensor
        return MockSensor(cls.generate_mock_air_flow_data())

    @classmethod
    def get_mock_wd_driver(cls):
        from drivers.mocks.mock_wd_driver import MockWdDriver
        return MockWdDriver()


REAL_DRIVERS_DICT = {"pressure": DriverFactory.get_pressure_driver,
                     "flow": DriverFactory.get_flow_driver,
                     "wd": DriverFactory.get_wd_driver}

MOCK_DRIVERS_DICT = {"pressure": DriverFactory.get_mock_pressure_driver,
                     "flow": DriverFactory.get_mock_flow_driver,
                     "wd": DriverFactory.get_mock_wd_driver}
