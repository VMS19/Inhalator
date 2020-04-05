import csv

import logging

from drivers.mocks.sinus import sinus, truncate, add_noise, zero


def generate_data_from_file(sensor, file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield float(row[sensor])


class DriverFactory(object):
    MOCK_SAMPLE_RATE_HZ = 50  # 20ms between reads assumed
    MOCK_BPM = 15  # Breathes per minutes to simulate
    MOCK_NOISE_SIGMA = 0.5  # Play with it to get desired result
    MOCK_AIRFLOW_AMPLITUDE = 20
    MOCK_PRESSURE_AMPLITUDE = 25
    MOCK_PIP = 25  # Peak Intake Pressure
    MOCK_PEEP = 3  # Positive End-Expiratory Pressure
    BASE_O2_SATURATION = 20
    OFFSET_O2_SATURATION = 3
    MOCK_O2_SATURATION_AMPLITUDE = BASE_O2_SATURATION + OFFSET_O2_SATURATION
    MOCK_O2_SATURATION_LOWER_LIMIT = BASE_O2_SATURATION - OFFSET_O2_SATURATION
    VALID_SLOPE_INTERVALS = 0.05

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    @classmethod
    def instance(cls):
        return cls.__instance

    def __init__(self, simulation_mode, simulation_data='sinus',  error_probability=0):
        self.mock = simulation_mode
        self.simulation_data = simulation_data  # can be either `sinus` or file path
        self.error_probability = error_probability
        self.drivers_cache = {}
        self.log = logging.getLogger(self.__class__.__name__)

    def acquire_driver(self, driver_name):
        """
        Get a driver by its name. The drivers are lazily created and cached.
        :param driver_name: The driver name. E.g "aux", "wd", "pressure"
        :return: The appropriate driver object.
        """
        key = (driver_name, self.mock)
        driver = self.drivers_cache.get(key)
        if driver is not None:
            return driver
        method_name = f"get{'_mock' if self.mock else ''}_{driver_name}_driver"
        method = getattr(self, method_name, None)
        if method is None:
            raise ValueError(f"Unsupported driver {driver_name}")
        driver = method()
        self.drivers_cache[key] = driver
        return driver

    def close_all_drivers(self):
        for (driver_name, ismock), driver in self.drivers_cache.items():
            if not ismock:
                try:
                    driver.close()
                    self.log.info("Closed {} driver.".format(driver_name))
                except:
                    self.log.exception("Error while closing driver {}"
                                  .format(driver_name))

    def generate_mock_dead_man(self):
        return zero(
            sample_rate=self.MOCK_SAMPLE_RATE_HZ,
            amplitude=self.MOCK_PRESSURE_AMPLITUDE,
            freq=self.MOCK_BPM / 60.0)

    def generate_mock_noise(self):
        samples = [0] * 1000
        noise_samples = add_noise(samples, self.MOCK_NOISE_SIGMA)
        return [10 + x for x in noise_samples]

    def generate_mock_pressure_data(self, noise=True):
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
        if noise:
            return add_noise(samples, self.MOCK_NOISE_SIGMA)

        else:
            return samples

    def generate_mock_flow_data(self, noise=True):
        samples = sinus(
            self.MOCK_SAMPLE_RATE_HZ,
            self.MOCK_AIRFLOW_AMPLITUDE,
            self.MOCK_BPM / 60)

        if noise:
            return add_noise(samples, self.MOCK_NOISE_SIGMA)

        else:
            return samples

    def generate_mock_oxygen_data(self, noise=True):
        samples = sinus(
            self.MOCK_SAMPLE_RATE_HZ,
            self.MOCK_O2_SATURATION_AMPLITUDE,
            self.MOCK_BPM / 60)
        samples = truncate(
            samples, lower_limit=self.MOCK_O2_SATURATION_LOWER_LIMIT,
            upper_limit=self.MOCK_O2_SATURATION_AMPLITUDE)

        if noise:
            return add_noise(samples, self.MOCK_NOISE_SIGMA)

        return samples

    @staticmethod
    def get_timer_driver():
        from drivers.timer import Timer
        return Timer()

    def get_mock_timer_driver(self):
        from drivers.mocks.timer import MockTimer
        if self.simulation_data == "sinus" or self.simulation_data == "dead" \
                or self.simulation_data == "noiseless_sinus":
            time_series = [0, 1 / self.MOCK_SAMPLE_RATE_HZ]
        elif self.simulation_data == "noise":
            time_series = [0, self.VALID_SLOPE_INTERVALS]
        else:
            time_series = generate_data_from_file("time elapsed (seconds)", self.simulation_data)
        return MockTimer(time_series=time_series)

    @staticmethod
    def get_pressure_driver():
        from drivers.abp_pressure_sensor import AbpPressureSensor
        return AbpPressureSensor()

    @staticmethod
    def get_flow_driver():
        from drivers.sfm3200_flow_sensor import Sfm3200
        return Sfm3200()

    @staticmethod
    def get_oxygen_a2d_driver():
        from drivers.ads7844_a2d import Ads7844A2D
        return Ads7844A2D()

    @staticmethod
    def get_wd_driver():
        from drivers.wd_driver import WdDriver
        return WdDriver()

    @staticmethod
    def get_aux_driver():
        from drivers.aux_sound import SoundViaAux
        return SoundViaAux.instance()

    @staticmethod
    def get_differential_pressure_driver():
        from drivers.sdp8_pressure_sensor import SdpPressureSensor
        return SdpPressureSensor()

    def get_mock_driver(self, driver_name):
        from drivers.mocks.sensor import MockSensor
        data_source = self.simulation_data
        if data_source == 'dead':
            data = self.generate_mock_dead_man()
        elif data_source == 'sinus' or data_source == 'noiseless_sinus':
            noise = "noiseless" not in data_source
            method_name = f"generate_mock_{driver_name}_data"
            method = getattr(self, method_name, None)
            data = method(noise=noise)
        elif data_source == "noise":
            data = self.generate_mock_noise()
        else:
            data = generate_data_from_file(driver_name, data_source)
        return MockSensor(data, error_probability=self.error_probability)

    def get_mock_differential_pressure_driver(self):
        return self.get_mock_driver('flow')

    def get_mock_pressure_driver(self):
        return self.get_mock_driver('pressure')

    def get_mock_flow_driver(self):
        return self.get_mock_driver('flow')

    def get_mock_oxygen_a2d_driver(self):
        return self.get_mock_driver('oxygen')

    @staticmethod
    def get_mock_wd_driver():
        from drivers.mocks.mock_wd_driver import MockWdDriver
        return MockWdDriver()

    @staticmethod
    def get_mock_aux_driver():
        from drivers.aux_sound import SoundViaAux
        return SoundViaAux.instance()
