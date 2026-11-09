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
            try:
              while True:
                  data = conn.recv(data_payload)
                  if not data:
                      break
                  conn.sendall(data)
            except OSError as e:
              print(f"Connection error with {addr}: {e}")


if __name__ == "__main__":
    server()
