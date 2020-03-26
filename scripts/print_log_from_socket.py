import socket
import pickle
import logging

level = logging.DEBUG
logger = logging.getLogger()
logger.setLevel(level)
# create file handler which logs even debug messages
fh = logging.FileHandler('/tmp/inhalator.log')
fh.setLevel(level)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(level)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

PORT = 7777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', PORT))

while True:
    raw_log = sock.recv(2 ** 16)
    log_meta = pickle.loads(raw_log[4:])  # Remove header
    logger.debug(log_meta['msg'])

