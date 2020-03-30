"""Save log from the debug port into a file."""
import csv
import re
import socket
import pickle
import logging
import argparse
import datetime

PORT = 7777
LOG_LEVEL = logging.DEBUG
LOG_FILE_PATH = '/tmp/inhalator.log'
CSV_FILE_OUTPUT = '/tmp/inhalator.csv'

DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


def configure_logger(log_level, output_file_path):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(output_file_path)
    fh.setLevel(log_level)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s >> %(message)s', datefmt=DATE_FORMAT)
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


GENERIC_LOG_REGEX = "'(?P<timestamp>.*) >> {message}"
SENSOR_TO_REGEX = {
    'pressure': GENERIC_LOG_REGEX.format(message='pressure sensor value: (?P<value>.*)'),
    'flow': GENERIC_LOG_REGEX.format(message='flow sensor value: (?P<value>.*)'),
    'oxygen': GENERIC_LOG_REGEX.format(message='oxygen sensor value: (?P<value>.*)')
}


def sample_generator(log_file_path):
    with open(log_file_path) as log_file:
        for log_line in log_file:
            for sensor, regex in SENSOR_TO_REGEX.items():
                match = re.search(regex, log_line)
                if match is not None:
                    yield sensor, match.group('timestamp'), match.group('value')
                    break


def time_diff(timestamp1, timestamp2):
    ts1 = datetime.datetime.strptime(timestamp1, DATE_FORMAT)
    ts2 = datetime.datetime.strptime(timestamp2, DATE_FORMAT)
    return (ts2 - ts1).total_seconds()


def log_file_to_csv(log_file_path, csv_file_path):
    current_ts = None
    values = [None] * 3

    with open(csv_file_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['timestamp', 'pressure', 'flow', 'oxygen'])
        for sensor, timestamp, value in sample_generator(log_file_path):
            if current_ts is None:
                current_ts = timestamp

            if current_ts != timestamp and current_ts is not None:
                writer.writerow([time_diff(current_ts, timestamp)] + values)

                current_ts = timestamp
                values = [None] * 3

            values[list(SENSOR_TO_REGEX.keys()).index(sensor)] = value


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
        logger.info("Saving log into CSV file %s" % cli_args.csv_output)
        log_file_to_csv(cli_args.output, cli_args.csv_output)


if __name__ == '__main__':
    main()
