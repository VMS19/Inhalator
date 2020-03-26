import os
import argparse
import logging
import signal

from logging.handlers import RotatingFileHandler
from time import sleep

from drivers.driver_factory import DriverFactory
from data.data_store import DataStore
from gui import Application
from algo import Sampler
from sound import SoundDevice


def configure_logging(level, store):
    logger = logging.getLogger()
    logger.setLevel(level)
    # create file handler which logs even debug messages
    fh = RotatingFileHandler('inhalator.log', maxBytes=1024 * 100, backupCount=3)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.disabled = not store.log_enabled
    return logger


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", default=0)
    parser.add_argument("--simulate", "-s", action='store_true')
    args = parser.parse_args()
    args.verbose = max(0, logging.WARNING - (10 * args.verbose))
    return args


def handle_sigterm(signum, frame):
    log = logging.getLogger()
    log.warning("Received SIGTERM. Exiting")
    Application.instance().exit()


def main():
    store = DataStore.load_from_config()
    signal.signal(signal.SIGTERM, handle_sigterm)
    args = parse_args()
    store = DataStore()
    log = configure_logging(args.verbose, store)

    # Initialize all drivers, or mocks if in simulation mode
    if args.simulate or os.uname()[1] is not 'raspberrypi':
        log.info("Running in simulation mode! simulating: "
                 "flow, pressure sensors, and watchdog")
        drivers = DriverFactory(simulation_mode=True)

    else:
        drivers = DriverFactory(simulation_mode=False)

    pressure_sensor = drivers.get_driver("pressure")
    flow_sensor = drivers.get_driver("flow")
    watchdog = drivers.get_driver("wd")

    sound_device = SoundDevice()
    store.alerts_queue.subscribe(sound_device, sound_device.on_alert)

    app = Application(store, watchdog)

    sampler = Sampler(store, flow_sensor, pressure_sensor)
    app.render()
    sampler.start()

    while app.should_run:
        try:
            app.gui_update()
            sleep(0.02)
        except KeyboardInterrupt:
            app.exit()
            break


if __name__ == '__main__':
    main()
