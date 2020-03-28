import re

from drivers.mocks.sinus import sinus, truncate, add_noise


def generate_data_from_file(sensor, file_path):
    sensors_to_regex = {
        'pressure': 'Pressure: (.*)',
        'flow': 'Flow: (.*)',
        'oxygen': "Breathed: (.*)"
    }

    with open(file_path, 'r') as log_file:
        for sample_line in log_file:
            match = re.search(sensors_to_regex[sensor], sample_line)
            if match is not None:
                yield float(match.group(1))


class DriverFactory(object):
    MOCK_SAMPLE_RATE_HZ = 50  # 20ms between reads assumed
    MOCK_BPM = 15  # Breathes per minutes to simulate
    MOCK_NOISE_SIGMA = 0.5  # Play with it to get desired result
    MOCK_AIRFLOW_AMPLITUDE = 20
    MOCK_PRESSURE_AMPLITUDE = 25
    MOCK_PIP = 25  # Peak Intake Pressure
    MOCK_PEEP = 3  # Positive End-Expiratory Pressure

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    @classmethod
    def instance(cls):
        return cls.__instance

    def __init__(self, simulation_mode, simulation_data='sinus'):
        self.mock = simulation_mode
        self.simulation_data = simulation_data  # can be either `sinus` or file path
        self.drivers_cache = {}

    def get_driver(self, driver_name):
        """
        Get a driver by its name. The drivers are lazily created and cached.
        :param driver_name: The driver name. E.g "aux", "wd", "pressure"
        :return: The appropriate driver object.
        """
        key = (driver_name, self.mock)
        driver = self.drivers_cache.get(key)
        if driver is not None:
            return driver
        method_name = "get{}_{}_driver".format(("_mock" if self.mock else ""), driver_name)
        method = getattr(self, method_name, None)
        if method is None:
            raise ValueError("Unsupported driver {}".format(driver_name))
        driver = method()
        self.drivers_cache[key] = driver
        return driver

    def generate_mock_pressure_data(self):
        samples = sinus(
            sample_rate=self.MOCK_SAMPLE_RATE_HZ,
            amplitude=self.MOCK_PRESSURE_AMPLITUDE,
            freq=self.MOCK_BPM / 60.0)

        # upper limit is `PIP - PEEP` and not simply PIP because we will raise
        # the entire signal by PEEP later
        samples = truncate(
            samples, lower_limit=0, upper_limit=self.MOCK_PIP - self.MOCK_PEEP)

        # Raise by PEEP so it will be the baseline
        samples = [s + self.MOCK_PEEP for s in samples]
        return add_noise(samples, self.MOCK_NOISE_SIGMA)

    def generate_mock_air_flow_data(self):
        samples = sinus(
            self.MOCK_SAMPLE_RATE_HZ,
            self.MOCK_AIRFLOW_AMPLITUDE,
            self.MOCK_BPM / 60)
        samples = truncate(
            samples, lower_limit=0, upper_limit=self.MOCK_AIRFLOW_AMPLITUDE)
        return add_noise(samples, self.MOCK_NOISE_SIGMA)

    @staticmethod
    def get_pressure_driver():
        from drivers.hce_pressure_sensor import HcePressureSensor
        return HcePressureSensor()

    @staticmethod
    def get_flow_driver():
        from drivers.sfm3200_flow_sensor import Sfm3200
        return Sfm3200()

    @staticmethod
    def get_wd_driver():
        from drivers.wd_driver import WdDriver
        return WdDriver()

    @staticmethod
    def get_aux_driver():
        from drivers.aux_sound import SoundViaAux
        return SoundViaAux.instance()

    def get_mock_pressure_driver(self):
        from drivers.mocks.sensor import MockSensor
        data_source = self.simulation_data
        if data_source == 'sinus':
            data = self.generate_mock_pressure_data()
        else:
            data = generate_data_from_file('pressure', data_source)
        return MockSensor(data)

    def get_mock_flow_driver(self):
        from drivers.mocks.sensor import MockSensor
        simulation_data = self.simulation_data
        if simulation_data == 'sinus':
            data = self.generate_mock_air_flow_data()
        else:
            data = generate_data_from_file('flow', simulation_data)
        return MockSensor(data)

    @staticmethod
    def get_mock_wd_driver():
        from drivers.mocks.mock_wd_driver import MockWdDriver
        return MockWdDriver()

    @staticmethod
    def get_mock_aux_driver():
        from unittest.mock import MagicMock
        return MagicMock()
