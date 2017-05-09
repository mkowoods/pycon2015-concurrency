# perf2.py
# requests/sec of fast requests

# Assessing the perfomrance of a threaded implementation

# start running and observe high through put performance
# then open another session and execute a long running request nc localhost 25000 (then type 50)
# you should see the req/sec drop when long running jobs are present
# the GIL prioritizes long running jobs

# the OS handles it differently giving priority to short running jobs
# you can test this by calling python -i fib.py and running fib(50) in multiple session
# you'll see that although the processor is working hard to process the requests the performance of the jobs still
# runs in the 25K - 35K req/sec range
#

from socket import *
import time

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('localhost', 25000))

n = 0
from threading import Thread
def monitor():
    global n
    while True:
        time.sleep(1)
        print(n, 'reqs/sec')
        n = 0

Thread(target=monitor).start()

while True:
    sock.send(b'1')
    resp = sock.recv(100)
    n += 1