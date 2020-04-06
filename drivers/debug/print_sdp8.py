import time
import logging

from drivers.sdp8_pressure_sensor import SdpPressureSensor


def main():
    logging.basicConfig(level=logging.DEBUG)
    sdp = SdpPressureSensor()
    while True:
        pressure = sdp.read()
        print(pressure)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
