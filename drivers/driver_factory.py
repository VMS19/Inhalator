import csv
import logging
import functools
from cached_property import cached_property

from drivers.mocks.sinus import sinus, truncate, add_noise, zero


def generate_data_from_file(sensor, file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield float(row[sensor])


def production(func):
    @property
    @functools.wraps(func)
    def check_for_mock(self, *args):
        if self.mock:
            return getattr(self, f"mock_{func.__name__}")

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
        # the entire signal by PEEP later
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
        return cached_property(self.timer, Timer)

    @production
    def pressure(self):
        from drivers.abp_pressure_sensor import AbpPressureSensor
        return cached_property(self.pressure, AbpPressureSensor)

    @production
    def flow(self):
        from drivers.hsc_pressure_sensor import HscPressureSensor
        return cached_property(self.flow, HscPressureSensor)

    differential_pressure = flow

    @production
    def a2d(self):
        from drivers.ads7844_a2d import Ads7844A2D
        return cached_property(self.a2d, Ads7844A2D)

    @production
    def wd(self):
        from drivers.wd_driver import WdDriver
        return cached_property(self.wd, WdDriver)

    @production
    def alert(self):
        from drivers.alert_driver import AlertDriver
        return cached_property(self.alert, AlertDriver)

    @production
    def rtc(self):
        from drivers.rv8523_rtc import Rv8523Rtc
        return cached_property(self.rtc, Rv8523Rtc)

    @production
    def mux(self):
        from drivers.mux_i2c import MuxI2C
        return cached_property(self.mux, MuxI2C)

    def _get_data(self, data_source, data_type):
        source = data_source.get(self.simulation_data)
        if source is not None:
            return source()
        return generate_data_from_file(data_type, self.simulation_data)

    @property
    def mock_pressure(self):
        from drivers.mocks.sensor import MockSensor

        data_sources = {'dead': self.generate_mock_dead_man,
                        'sinus': self.generate_mock_pressure_data,
                        'noiseless_sinus': self.generate_mock_pressure_data_noiseless,
                        'noise': self.generate_mock_noise}

        data = self._get_data(data_sources, 'pressure')

        return MockSensor(data, error_probability=self.error_probability)

    @property
    def mock_flow(self):
        from drivers.mocks.sensor import DifferentialPressureMockSensor

        data_sources = {'dead': self.generate_mock_dead_man,
                        'sinus': self.generate_mock_air_flow_data,
                        'noiseless_sinus': self.generate_mock_air_flow_data_noiseless,
                        'noise': self.generate_mock_noise}

        data = self._get_data(data_sources, 'flow')

        return DifferentialPressureMockSensor(data,
                                              error_probability=self.error_probability)

    @property
    def mock_timer(self):
        from drivers.mocks.timer import MockTimer

        if self.simulation_data in ["sinus", "dead", "noiseless_sinus"]:
            time_series = [0, 1 / self.MOCK_SAMPLE_RATE_HZ]
        elif self.simulation_data == "noise":
            time_series = [0, self.VALID_SLOPE_INTERVALS]
        else:
            time_series = generate_data_from_file("time elapsed (seconds)", self.simulation_data)

        return MockTimer(time_series=time_series)

    @property
    def mock_a2d(self):
        from drivers.mocks.a2d_mock import MockA2D
        return MockA2D()

    @property
    def mock_wd(self):
        from drivers.mocks.mock_wd_driver import MockWdDriver
        return MockWdDriver()

    @property
    def mock_alert(self):
        from drivers.mocks.mock_alert_driver import MockAlertDriver
        return MockAlertDriver()

    @property
    def null(self):
        from drivers.null_driver import NullDriver
        return NullDriver()

    @property
    def mock_rtc(self):
        from drivers.mocks.mock_rv8523_rtc_driver import MockRv8523Rtc
        return MockRv8523Rtc()

    @property
    def mock_mux(self):
        from unittest.mock import MagicMock
        return MagicMock()
