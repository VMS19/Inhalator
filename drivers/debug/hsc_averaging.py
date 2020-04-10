import time
import logging
import csv
import time

from drivers.hsc_pressure_sensor import HscPressureSensor

FILE_NAME = "hsc_flow_output.csv"

def main():
    logging.basicConfig(level=logging.DEBUG)
    hsc = None
    last_time = time.time()

    with open(FILE_NAME,'w') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp","differential_pressure"])

        try:
            hsc = HscPressureSensor()
            while True:
                #x = time.time()
                pressure = hsc.read()
                #ts = time.time() - x
                #print(f'seconds={ts}')
                #print(pressure)
                writer.writerow([time.time(), pressure])
        finally:
            if hsc is not None:
                hsc.close()


if __name__ == "__main__":
    main()
