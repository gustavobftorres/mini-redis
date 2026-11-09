import socket


def server(host="localhost", port=8001):
    data_payload = 2048

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((host, port))
    sock.listen()
    while True:
        conn, addr = sock.accept()

        with conn:
            print("Connected by", addr)
            while True:
                data = conn.recv(data_payload)
                if not data:
                    break
                conn.sendall(data)


if __name__ == "__main__":
    server()
