import socket


def client(host="localhost", port=8001):
    data_payload = 2048

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((host, port))
    sock.sendall(b"Hello world")
    data = sock.recv(data_payload)

    print("Received", repr(data))

if __name__ == "__main__":
    client()
