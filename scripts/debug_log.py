"""Save log from the debug port into a file."""
import csv
import itertools
import re
import socket
import pickle
import logging
import argparse
import datetime

NOTICE = logging.DEBUG - 1
logging.addLevelName(NOTICE, 'NOTICE')

PORT = 7777
LOG_LEVEL = 'NOTICE'
LOG_FILE_PATH = '/tmp/inhalator.log'
CSV_FILE_OUTPUT = '/tmp/inhalator.csv'

DATE_FORMAT = '%Y-%m-%d %H:%M:%S,%f'

GENERIC_LOG_REGEX = "(?P<timestamp>.*) >> {message}"
SENSORS_LOG_ORDER = ['flow', 'pressure', 'oxygen']
SENSOR_TO_REGEX = {
    'flow': GENERIC_LOG_REGEX.format(message='flow: (?P<value>.*)'),
    'pressure': GENERIC_LOG_REGEX.format(message='pressure: (?P<value>.*)'),
    'oxygen': GENERIC_LOG_REGEX.format(message='oxygen: (?P<value>.*)')
}


def configure_logger(log_level, output_file_path):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(output_file_path, mode='w')
    fh.setLevel(log_level)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s >> %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--csv_output', default=CSV_FILE_OUTPUT)
    parser.add_argument('-p', '--port', default=PORT)
    parser.add_argument('-l', '--level', default=LOG_LEVEL)
    parser.add_argument('-o', '--output', default=LOG_FILE_PATH)
    return parser.parse_args()


def sample_generator(log_file_path):
    sensors = itertools.cycle(SENSORS_LOG_ORDER)
    sensor = next(sensors)
    with open(log_file_path) as log_file:
        for log_line in log_file:
            match = re.search(SENSOR_TO_REGEX[sensor], log_line)
            if match is not None:
                yield match.group('timestamp'), match.group('value')
                sensor = next(sensors)


def time_diff(timestamp1, timestamp2):
    if type(timestamp1) is str:
        timestamp1 = datetime.datetime.strptime(timestamp1, DATE_FORMAT)

    if type(timestamp2) is str:
        timestamp2 = datetime.datetime.strptime(timestamp2, DATE_FORMAT)

    return (timestamp2 - timestamp1).total_seconds()


def log_file_to_csv(log_file_path, csv_file_path):
    start_ts = None
    values = []
    with open(csv_file_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['timestamp', 'flow', 'pressure', 'oxygen'])
        for timestamp, value in sample_generator(log_file_path):
            if start_ts is None:
                start_ts = timestamp

            if len(values) == 3:
                writer.writerow([time_diff(start_ts, timestamp)] + values)
                values = []

            values.append(value)

        values = values + [None] * (3 - len(values))
        writer.writerow([time_diff(start_ts, timestamp)] + values)


def main():
    cli_args = parse_cli_args()
    logger = configure_logger(cli_args.level, cli_args.output)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', PORT))

    try:
        while True:
            raw_log = sock.recv(2 ** 16)
            log_meta = pickle.loads(raw_log[4:])  # Remove header
            logger.handle(logging.makeLogRecord(log_meta))

    except KeyboardInterrupt:
        # Save to CSV file.
        logger.info("Saving log into CSV file %s", cli_args.csv_output)
        log_file_to_csv(cli_args.output, cli_args.csv_output)


if __name__ == '__main__':
    main()
