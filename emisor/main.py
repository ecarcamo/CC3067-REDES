"""Cajero automatico (emisor). Hito 0: solo conecta y manda un string de prueba."""

import socket

HOST = "127.0.0.1"
PORT = 2705


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print(f"[EMISOR] Conectado a {HOST}:{PORT}")

        sock.sendall(b"hola banco\n")
        respuesta = sock.recv(4096)
        print(f"[EMISOR] Respuesta: {respuesta.decode('utf-8').strip()}")


if __name__ == "__main__":
    main()
