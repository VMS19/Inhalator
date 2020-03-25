import argparse
import logging
from logging.handlers import RotatingFileHandler
from time import sleep

from drivers.mocks.mock_hce_pressure_sensor import MockHcePressureSensor
from drivers.mocks.mock_sfm3200_flow_sensor import MockSfm3200
from drivers.hce_pressure_sensor import HcePressureSensor
from drivers.sfm3200_flow_sensor import Sfm3200
from data.data_store import DataStore
from gui import GUI
from algo import Sampler
from sound import SoundDevice


def configure_logging(level, store):
    logger = logging.getLogger()
    logger.setLevel(level)
    # create file handler which logs even debug messages
    fh = RotatingFileHandler('inhalator.log', maxBytes=1024 * 100, backupCount=3)
    fh.setLevel(logging.ERROR)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.disabled = not store.log_enabled


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", action="count", default=0)
    parser.add_argument("--simulate", "-s", action='store_true')
    args = parser.parse_args()
    args.verbose = max(0, logging.WARNING - (10 * args.verbose))
    return args


def main():
    args = parse_args()
    store = DataStore()
    configure_logging(args.verbose, store)

    if args.simulate:
        flow_sensor = MockSfm3200()
        pressure_sensor = MockHcePressureSensor()

    else:
        flow_sensor = Sfm3200()
        pressure_sensor = HcePressureSensor()

    sound_device = SoundDevice()
    store.alerts_queue.subscribe(sound_device, sound_device.on_alert)

    gui = GUI(store)

    sampler = Sampler(store, flow_sensor, pressure_sensor)
    gui.render()
    # Wait for GUI to render
    #     time.sleep(5)
    sampler.start()


    while True:
        gui.gui_update()
        sleep(0.02)

if __name__ == '__main__':
    main()
