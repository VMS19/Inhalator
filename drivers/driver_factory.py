import re

from drivers.mocks.sinus import sinus, truncate, add_noise


class DriverFactory(object):
    MOCK_SAMPLE_RATE_HZ = 50  # 20ms between reads assumed
    MOCK_BPM = 15  # Breathes per minutes to simulate
    MOCK_NOISE_SIGMA = 0.5  # Play with it to get desired result
    MOCK_AIRFLOW_AMPLITUDE = 20
    MOCK_PRESSURE_AMPLITUDE = 25
    MOCK_PIP = 25  # Peak Intake Pressure
    MOCK_PEEP = 3  # Positive End-Expiratory Pressure

    def __init__(self, simulation_mode, simulation_data='sinus'):
        self.simulation_mode = simulation_mode
        self.simulation_data = simulation_data  # can be either `sinus` or file path

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
    def generate_data_from_file(cls, sensor, file_path):
        SENSORS_TO_REGEX = {
            'pressure': 'Pressure: (.*)',
            'flow': 'Flow: (.*)',
            'oxygen': "Breathed: (.*)"
        }

        with open(file_path, 'r') as log_file:
            for sample_line in log_file:
                match = re.search(SENSORS_TO_REGEX[sensor], sample_line)
                if match is not None:
                    yield float(match.group(1))

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
    def get_aux_driver(cls):
        from drivers.aux_sound import SoundViaAux
        return SoundViaAux.instance()

    @classmethod
    def get_mock_pressure_driver(cls, data_source):
        from drivers.mocks.sensor import MockSensor
        if data_source == 'sinus':
            data = cls.generate_mock_pressure_data()

        else:
            data = cls.generate_data_from_file('pressure', data_source)

        return MockSensor(data)

    @classmethod
    def get_mock_flow_driver(cls, data_source):
        from drivers.mocks.sensor import MockSensor
        if data_source == 'sinus':
            data = cls.generate_mock_air_flow_data()

        else:
            data = cls.generate_data_from_file('flow', data_source)

        return MockSensor(data)

    @classmethod
    def get_mock_wd_driver(cls):
        from drivers.mocks.mock_wd_driver import MockWdDriver
        return MockWdDriver()

    @classmethod
    def get_mock_aux_driver(cls):
        from unittest.mock import MagicMock
        return MagicMock()

REAL_DRIVERS_DICT = {"pressure": DriverFactory.get_pressure_driver,
                     "flow": DriverFactory.get_flow_driver,
                     "wd": DriverFactory.get_wd_driver,
                     "aux": DriverFactory.get_aux_driver}


# We don't want to mock sound in development mode, unit-tests call the mock functions
# explicitly, if we want to support multiple program modes (demo/test/real/develop/etc...)
# it should be done in a future issue
MOCK_DRIVERS_DICT = {"pressure": DriverFactory.get_mock_pressure_driver,
                     "flow": DriverFactory.get_mock_flow_driver,
                     "wd": DriverFactory.get_mock_wd_driver,
                     "aux": DriverFactory.get_aux_driver}
