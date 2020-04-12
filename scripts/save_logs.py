"""Copy log files from the raspberry to a local CSV file."""
import csv
import ftplib
import io
import logging
import argparse
import re
from pathlib import Path

RPI_IP = '192.168.43.234'

CSV_FILE_OUTPUT = 'inhalator.csv'
ALERTS_CSV_OUTPUT = 'alerts.csv'
LOG_FILE_PATH = 'inhalator.log'

REMOTE_LOG_FILE = 'Inhalator/inhalator.log'
REMOTE_HEADERS_FILE = 'Inhalator/headers.csv'


class AlertsExtractor:
    GENERIC_LOG_REGEX = "(?P<timestamp>.*) - (?P<module>.*) - (?P<level>.*) - {message}"
    ALERTS_ORDER = ['low_pressure', 'high_pressure', 'low_volume', 'high_volume']
    ALERTS_TO_REGEX = {
        'low_pressure': GENERIC_LOG_REGEX.format(message='pressure too low (?P<value>.*),'),
        'high_pressure': GENERIC_LOG_REGEX.format(message='pressure too high (?P<value>.*),'),
        'low_volume': GENERIC_LOG_REGEX.format(message='volume too low (?P<value>.*),'),
        'high_volume': GENERIC_LOG_REGEX.format(message='volume too high (?P<value>.*),')
    }

    def __init__(self, log_file_path, output_csv_file_path, logger):
        self.log_path = log_file_path
        self.csv_path = output_csv_file_path
        self.logger = logger

    def alerts_generator(self):
        done = 0
        total_size = Path(self.log_path).stat().st_size
        with open(self.log_path) as log_file:
            for i, log_line in enumerate(log_file):
                done += len(log_line)
                if i % 5_000 == 0:
                    percentage = round(((100 * done) / total_size))
                    self.logger.info(f'{percentage}% completed')
                for alert in self.ALERTS_ORDER:
                    match = re.search(self.ALERTS_TO_REGEX[alert], log_line)
                    if match is not None:
                        yield match.group('timestamp'), alert, match.group('value')
                        break

    def convert_log_to_csv(self):
        with open(self.csv_path, 'w', newline='') as csv_file:
            self.writer = csv.writer(csv_file)
            self.writer.writerow(['timestamp'] + self.ALERTS_ORDER)
            for ts, alert, value in self.alerts_generator():
                data = [0] * len(self.ALERTS_ORDER)
                data[self.ALERTS_ORDER.index(alert)] = 1
                self.writer.writerow([ts] + data)


def configure_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # create console handler with a higher log level
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s >> %(message)s')
    stream_handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(stream_handler)
    return logger


def parse_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--csv_output', default=CSV_FILE_OUTPUT)
    parser.add_argument('-a', '--alerts_output', nargs='?', type=str, const=ALERTS_CSV_OUTPUT)
    parser.add_argument('-i', '--ip', default=RPI_IP, required=True)
    parser.add_argument('-d', '--delete', action='store_true')
    parser.add_argument('-o', '--output', default=LOG_FILE_PATH)
    return parser.parse_args()


def remote_sensor_data_files(ftp):
    log_files = ftp.nlst('Inhalator/inhalator.csv*')
    return sorted(log_files, reverse=True)


def copy_sensor_data(output_file, ftp, logger):
    """Copy log file from the Raspberry pi using FTP.

    Copying all log files from the remote RPi, and merging them into one file locally.

    Args:
        output_file (str): the output log file.
        ip (str): ip address of the raspberry pi.
        user (str): raspberry pi user.
        passwd (str): raspberry pi password.
    """
    open(output_file, 'w').close()  # create empty file
    with open(output_file, 'ab') as out_file:
        log_files = remote_sensor_data_files(ftp)
        log_files.insert(0, REMOTE_HEADERS_FILE)
        amount = len(log_files)
        for i, log_file in enumerate(log_files):
            logger.info("Copying %s / %s", i + 1, amount)
            ftp.retrbinary(f'RETR {log_file}', out_file.write)


def copy_log(ftp, output_path):
    open(output_path, 'w').close()  # create empty file
    with open(output_path, 'ab') as out_file:
        ftp.retrbinary(f'RETR Inhalator/inhalator.log', out_file.write)


def delete_sensor_values_files(ftp):
    bio = io.BytesIO(b'')
    for log_file in remote_sensor_data_files(ftp):
        ftp.storbinary(f'STOR {log_file}', bio)


def delete_log_file(ftp):
    bio = io.BytesIO(b'')
    ftp.storbinary(f'STOR {REMOTE_LOG_FILE}', bio)


def delete_files_conversation(logger, ip):
    logger.warning('You are about to delete all the sensor data in the Raspberry pi(%s) '
                   'Are you sure? (y/n)', ip)
    while True:
        answer = input()
        if answer != 'x' and answer != 'y':
            logger.info('Please enter `y` or `n`')

        else:
            break

    return answer == 'y'


def main():
    cli_args = parse_cli_args()
    logger = configure_logger()

    with ftplib.FTP(cli_args.ip, user='pi', passwd='raspberry') as ftp:
        if cli_args.delete:
            if delete_files_conversation(logger, cli_args.ip):
                logger.info('Deleting Raspberry logs')
                delete_sensor_values_files(ftp)
                delete_log_file(ftp)
                logger.info("Raspberry data deleted !")

        else:
            # Copy files from RPi to local storage.
            logger.info("Copying data files from Raspberry(%s) to %s",
                        cli_args.ip, cli_args.csv_output)
            copy_sensor_data(cli_args.csv_output, ftp, logger)
            logger.info('Copying log file')
            copy_log(ftp, cli_args.output)
            if cli_args.alerts_output is not None:
                alerts_extractor = AlertsExtractor(cli_args.output, cli_args.alerts_output, logger)
                logger.info('Parsing alerts log into CSV')
                alerts_extractor.convert_log_to_csv()
            logger.info('Finished, saved sensor data at %s, alerts at %s', cli_args.csv_output, cli_args.alerts_output)


if __name__ == '__main__':
    main()
