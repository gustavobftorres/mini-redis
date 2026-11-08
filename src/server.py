import socket


def server(host='localhost', port=8000):
    data_payload = 2048

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((host, port))
    conn, addr = sock.accept()

    with conn:
        print("Connected by", addr)
        while True:
            data = conn.recv(data_payload)
            if not data:
                break
            conn.sendall(data)


def client(host='localhost', port=3000):
    data_payload = 2048

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((host, port))
    sock.sendall(b"Hello world")
    data = sock.recv(data_payload)

    print("Received", repr(data))
