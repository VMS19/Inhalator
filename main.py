import argparse
import logging
import signal
import socket

from logging.handlers import RotatingFileHandler
from time import sleep

from drivers.mocks.mock_hce_pressure_sensor import MockHcePressureSensor
from drivers.mocks.mock_sfm3200_flow_sensor import MockSfm3200
from data.data_store import DataStore
from gui import Application
from algo import Sampler
from sound import SoundDevice

class BroadcastHandler(logging.handlers.DatagramHandler):
    '''
    A handler for the python logging system which is able to broadcast packets.
    '''

    def makeSocket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        return sock

def configure_logging(level, store):
    logger = logging.getLogger()
    logger.setLevel(level)
    # create file handler which logs even debug messages
    fh = RotatingFileHandler('inhalator.log', maxBytes=1024 * 100, backupCount=3)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(level)
    # create socket handler to broadcast logs
    sh = BroadcastHandler('255.255.255.255', store.debug_port)
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
    logger.disabled = not store.log_enabled


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", default=0)
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
    configure_logging(args.verbose, store)
    sound_device = SoundDevice(store)

    app = Application(store)
    flow_sensor = MockSfm3200()
    pressure_sensor = MockHcePressureSensor()
    sampler = Sampler(store, flow_sensor, pressure_sensor)
    app.render()
    sampler.start()

    while app.should_run:
        try:
            app.gui_update()
            sleep(0.02)
        except KeyboardInterrupt:
            app.exit()
            sound_device.stop_ringing()
            break


if __name__ == '__main__':
    main()
