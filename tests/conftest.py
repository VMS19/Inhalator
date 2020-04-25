import pytest

from algo import Sampler
from data.configurations import ConfigurationManager
from data.events import Events
from data.measurements import Measurements
from drivers.driver_factory import DriverFactory


@pytest.fixture
def config_path(tmpdir):
    return tmpdir / "config.json"


@pytest.fixture
def events():
    e = Events()
    e.alerts_queue.initial_uptime = 0
    return e


@pytest.fixture
def configuration_manager(config_path, events):
    return ConfigurationManager.initialize(events, config_path)


@pytest.fixture
def default_config(configuration_manager, events):
    # For the sake of tests, some of the defaults are really not appropriate
    # and should be modified
    c = configuration_manager.config
    c.boot_alert_grace_time = 0
    return c


@pytest.fixture
def config(default_config):
    return default_config


@pytest.fixture
def measurements(default_config):
    return Measurements(default_config.graph_seconds)


@pytest.fixture
def driver_factory(data):
    return DriverFactory(simulation_mode=True, simulation_data=data)


@pytest.fixture
def sim_sampler(driver_factory, config, measurements, events):
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(config, measurements, events, flow_sensor,
                      pressure_sensor, a2d, timer)
    return sampler
