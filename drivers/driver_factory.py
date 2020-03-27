class DriverFactory(object):
    MOCK_BPM = 15  # Breathes per minutes to simulate
    MOCK_NOISE_SIGMA = 0.5  # Play with it to get desired result

    def __init__(self, simulation_mode):
        self.simulation_mode = simulation_mode

    def get_driver(self, driver_name):
        if self.simulation_mode:
            return MOCK_DRIVERS_DICT[driver_name]()
        else:
            return REAL_DRIVERS_DICT[driver_name]()

    @classmethod
    def get_pressure_driver(cls):
        from drivers.hce_pressure_sensor import HcePressureSensor
        return HcePressureSensor()

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
        from drivers.mocks.mock_pressure_sensor import MockPressureSensor
        return MockPressureSensor(cls.MOCK_BPM, cls.MOCK_NOISE_SIGMA)

    @classmethod
    def get_mock_flow_driver(cls):
        from drivers.mocks.mock_air_flow_sensor import MockAirFlowSensor
        return MockAirFlowSensor(cls.MOCK_BPM, cls.MOCK_NOISE_SIGMA)

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
