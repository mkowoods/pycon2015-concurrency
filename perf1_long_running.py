# perf1.py
# Time of a long running request

# Assessing the perfomrance of a threaded implementation

# run in multiple sessions and see the time to execute start to increase proprotional to the number of concurrent requests
# a function of the GIL sharing resources

from socket import *
import time

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('localhost', 25000))

while True:
    start = time.time()
    sock.send(b'30')
    resp = sock.recv(100)
    end = time.time()
    print('Total Time', end - start)