from dsp_pressure_sensor import DspPressureSensor
import logging
import time

def main():
    logging.basicConfig(level=logging.DEBUG)
    dsp = DspPressureSensor()
    while True:
        pressure = dsp.read()
        print((pressure/60)/100)
        time.sleep(0.2)
    #print('cmh20', pressure/100.0)


if __name__ == "__main__":
    main()
