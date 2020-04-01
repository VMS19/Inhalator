"""Copy log files from the raspberry to a local CSV file."""
import argparse
import csv
import datetime
import ftplib
import itertools
import logging
import re

TRACE = logging.DEBUG - 1
logging.addLevelName(TRACE, 'TRACE')

RPI_IP = '192.168.43.234'

LOG_LEVEL = 'TRACE'
LOG_FILE_PATH = 'inhalator.log'
CSV_FILE_OUTPUT = 'inhalator.csv'

DATE_FORMAT = '%Y-%m-%d %H:%M:%S,%f'

GENERIC_LOG_REGEX = "(?P<timestamp>.*) - (?P<module>.*) - (?P<level>.*) - {message}"
SENSORS_LOG_ORDER = ['flow', 'pressure', 'oxygen']
SENSOR_TO_REGEX = {
    'flow': GENERIC_LOG_REGEX.format(message='flow: (?P<value>.*)'),
    'pressure': GENERIC_LOG_REGEX.format(message='pressure: (?P<value>.*)'),
    'oxygen': GENERIC_LOG_REGEX.format(message='oxygen: (?P<value>.*)')
}


def configure_logger(log_level):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    # create console handler with a higher log level
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s >> %(message)s')
    stream_handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(stream_handler)
    return logger


def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--csv_output', default=CSV_FILE_OUTPUT)
    parser.add_argument('-l', '--level', default=LOG_LEVEL)
    parser.add_argument('-o', '--output', default=LOG_FILE_PATH)
    parser.add_argument('-i', '--ip', default=RPI_IP)
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
    values = []
    start_ts = None
    last_timestamp = None
    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['timestamp', 'unix_time (seconds)', 'time elapsed (seconds)', 'flow', 'pressure', 'oxygen'])
        for timestamp, value in sample_generator(log_file_path):
            if start_ts is None:
                start_ts = timestamp

            if len(values) == len(SENSORS_LOG_ORDER):
                writer.writerow([last_timestamp, unix_time(timestamp), time_diff(start_ts, timestamp)] + values)
                values = []

            values.append(value)
            last_timestamp = timestamp

        values = values + [None] * (len(SENSORS_LOG_ORDER) - len(values))
        writer.writerow([timestamp, unix_time(timestamp), time_diff(start_ts, timestamp)] + values)


def copy_log_files(output_file, ip, user='pi', passwd='raspberry'):
    """Copy log file from the Raspberry pi using FTP.

    Copying all log files from the remote RPi, and merging them into one file locally.

    Args:
        output_file (str): the output log file.
        ip (str): ip address of the raspberry pi.
        user (str): raspberry pi user.
        passwd (str): raspberry pi password.
    """
    with ftplib.FTP(ip, user, passwd) as ftp:
        ftp.cwd('Inhalator')
        log_files = ftp.nlst('inhalator.log*')
        log_files.sort(reverse=True)
        open(output_file, 'w').close()  # create empty file
        with open(output_file, 'ab') as out_file:
            for log_file in log_files:
                ftp.retrbinary(f'RETR {log_file}', out_file.write)


def main():
    cli_args = parse_cli_args()
    logger = configure_logger(cli_args.level)

    # Copy files from RPi to local storage.
    logger.info(f"Copying log files from Raspberry(%s) to %s", cli_args.ip, cli_args.output)
    copy_log_files(cli_args.output, cli_args.ip)

    # parse file.
    logger.info("Saving CSV file at %s", cli_args.csv_output)
    log_file_to_csv(cli_args.output, cli_args.csv_output)


if __name__ == '__main__':
    main()
