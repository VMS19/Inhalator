import logging
from logging.handlers import RotatingFileHandler
from time import sleep

from mocks.mock_hce_pressure_sensor import MockHcePressureSensor
from mocks.mock_sfm3200_flow_sensor import MockSfm3200
from data_store import DataStore
from gui import GUI, mainloop
from algo import Sampler


def configure_logging(store):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
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


def main():
    store = DataStore()
    configure_logging(store)
    gui = GUI(store)
    flow_sensor = MockSfm3200()
    pressure_sensor = MockHcePressureSensor()
    sampler = Sampler(store, flow_sensor, pressure_sensor, gui.alert)
    gui.render()
    # Wait for GUI to render
    #     time.sleep(5)
    sampler.start()

    while True:
        gui.gui_update()
        # sleep(0.02)
    #
    # mainloop()


if __name__ == '__main__':
    main()
