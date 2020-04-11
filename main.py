import multiprocessing
import argparse
import logging
import signal
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from threading import Event

import psutil

from drivers.driver_factory import DriverFactory
from data.configurations import Configurations
from data.measurements import Measurements
from data.events import Events
from application import Application
from algo import Sampler
from wd_task import WdTask
from alert_peripheral_handler import AlertPeripheralHandler
import errors
from drivers.null_driver import NullDriver

BYTES_IN_MB = 2 ** 20
BYTES_IN_GB = 2 ** 30

# the Honeywell differential pressure sensor is very noisy, so we've applied
# some averaging of the last samples to make the graph smoother
NOISY_DP_SENSOR_SAMPLES = 6


def monitor(target, args, output_path):
    worker_process = multiprocessing.Process(target=target, args=[args])
    worker_process.start()
    p = psutil.Process(worker_process.pid)

    # log memory usage of `worker_process` every 10 seconds
    # save the data in MB units
    with open(output_path, 'w') as out:
        out.write("timestamp,memory usage [MB]\n")

    while worker_process.is_alive():
        with open(output_path, 'a') as out:
            timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            out.write(f"{timestamp},{p.memory_info().rss / BYTES_IN_MB}\n")
        time.sleep(10)

    worker_process.join()


def configure_logging(level):
    config = Configurations.instance()

    logger = logging.getLogger()
    logger.setLevel(level)
    # create file handler which logs even debug messages
    file_handler = RotatingFileHandler('inhalator.log',
                                       maxBytes=BYTES_IN_GB,
                                       backupCount=1)
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
    parser.add_argument("--memory-usage-output", "-m",
                        help="To run memory usage analysis for application,"
                             "give path to output csv file")
    parser.add_argument(
        "--debug", "-d",
        help="Whether to save the sensor values to a CSV file (inhalator.csv)",
        action='store_true')
    args = parser.parse_args()
    args.verbose = max(0, logging.WARNING - (10 * args.verbose))
    return args


def handle_sigterm(signum, frame):
    log = logging.getLogger()
    log.warning("Received SIGTERM. Exiting")
    Application.instance().exit()


def start_app(args):
    signal.signal(signal.SIGTERM, handle_sigterm)
    events = Events()
    measurements = Measurements(args.sample_rate if args.simulate else Application.HARDWARE_SAMPLE_RATE)
    arm_wd_event = Event()
    log = configure_logging(args.verbose)

    # Initialize all drivers, or mocks if in simulation mode
    simulation = args.simulate is not None
    if simulation:
        log.info("Running in simulation mode!")
        log.info("Sensor Data Source: %s", args.simulate)
        log.info("Error probability: %s", args.error)

    drivers = None
    try:
        drivers = DriverFactory(simulation_mode=simulation,
                                simulation_data=args.simulate,
                                error_probability=args.error)

        # Must initialize mux before pressure and flow drivers! do not reorder
        try:
            # mux driver is singleton. initialize it and driver factory cache it
            drivers.acquire_driver("mux")
        except errors.I2CDeviceNotFoundError:
            pass

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
            a2d = drivers.acquire_driver("a2d")
        except errors.SPIDriverInitError:
            a2d = drivers.acquire_driver("null")

        timer = drivers.acquire_driver("timer")

        try:
            rtc = drivers.acquire_driver("rtc")
        except errors.InhalatorError:
            rtc = drivers.acquire_driver("null")

        try:
            if not isinstance(rtc, NullDriver):
                rtc.set_system_time()
        except ValueError:
            pass

        alert_driver = drivers.acquire_driver("alert")

        if any(isinstance(driver, NullDriver)
               for driver in (pressure_sensor, flow_sensor, watchdog, a2d, rtc)):
            alert_driver.set_system_fault_alert(value=False, mute=False)

        AlertPeripheralHandler(events, drivers).subscribe()
        sampler = Sampler(measurements=measurements, events=events,
                          flow_sensor=flow_sensor,
                          pressure_sensor=pressure_sensor,
                          a2d=a2d, timer=timer,
                          save_sensor_values=args.debug,
                          average_window=NOISY_DP_SENSOR_SAMPLES)

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


def main():
    args = parse_args()
    if args.memory_usage_output:
        monitor(start_app, args, args.memory_usage_output)

    else:
        start_app(args)


if __name__ == '__main__':
    main()
