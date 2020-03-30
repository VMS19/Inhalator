import re
import csv
import sys
from itertools import zip_longest


def log_to_csv(log_file_path, sensor):
    with open(log_file_path) as log_file:
        for log_line in log_file:
            match = re.search(f'{sensor.title()}: (.*)', log_line)
            if match is not None:
                yield match.group(1)


LOG_FILE_PATH = sys.argv[1]
CSV_PATH = sys.argv[2]

pressures = log_to_csv(LOG_FILE_PATH, 'Pressure')
flows = log_to_csv(LOG_FILE_PATH, 'Flow')

with open(CSV_PATH, 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['pressure', 'flow'])
    for pressure, flow in zip(pressures, flows):
        writer.writerow([pressure, flow])
