"""Save log from the debug port into a file."""
import csv
import itertools
import re
import socket
import pickle
import logging
import argparse
import datetime

TRACE = logging.DEBUG - 1
logging.addLevelName(TRACE, 'TRACE')

PORT = 7777
LOG_LEVEL = 'TRACE'
LOG_FILE_PATH = 'inhalator.log'
CSV_FILE_OUTPUT = 'inhalator.csv'

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
    file_handler = logging.FileHandler(output_file_path, mode='w')
    file_handler.setLevel(log_level)
    # create console handler with a higher log level
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s >> %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
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


def unix_time(timestamp):
    return datetime.datetime.strptime(timestamp, DATE_FORMAT).timestamp() * 1000


def log_file_to_csv(log_file_path, csv_file_path):
    start_ts = None
    values = []
    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['timestamp', 'unix_time (seconds)', 'time elapsed (seconds)', 'flow', 'pressure', 'oxygen'])
        for timestamp, value in sample_generator(log_file_path):
            if start_ts is None:
                start_ts = timestamp

            if len(values) == len(SENSORS_LOG_ORDER):
                writer.writerow([timestamp, unix_time(timestamp), time_diff(start_ts, timestamp)] + values)
                values = []

            values.append(value)

        values = values + [None] * (len(SENSORS_LOG_ORDER) - len(values))
        writer.writerow([timestamp, unix_time(timestamp), time_diff(start_ts, timestamp)] + values)


def get_connection(port):
    sock = socket.socket()
    sock.bind(('0.0.0.0', port))
    sock.listen()
    x, _ = sock.accept()
    return x


def main():
    cli_args = parse_cli_args()
    logger = configure_logger(cli_args.level, cli_args.output)

    try:
        logger.info("Waiting for module to start sending logs.")
        sock = get_connection(cli_args.port)
        while True:
            try:
                raw_log = sock.recv(2 ** 16)
                log_meta = pickle.loads(raw_log[4:])  # Remove header
                logger.handle(logging.makeLogRecord(log_meta))

            except ConnectionResetError:
                logger.warning("Connection reset, waiting for new connection from module")
                sock = get_connection(cli_args.port)

    except KeyboardInterrupt:
        # Save to CSV file.
        logger.info("Saving log into CSV file %s", cli_args.csv_output)
        log_file_to_csv(cli_args.output, cli_args.csv_output)


if __name__ == '__main__':
    main()
