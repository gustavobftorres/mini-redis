import socket


def interactive_client(host="localhost", port=8002):
    data_payload = 2048

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((host, port))

    try:
        while True:
            received_bytes = 0
            received_msg = []
            msg = input("Digite uma mensagem (ou 'sair' para encerrar):")
            msg_bytes = len(msg.encode("utf-8"))

            if msg.lower() == "sair":
                break

            sock.sendall((msg).encode("utf-8"))
            ## E se eu receber mais do que 2048 bytes?
            while received_bytes < msg_bytes:
                data = sock.recv(data_payload)
                if not data:
                    break
                received_bytes = received_bytes + len(data)
                received_msg.append(data)

            if received_bytes != msg_bytes:
                print("The answer is not complete")
                break

            response_bytes = b"".join(received_msg)
            if response_bytes != msg.encode("utf-8"):
                print("The answer is not the same as sended message")

            response = response_bytes.decode("utf-8")
            print("Received", response)

    finally:
        sock.close()


def client(host, port, msg):
    data_payload = 2048

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((host, port))

    try:
        received_bytes = 0
        received_msg = []
        msg_bytes = len(msg.encode("utf-8"))

        sock.sendall((msg).encode("utf-8"))
        ## E se eu receber mais do que 2048 bytes?
        while received_bytes < msg_bytes:
            data = sock.recv(data_payload)
            if not data:
                break
            received_bytes = received_bytes + len(data)
            received_msg.append(data)

        if received_bytes != msg_bytes:
            print("The answer is not complete")

        response_bytes = b"".join(received_msg)
        if response_bytes != msg.encode("utf-8"):
            print("The answer is not the same as sended message")

        response = response_bytes.decode("utf-8")
        print("Received", response)
        return response

    finally:
        sock.close()
        print("Processo encerrado")
