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
import errors

BYTES_IN_GB = 2 ** 30


def configure_logging(level):
    config = Configurations.instance()

    logger = logging.getLogger()
    logger.setLevel(level)
    # create file handler which logs even debug messages
    file_handler = RotatingFileHandler('inhalator.log',
                                       maxBytes=BYTES_IN_GB,
                                       backupCount=7)
    file_handler.setLevel(level)
    # create console handler
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    steam_handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(steam_handler)
    logger.disabled = not config.log_enabled
    return logger


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", default=0)
    sim_options = parser.add_argument_group(
        "simulation", "Options for data simulation")
    sim_options.add_argument("--simulate", "-s", nargs='?', type=str, const='sinus',
                             help="data simulation source. "
                                  "Can be either `sinus` (default), `dead`, or path to a CSV file.")
    sim_options.add_argument(
        "--error", "-e", type=float,
        help="The probability of error in each driver", default=0)
    sim_options.add_argument(
        "--sample-rate", "-r",
        help="The speed, in samples-per-seconds, in which the simulation will "
             "be played at. Useful for slowing down the simulation to see what "
             "is going on, or speeding up to run simulation faster",
        type=float, default=22)
    parser.add_argument(
        "--fps", "-f",
        help="Frames-per-second for the application to render",
        type=int, default=25)
    args = parser.parse_args()
    args.verbose = max(0, logging.WARNING - (10 * args.verbose))
    return args


def handle_sigterm(signum, frame):
    log = logging.getLogger()
    log.warning("Received SIGTERM. Exiting")
    Application.instance().exit()


def main():
    signal.signal(signal.SIGTERM, handle_sigterm)
    events = Events()
    args = parse_args()
    measurements = Measurements(args.sample_rate if args.simulate else Application.HARDWARE_SAMPLE_RATE)
    arm_wd_event = Event()
    log = configure_logging(args.verbose)

    # Initialize all drivers, or mocks if in simulation mode
    simulation = args.simulate is not None or os.uname()[1] != 'raspberrypi'
    if simulation:
        log.info("Running in simulation mode!")
        log.info("Sensor Data Source: %s", args.simulate)
        log.info("Error probability: %s", args.error)

    drivers = None
    try:
        drivers = DriverFactory(simulation_mode=simulation,
                                simulation_data=args.simulate,
                                error_probability=args.error)

        try:
            pressure_sensor = drivers.acquire_driver("pressure")
        except errors.I2CDeviceNotFoundError:
            pressure_sensor = drivers.acquire_driver("null")

        try:
            flow_sensor = drivers.acquire_driver("differential_pressure")
        except errors.I2CDeviceNotFoundError:
            flow_sensor = drivers.acquire_driver("null")

        watchdog = drivers.acquire_driver("wd")
        try:
            oxygen_a2d = drivers.acquire_driver("oxygen_a2d")
        except errors.SPIDriverInitError:
            oxygen_a2d = drivers.acquire_driver("null")
        timer = drivers.acquire_driver("timer")

        sampler = Sampler(measurements=measurements, events=events,
                          flow_sensor=flow_sensor,
                          pressure_sensor=pressure_sensor,
                          oxygen_a2d=oxygen_a2d, timer=timer)

        app = Application(measurements=measurements,
                          events=events,
                          arm_wd_event=arm_wd_event,
                          drivers=drivers,
                          sampler=sampler,
                          simulation=simulation,
                          fps=args.fps,
                          sample_rate=args.sample_rate)

        watchdog_task = WdTask(watchdog, arm_wd_event)
        watchdog_task.start()

        app.run()

    finally:
        if drivers is not None:
            drivers.close_all_drivers()


if __name__ == '__main__':
    main()
