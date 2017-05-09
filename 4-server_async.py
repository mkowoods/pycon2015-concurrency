# server.py
# fib microservice

"""
this implementation has overall poor performance because of higher overhead and
still runs into the same issues RE: blocking, GIL CPU issues

to see this run perf2 in one environment and the below commands in another

nc localhost 25000
40

"""

from  socket import *
from fib import fib
from collections import deque
from select import select

tasks = deque()
recv_wait = {} # Mapping sockets -> tasks (generators)
send_wait = {}
def run():
    while any([tasks, recv_wait, send_wait]):
        # print('num tasks', len(tasks))
        while not tasks:
            # No active tasks to run
            # waits for I/O
            # print('No tasks', 'recv_wait', len(recv_wait), 'send_wait', len(send_wait))
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
           else:
               raise RuntimeError("ARG!")
        except StopIteration:
            print("task done")

def fib_server(address):
    print("Starting Server @ ", address)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    while True:
        ## print('waiting for new connection')
        yield 'recv', sock
        client, addr = sock.accept() # blocking code
        print("Connection", addr)
        tasks.append( fib_handler(client) )

def fib_handler(client, addr=None):
    while True:
        # print('waiting for data from', addr)
        yield 'recv', client
        req = client.recv(100) # blocking code
        if not req:
            break
        n = int(req)
        # print('received data going to fib', n)
        result = fib(n)
        resp = str(result).encode('ascii') + b'\n'
        # print('waiting to send', result)
        yield 'send', client
        client.send(resp) # blocking code
        ## print('sent response')
    # print("Closed", addr)

# add the server
tasks.append(fib_server(('', 25000)))
run()