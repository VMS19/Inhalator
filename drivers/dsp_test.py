from dsp_pressure_sensor import DspPressureSensor
import logging


def main():
    logging.basicConfig(level=logging.DEBUG)
    dsp = DspPressureSensor()
    pressure = dsp.read()
    print(pressure)


if __name__ == "__main__":
    main()
