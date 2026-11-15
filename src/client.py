import socket
import time

def client(host="localhost", port=8001):
    data_payload = 2048

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((host, port))
    while True:
      sock.sendall(b"Hello world")
      data = sock.recv(data_payload)
      time.sleep(5)
  
      print("Received", repr(data))

if __name__ == "__main__":
    client()
