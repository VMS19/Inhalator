from drivers.hce_pressure_sensor import HcePressureSensor
import logging


def main():
    logging.basicConfig(level=logging.DEBUG)
    hce = HcePressureSensor()
    pressure = hce.read()
    print(pressure)


if __name__ == "__main__":
    main()
