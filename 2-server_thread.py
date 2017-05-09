# server.py
# fib microservice

# can handle multiple request since each connection gets assigned it's own thread
# can handle one long running request and still serve other requests
# since the long running request can execute in the thread
# one issue is that because of the GIL a single long running process can bring down the performance
# of all threads
# run perf2 in one terminal and connect and send localhost 25000 the value 40


from socket import *
from fib import fib
from threading import Thread

def fib_handler(client, addr):
    while True:
        print('waiting on data', addr)
        req = client.recv(100)
        print('received data', req, addr)
        if not req:
            break
        n = int(req)
        print('starting to calc fib', addr)
        result = fib(n)
        resp = str(result).encode('ascii') + b'\n'
        client.send(resp)
        print('sent data', resp, addr)
    print("Closed")


def fib_server(address):
    print("Starting Server @ ", address)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    while True:
        client, addr = sock.accept()
        print("Connection", addr)
        Thread(target=fib_handler, args=(client,addr), daemon=True).start()


fib_server(('', 25000))


