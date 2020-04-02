from drivers.mux_i2c import MuxI2C
import logging
from sys import argv


def main():
    logging.basicConfig(level=logging.DEBUG)
    mux = MuxI2C()
    mux.switch_port(argv[1])


if __name__ == "__main__":
    main()
