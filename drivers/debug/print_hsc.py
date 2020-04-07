import time
import logging

from drivers.hsc_pressure_sensor import HscPressureSensor


def main():
    logging.basicConfig(level=logging.DEBUG)
    hsc = None

    try:
        hsc = HscPressureSensor()
        while True:
            pressure = hsc.read()
            print(pressure)
            time.sleep(0.2)
    finally:
        if hsc is not None:
            hsc.close()


if __name__ == "__main__":
    main()
