import os
import argparse
import logging
import signal
from logging.handlers import RotatingFileHandler
from threading import Event

from drivers.driver_factory import DriverFactory
from data.configurations import Configurations
from data.measurements import Measurements
from data.events import Events
from application import Application
from algo import Sampler
from wd_task import WdTask

GB_IN_BYTES = 2 ** 30


def configure_logging(level):
    config = Configurations.instance()

    logger = logging.getLogger()
    logger.setLevel(level)
    # create file handler which logs even debug messages
    fh = RotatingFileHandler('inhalator.log',
                             maxBytes=GB_IN_BYTES,
                             backupCount=10)
    fh.setLevel(logging.DEBUG)
    # # create console handler with a higher log level
    # ch = logging.StreamHandler()
    # ch.setLevel(level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    # logger.addHandler(ch)
    logger.disabled = not config.log_enabled
    return logger


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", default=0)
    parser.add_argument("--simulate", "-s", action='store_true')
    parser.add_argument("--data", '-d', default='sinus')
    args = parser.parse_args()
    args.verbose = max(0, logging.WARNING - (10 * args.verbose))
    return args


def handle_sigterm(signum, frame):
    log = logging.getLogger()
    log.warning("Received SIGTERM. Exiting")
    Application.instance().exit()


def main():
    measurements = Measurements()
    events = Events()
    signal.signal(signal.SIGTERM, handle_sigterm)
    args = parse_args()
    arm_wd_event = Event()
    log = configure_logging(args.verbose)

    # Initialize all drivers, or mocks if in simulation mode
    simulation = args.simulate or os.uname()[1] != 'raspberrypi'
    if simulation:
        log.info("Running in simulation mode! simulating: "
                 "flow, pressure sensors, and watchdog")
    drivers = DriverFactory(
        simulation_mode=simulation, simulation_data=args.data)

    pressure_sensor = drivers.get_driver("pressure")
    flow_sensor = drivers.get_driver("flow")

    watchdog = drivers.get_driver("wd")
    oxygen_a2d = drivers.get_driver("oxygen_a2d")

    sampler = Sampler(measurements=measurements, events=events,
                      flow_sensor=flow_sensor, pressure_sensor=pressure_sensor,
                      oxygen_a2d=oxygen_a2d)

    app = Application(measurements=measurements,
                      events=events,
                      arm_wd_event=arm_wd_event,
                      drivers=drivers,
                      sampler=sampler)

    watchdog_task = WdTask(watchdog, arm_wd_event)
    watchdog_task.start()

    app.run()


if __name__ == '__main__':
    main()
