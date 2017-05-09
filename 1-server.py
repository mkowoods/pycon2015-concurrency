# server.py
# fib microservice

# original synchronous implementation. can only support 1 request at a time
# can only support one connection (becaus the I/O on client.recv blocks the server)
from  socket import  *
from fib import fib

def fib_handler(client):
   while True:
      print('waiting to receive data')
      req = client.recv(100)
      print(req)
      if not req:
          break
      n = int(req)
      result = fib(n)
      resp = str(result).encode('ascii') + b'\n'
      client.send(resp)
      print('sent')
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
        fib_handler(client)

      
fib_server(('', 25000))