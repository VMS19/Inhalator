import csv

import logging

from drivers.mocks.sinus import sinus, truncate, add_noise, zero


def generate_data_from_file(sensor, file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield float(row[sensor])


def production(func):
    @property
    def check_for_mock(*args):
        self = args[0]
        if self.mock:
            driver = getattr(self, f"mock_{func.__name__}", None)
            if driver is None:
                raise ValueError(f"Unsupported driver {func.__name__}")
            return driver

        return func(*args)

    return check_for_mock


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

    def __init__(self, simulation_mode, simulation_data=None, error_probability=0):
        self.mock = simulation_mode
        if simulation_data is None:
            simulation_data = 'sinus'
        self.simulation_data = simulation_data  # can be either `sinus` or file path
        self.error_probability = error_probability
        self.drivers_cache = {}
        self.log = logging.getLogger(self.__class__.__name__)

    def _acquire_driver(self, driver_class, *args, **kwargs):
        """
        Get a driver. The drivers are lazily created and cached.
        :param driver_class: The driver class.
        :return: The appropriate driver object.
        """
        key = (driver_class.__name__, self.mock)
        driver = self.drivers_cache.get(key)
        if driver is not None:
            return driver

        driver = driver_class(*args, **kwargs)
        self.drivers_cache[key] = driver
        return driver

    def close_all_drivers(self):
        for (driver_name, ismock), driver in self.drivers_cache.items():
            if not ismock:
                try:
                    driver.close()
                    self.log.info("Closed {} driver".format(driver_name))
                except Exception:
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

    def generate_mock_pressure_data(self):
        samples = sinus(
            sample_rate=self.MOCK_SAMPLE_RATE_HZ,
            amplitude=self.MOCK_PRESSURE_AMPLITUDE,
            freq=self.MOCK_BPM / 60.0)

        # upper limit is `PIP - PEEP` and not simply PIP because we will raise
        # the _entireacquire_driver signal by PEEP later
        samples = truncate(
            samples, lower_limit=0, upper_limit=self.MOCK_PIP - self.MOCK_PEEP)

        # Raise by PEEP so it will be the baseline
        samples = [s + self.MOCK_PEEP for s in samples]
        return add_noise(samples, self.MOCK_NOISE_SIGMA)

    def generate_mock_pressure_data_noiseless(self):
        samples = sinus(
            sample_rate=self.MOCK_SAMPLE_RATE_HZ,
            amplitude=self.MOCK_PRESSURE_AMPLITUDE,
            freq=self.MOCK_BPM / 60.0)

        # upper limit is `PIP - PEEP` and not simply PIP because we will raise
        # the entire signal by PEEP later
        samples = truncate(
            samples, lower_limit=0, upper_limit=self.MOCK_PIP - self.MOCK_PEEP)

        # Raise by PEEP so it will be the baseline
        return [s + self.MOCK_PEEP for s in samples]

    def generate_mock_air_flow_data(self):
        samples = sinus(
            self.MOCK_SAMPLE_RATE_HZ,
            self.MOCK_AIRFLOW_AMPLITUDE,
            self.MOCK_BPM / 60)
        return add_noise(samples, self.MOCK_NOISE_SIGMA)

    def generate_mock_air_flow_data_noiseless(self):
        samples = sinus(
            self.MOCK_SAMPLE_RATE_HZ,
            self.MOCK_AIRFLOW_AMPLITUDE,
            self.MOCK_BPM / 60)
        return samples

    def generate_mock_a2d_data(self):
        samples = sinus(
            self.MOCK_SAMPLE_RATE_HZ,
            self.MOCK_O2_SATURATION_AMPLITUDE,
            self.MOCK_BPM / 60)
        samples = truncate(
            samples, lower_limit=self.MOCK_O2_SATURATION_LOWER_LIMIT,
            upper_limit=self.MOCK_O2_SATURATION_AMPLITUDE)
        return add_noise(samples, self.MOCK_NOISE_SIGMA)

    def generate_mock_a2d_data_noiseless(self):
        samples = sinus(
            self.MOCK_SAMPLE_RATE_HZ,
            self.MOCK_O2_SATURATION_AMPLITUDE,
            self.MOCK_BPM / 60)
        samples = truncate(
            samples, lower_limit=self.MOCK_O2_SATURATION_LOWER_LIMIT,
            upper_limit=self.MOCK_O2_SATURATION_AMPLITUDE)
        return samples

    @production
    def timer(self):
        from drivers.timer import Timer
        return self._acquire_driver(Timer)

    @production
    def pressure(self):
        from drivers.abp_pressure_sensor import AbpPressureSensor
        return self._acquire_driver(AbpPressureSensor)

    @production
    def flow(self):
        from drivers.hsc_pressure_sensor import HscPressureSensor
        return self._acquire_driver(HscPressureSensor)

    @production
    def a2d(self):
        from drivers.ads7844_a2d import Ads7844A2D
        return self._acquire_driver(Ads7844A2D)

    @production
    def wd(self):
        from drivers.wd_driver import WdDriver
        return self._acquire_driver(WdDriver)

    @production
    def alert(self):
        from drivers.alert_driver import AlertDriver
        return self._acquire_driver(AlertDriver)

    @production
    def differential_pressure(self):
        from drivers.hsc_pressure_sensor import HscPressureSensor
        return self._acquire_driver(HscPressureSensor)

    @production
    def rtc(self):
        from drivers.rv8523_rtc import Rv8523Rtc
        return self._acquire_driver(Rv8523Rtc)

    @production
    def mux(self):
        from drivers.mux_i2c import MuxI2C
        return self._acquire_driver(MuxI2C)

    @property
    def mock_differential_pressure(self):
        from drivers.mocks.sensor import DifferentialPressureMockSensor

        if self.simulation_data == 'dead':
            data = self.generate_mock_dead_man()
        elif self.simulation_data == 'sinus':
            data = self.generate_mock_air_flow_data()
        else:
            data = generate_data_from_file('flow', self.simulation_data)

        return self._acquire_driver(DifferentialPressureMockSensor, data)

    @property
    def mock_pressure(self):
        from drivers.mocks.sensor import MockSensor

        data_source = self.simulation_data
        if data_source == 'dead':
            data = self.generate_mock_dead_man()
        elif data_source == 'sinus':
            data = self.generate_mock_pressure_data()
        elif data_source == 'noiseless_sinus':
            data = self.generate_mock_pressure_data_noiseless()
        elif data_source == "noise":
            data = self.generate_mock_noise()
        else:
            data = generate_data_from_file('pressure', data_source)

        return self._acquire_driver(MockSensor, data, error_probability=self.error_probability)

    @property
    def mock_flow(self):
        from drivers.mocks.sensor import DifferentialPressureMockSensor

        if self.simulation_data == 'dead':
            data = self.generate_mock_dead_man()
        elif self.simulation_data == 'sinus':
            data = self.generate_mock_air_flow_data()
        elif self.simulation_data == 'noiseless_sinus':
            data = self.generate_mock_air_flow_data_noiseless()
        elif self.simulation_data == "noise":
            data = self.generate_mock_noise()
        else:
            data = generate_data_from_file('flow', self.simulation_data)

        return self._acquire_driver(DifferentialPressureMockSensor, data,
                                    error_probability=self.error_probability)

    @property
    def mock_timer(self):
        from drivers.mocks.timer import MockTimer

        if self.simulation_data == "sinus" or self.simulation_data == "dead" \
                or self.simulation_data == "noiseless_sinus":
            time_series = [0, 1 / self.MOCK_SAMPLE_RATE_HZ]
        elif self.simulation_data == "noise":
            time_series = [0, self.VALID_SLOPE_INTERVALS]
        else:
            time_series = generate_data_from_file("time elapsed (seconds)", self.simulation_data)

        return self._acquire_driver(MockTimer, time_series=time_series)

    @property
    def mock_a2d(self):
        from drivers.mocks.a2d_mock import MockA2D
        return self._acquire_driver(MockA2D)

    @property
    def mock_wd(self):
        from drivers.mocks.mock_wd_driver import MockWdDriver
        return self._acquire_driver(MockWdDriver)

    @property
    def mock_alert(self):
        from drivers.mocks.mock_alert_driver import MockAlertDriver
        return self._acquire_driver(MockAlertDriver)

    @property
    def null(self):
        from drivers.null_driver import NullDriver
        return self._acquire_driver(NullDriver)

    @property
    def mock_rtc(self):
        from drivers.mocks.mock_rv8523_rtc_driver import MockRv8523Rtc
        return self._acquire_driver(MockRv8523Rtc)

    @property
    def mock_mux(self):
        from unittest.mock import MagicMock
        return self._acquire_driver(MagicMock)
