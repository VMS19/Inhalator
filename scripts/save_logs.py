"""Copy log files from the raspberry to a local CSV file."""
import ftplib
import logging
import argparse

RPI_IP = '192.168.43.234'

LOG_LEVEL = 'TRACE'
CSV_FILE_OUTPUT = 'inhalator.csv'


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
    parser.add_argument('-i', '--ip', default=RPI_IP)
    return parser.parse_args()


def remote_log_files(ftp):
    log_files = ftp.nlst('Inhalator/inhalator.csv*')
    return sorted(log_files, reverse=True)


def copy_log_files(output_file, ftp, logger):
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
        log_files = remote_log_files(ftp)
        amount = len(log_files)
        for i, log_file in enumerate(log_files):
            logger.info("Copying %s / %s", i + 1, amount)
            ftp.retrbinary(f'RETR {log_file}', out_file.write)


def main():
    # TODO delete files
    cli_args = parse_cli_args()
    logger = configure_logger()

    with ftplib.FTP(cli_args.ip, user='pi', passwd='raspberry') as ftp:
        # Copy files from RPi to local storage.
        logger.info(f"Copying log files from Raspberry(%s) to %s", cli_args.ip, cli_args.csv_output)
        copy_log_files(cli_args.csv_output, ftp, logger)

    logger.info("Finished, saved at %s", cli_args.csv_output)


if __name__ == '__main__':
    main()
