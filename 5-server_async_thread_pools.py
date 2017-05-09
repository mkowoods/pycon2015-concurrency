# server.py
# fib microservice


""""
Uses a thread pool and coroutines to handle the server call and avoid the blocking issue

"""

from  socket import *
from fib import fib
from collections import deque
from select import select
from concurrent.futures import ThreadPoolExecutor as Pool

pool = Pool(10)

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
        # reall expensive!!!
        # ctr += 1
        # if ctr == 1000:
        #     print('num tasks', len(tasks), len(recv_wait), len(send_wait), len(future_wait))
        #     ctr = 0
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
           elif why == 'future':
               future_wait[what] = task
               what.add_done_callback(future_done)
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
        #result = fib(n)
        future = pool.submit(fib, n)
        yield 'future', future #convert the future to non-blocking
        result = future.result() # this doesnt work without yiel because of blocking, because this blocks
        resp = str(result).encode('ascii') + b'\n'
        # print('waiting to send', result)
        yield 'send', client
        client.send(resp) # blocking code
        ## print('sent response')
    # print("Closed", addr)

# add the server
tasks.append(fib_server(('', 25000)))
run()