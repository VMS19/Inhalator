import time
import logging

from drivers.abp_pressure_sensor import AbpPressureSensor


def main():
    logging.basicConfig(level=logging.DEBUG)
    abp = None

    try:
        abp = AbpPressureSensor()
        while True:
            pressure = abp.read()
            print(pressure)
            time.sleep(0.2)
    finally:
        if abp is not None:
            abp.close()


if __name__ == "__main__":
    main()
