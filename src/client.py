import socket


def client(host="localhost", port=8002):
    data_payload = 2048

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((host, port))
    received_bytes = 0
    received_msg = []
    try:
        while True:
            msg = input("Digite uma mensagem (ou 'sair' para encerrar):")
            msg_bytes = len(msg.encode("utf-8"))

            if msg.lower() == "sair":
                break

            sock.sendall((msg).encode("utf-8"))
            ## E se eu receber mais do que 2048 bytes?
            data = sock.recv(data_payload)
            while int(data) < msg_bytes:
                received_bytes = received_bytes + data_payload
                received_msg.append(data)

            print("Received", repr(data))

    finally:
        sock.close()


if __name__ == "__main__":
    client()
