from sdp8_pressure_sensor import SdpPressureSensor
import logging
import time

def main():
    logging.basicConfig(level=logging.DEBUG)
    sdp = SdpPressureSensor()
    while True:
        pressure = sdp.read()
        print(pressure)
        time.sleep(0.2)

if __name__ == "__main__":
    main()
