import time
import logging

from drivers.hsc_pressure_sensor import HscPressureSensor


def main():
    logging.basicConfig(level=logging.DEBUG)
    hsc = HscPressureSensor()
    while True:
        pressure = hsc.read()
        print(pressure)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
