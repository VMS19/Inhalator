import datetime
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

BYTES_IN_GB = 2 ** 30


class SamplesStorage:
    COLUMNS = ['timestamp',
               'unix_time (milliseconds)',
               'time_elapsed (seconds)',
               'flow',
               'pressure',
               'oxygen']

    def __init__(self, file_name_template='inhalator.csv',
                 max_file_size=BYTES_IN_GB * 7, max_files=1):
        self.max_files = max_files
        self.max_file_size = max_file_size
        self.file_name = file_name_template
        self.first_ts = None
        self.logger = self._configure_logger()
        # Write title row
        if self.no_log_files_exists:
            self._write_row(self.COLUMNS)

    @property
    def no_log_files_exists(self):
        Path().stat()
        rotated_files = [item for item in Path(self.file_name).parent.iterdir()
                         if item.name.startswith(self.file_name)]
        sizes = [log_file.stat().st_size for log_file in rotated_files]
        return all(size == 0 for size in sizes)

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

    def write(self, flow, pressure, oxygen):
        timestamp = datetime.datetime.now()
        unix_time = timestamp.timestamp() * 1000
        time_diff = self._time_diff(timestamp)
        self._write_row([timestamp, unix_time, time_diff, flow, pressure, oxygen])
