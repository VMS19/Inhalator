import socket
import pickle
import logging

PORT = 7777
LOG_LEVEL = logging.DEBUG
LOG_FILE_PATH = '/tmp/inhalator.log'

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)
# create file handler which logs even debug messages
fh = logging.FileHandler(LOG_FILE_PATH)
fh.setLevel(LOG_LEVEL)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(LOG_LEVEL)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s >> %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', PORT))

while True:
    raw_log = sock.recv(2 ** 16)
    log_meta = pickle.loads(raw_log[4:])  # Remove header
    logger.handle(logging.makeLogRecord(log_meta))
