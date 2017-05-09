# server.py
# fib microservice

"""
Each thread can now take advantage of multiple processors so that
long running task can be run on their own core. However, the overhead
of adding processors lowers the overall performance in requests/sec (run perf2)

"""

from  socket import *
from fib import fib
from threading import Thread
from concurrent.futures import ProcessPoolExecutor as Pool

pool = Pool(4) #pool with 4 processes

def fib_server(address):
    print("Starting Server @ ", address)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    while True:
        client, addr = sock.accept()
        print("Connection", addr)
        Thread(target=fib_handler, args=(client,), daemon=True).start()


def fib_handler(client):
    while True:
        req = client.recv(100)
        if not req:
            break
        n = int(req)
        future = pool.submit(fib, n) #modification
        result = future.result()
        resp = str(result).encode('ascii') + b'\n'
        client.send(resp)
    print("Closed")


fib_server(('', 25000))


