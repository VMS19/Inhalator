import csv
import datetime
import logging
from logging.handlers import RotatingFileHandler

BYTES_IN_GB = 2 ** 30


class SamplesStorage:
    COLUMNS = ['timestamp',
               'unix_time (milliseconds)',
               'time elapsed (seconds)',
               'flow',
               'pressure',
               'oxygen',
               'pip',
               'peep',
               'tv_insp',
               'tv_exp',
               'bpm',
               'state']
    HEADERS_FILE = 'headers.csv'

    def __init__(self, file_name_template='inhalator.csv',
                 max_file_size=BYTES_IN_GB, max_files=3):  # 3GB can store more than 2 weeks of data.
        self.max_files = max_files
        self.max_file_size = max_file_size
        self.file_name = file_name_template
        self.first_ts = None
        self.logger = self._configure_logger()
        # Write title row
        self._write_headers_file()

    def _write_headers_file(self):
        with open(self.HEADERS_FILE, 'w') as f:
            csv.writer(f).writerow(self.COLUMNS)

    def _configure_logger(self):
        logger = logging.getLogger('samples_storage')
        logger.setLevel(logging.DEBUG)
        file_handler = RotatingFileHandler(self.file_name,
                                           maxBytes=self.max_file_size,
                                           backupCount=self.max_files)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        return logger

    def _write_row(self, row):
        self.logger.debug(','.join(str(item) for item in row))

    def _time_diff(self, timestamp):
        if self.first_ts is None:
            self.first_ts = timestamp
        return (timestamp - self.first_ts).total_seconds()

    def write(self, flow, pressure, oxygen, pip=None, peep=None, tv_insp=None, tv_exp=None, bpm=None, state=None):
        timestamp = datetime.datetime.now()
        unix_time = timestamp.timestamp() * 1000
        time_diff = self._time_diff(timestamp)
        self._write_row([timestamp, unix_time, time_diff, flow, pressure, oxygen, pip, peep, tv_insp, tv_exp, bpm, state])
