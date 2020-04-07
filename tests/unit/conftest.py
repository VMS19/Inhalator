import os

from algo import Sampler
from drivers.driver_factory import DriverFactory

SIMULATION_FOLDER = "simulation"
THIS_DIR = os.path.dirname(__file__)


def create_sampler(data_source, events, measurements):
    if data_source.endswith(".csv"):
        data_source = os.path.join(THIS_DIR, SIMULATION_FOLDER, data_source)
    driver_factory = DriverFactory(
        simulation_mode=True, simulation_data=data_source)
    flow_sensor = driver_factory.acquire_driver("flow")
    pressure_sensor = driver_factory.acquire_driver("pressure")
    a2d = driver_factory.acquire_driver("a2d")
    timer = driver_factory.acquire_driver("timer")
    sampler = Sampler(measurements, events, flow_sensor, pressure_sensor,
                      a2d, timer)
    return sampler
