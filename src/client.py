import socket
import time


def client(host="localhost", port=8002):
    data_payload = 2048

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((host, port))
    while True:
        msg = input("Digite uma mensagem (ou 'sair' para encerrar):")

        if msg.lower() == "sair":
            sock.sendall((msg + "\n").encode("utf-8"))
            break

        sock.sendall((msg + "\n").encode("utf-8"))
        data = sock.recv(data_payload)

        print("Received", repr(data))


if __name__ == "__main__":
    client()
