import socket


def client(host="localhost", port=8002):
    data_payload = 2048

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((host, port))
    try:
        while True:
            msg = input("Digite uma mensagem (ou 'sair' para encerrar):")

            if msg.lower() == "sair":
                break

            sock.sendall((msg + "\n").encode("utf-8"))
            data = sock.recv(data_payload)

            print("Received", repr(data))

    finally:
        sock.close()


if __name__ == "__main__":
    client()
