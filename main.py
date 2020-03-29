import os
import argparse
import logging
import signal
import socket
from logging.handlers import RotatingFileHandler
from time import sleep

from drivers.driver_factory import DriverFactory
from data.configurations import Configurations
from data.measurements import Measurements
from data.events import Events
from application import Application
from algo import Sampler
from drivers.aux_sound import SoundViaAux


class BroadcastHandler(logging.handlers.DatagramHandler):
    '''
    A handler for the python logging system which is able to broadcast packets.
    '''

    def send(self, s):
        try:
            super().send(s)

        except OSError as e:
            if e.errno != 101:  # Network is unreachable
                raise e

    def makeSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        return sock


def configure_logging(level):
    config = Configurations.instance()

    logger = logging.getLogger()
    logger.setLevel(level)
    # create file handler which logs even debug messages
    fh = RotatingFileHandler('inhalator.log', maxBytes=1024 * 100, backupCount=3)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # create socket handler to broadcast logs
    sh = BroadcastHandler('255.255.255.255', config.debug_port)
    sh.setLevel(level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    sh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.addHandler(sh)
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

    app = Application(measurements=measurements,
                      events=events,
                      watchdog=watchdog,
                      drivers=drivers)
    sampler = Sampler(measurements=measurements, events=events,
                      flow_sensor=flow_sensor, pressure_sensor=pressure_sensor,
                      oxygen_a2d=oxygen_a2d)

    app.render()
    sampler.start()

    while app.should_run:
        try:
            app.gui_update()
            sleep(0.02)
        except KeyboardInterrupt:
            break

    app.exit()
    drivers.get_driver("aux").stop()


if __name__ == '__main__':
    main()
