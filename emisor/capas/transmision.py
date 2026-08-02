"""Capa de transmision: serializa/deserializa el sobre JSON sobre el socket TCP."""

import json
import socket


class LectorLineas:
    """Acumula bytes del socket hasta encontrar '\\n', porque TCP puede partir o pegar mensajes."""

    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._buffer = b""

    def leer_linea(self) -> str | None:
        while b"\n" not in self._buffer:
            fragmento = self._sock.recv(4096)
            if not fragmento:
                return None
            self._buffer += fragmento
        linea, _, self._buffer = self._buffer.partition(b"\n")
        return linea.decode("utf-8")


def enviar_informacion(sock: socket.socket, trama: str, algoritmo: str, parametros: dict) -> None:
    """Serializa el sobre JSON y lo envia terminado en salto de linea."""
    sobre = {"version": 1, "algoritmo": algoritmo, "parametros": parametros, "trama": trama}
    sock.sendall((json.dumps(sobre) + "\n").encode("utf-8"))


def recibir_informacion(lector: LectorLineas) -> dict | None:
    """Lee hasta el salto de linea y devuelve el sobre deserializado, o None si se cerro la conexion."""
    linea = lector.leer_linea()
    if linea is None:
        return None
    return json.loads(linea)
