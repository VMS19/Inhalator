import re

LOG_FILE = './pig_data'

SENSORS_TO_TEMPLATE = {
    'pressure': 'Pressure: (.*)',
    'flow': 'Flow: (.*)',
    'oxygen': "Breathed: (.*)"
}


def file_sampling_generator(sensor, log_file_path=LOG_FILE):
    with open(log_file_path, 'r') as log_file:
        for sample_line in log_file:
            match = re.search(SENSORS_TO_TEMPLATE[sensor], sample_line)
            if match is not None:
                yield float(match.group(1))
