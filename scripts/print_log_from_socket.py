import socket
import pickle

PORT = 7777

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', PORT))

while True:
    raw_log = sock.recv(2 ** 16)
    log_meta = pickle.loads(raw_log[4:])  # Remove header
    print(log_meta['msg'])

