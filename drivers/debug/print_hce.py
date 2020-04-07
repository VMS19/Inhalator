from drivers.hce_pressure_sensor import HcePressureSensor
import logging


def main():
    logging.basicConfig(level=logging.DEBUG)
    hce = None

    try:
        hce = HcePressureSensor()
        pressure = hce.read()
        print(pressure)
    finally:
        if hce is not None:
            hce.close()


if __name__ == "__main__":
    main()
