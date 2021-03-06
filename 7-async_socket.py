# server.py
# fib microservice


""""
introduces yield from syntax and refactos code 
"""

from  socket import *
from fib import fib
from collections import deque
from select import select
from concurrent.futures import ProcessPoolExecutor as Pool

pool = Pool(4)

tasks = deque()
recv_wait = {} # Mapping sockets -> tasks (generators)
send_wait = {}
future_wait = {}

#call back logic
future_notify, future_event = socketpair()

def future_done(future):
    tasks.append( future_wait.pop(future))
    future_notify.send(b'x') #whe

#not 100% sure what's happening here
def future_monitor():
    while True:
        #print("Added future even to task queue")
        yield 'recv', future_event
        future_event.recv(100)

tasks.append(future_monitor())
def run():
    ctr = 0

    while any([tasks, recv_wait, send_wait]):
        while not tasks:
            can_recv, can_send, _ = select(recv_wait, send_wait, [])
            for s in can_recv:
                tasks.append(recv_wait.pop(s))
            for s in can_send:
                tasks.append(send_wait.pop(s))

        task = tasks.popleft()
        try:
           why, what =  next(task) # run to the yield

           if why == 'recv':
               recv_wait[what] = task
           elif why == 'send':
               send_wait[what] = task
           elif why == 'future':
               future_wait[what] = task
               what.add_done_callback(future_done)
           else:
               raise RuntimeError("ARG!")
        except StopIteration:
            print("task done")

class AsyncSocket(object):

    def __init__(self, sock):
        self.sock = sock #Socket

    def recv(self, maxsize):
        yield 'recv', self.sock
        return self.sock.recv(maxsize)

    def send(self, data):
        yield 'send', self.sock
        return self.sock.send(data)

    def accept(self):
        yield 'recv', self.sock
        client, addr = self.sock.accept()
        return AsyncSocket(client), addr

    def __getattr__(self, item):
        return getattr(self.sock, item)

def fib_server(address):
    print("Starting Server @ ", address)
    sock = AsyncSocket( socket(AF_INET, SOCK_STREAM) )
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    while True:

        client, addr = yield from sock.accept() # blocking code
        print("Connection", addr)
        tasks.append( fib_handler(client) )

def fib_handler(client, addr=None):
    while True:

        req = yield from client.recv(100) # blocking code
        if not req:
            break
        n = int(req)
        future = pool.submit(fib, n)
        yield 'future', future #convert the future to non-blocking
        result = future.result() # this doesnt work without yiel because of blocking, because this blocks
        resp = str(result).encode('ascii') + b'\n'

        yield from client.send(resp) # blocking code

tasks.append(fib_server(('', 25000)))
run()