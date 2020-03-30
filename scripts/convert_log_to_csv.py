import re
import csv


def log_to_csv(log_file_path, sensor):
    with open(log_file_path) as log_file:
        for log_line in log_file:
            match = re.search(f'{sensor.title()}: (.*)', log_line)
            if match is not None:
                yield match.group(1)


LOG_FILE_PATH = ''
CSV_PATH = ''

pressures = log_to_csv(LOG_FILE_PATH, 'pressure')
flows = log_to_csv(LOG_FILE_PATH, 'flows')

with open(CSV_PATH, 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['pressure', 'flow'])
    for pressure, flow in zip(pressures, flows):
        writer.writerow([pressure, flow])
