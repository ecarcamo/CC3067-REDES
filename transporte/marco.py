"""Delimitacion de mensajes dentro del flujo TCP.

TCP es un flujo de bytes sin fronteras: un `recv` puede devolver medio mensaje,
dos pegados o los dos casos a la vez. El protocolo cierra cada mensaje con
`\\n`, asi que el lector acumula lo que llega hasta encontrar ese corte.
"""

import socket

from protocolo.constantes import CODIFICACION, DELIMITADOR

# Un mensaje de control ronda los 200 bytes y un sobre de datos con Hamming no
# llega a unos pocos miles. El limite solo existe para que un emisor roto o
# malintencionado no haga crecer el buffer sin fin.
LIMITE_LINEA = 1 << 20


class ErrorMarco(Exception):
    """La otra punta mando algo que no se puede enmarcar."""


class LectorLineas:
    """Entrega, una por una, las lineas completas que llegan por el socket."""

    def __init__(self, conexion: socket.socket):
        self._conexion = conexion
        self._buffer = b""

    def leer_linea(self) -> str | None:
        """Devuelve la siguiente linea sin el delimitador, o None si cerraron."""
        separador = DELIMITADOR.encode(CODIFICACION)
        while separador not in self._buffer:
            if len(self._buffer) > LIMITE_LINEA:
                raise ErrorMarco("linea demasiado larga, se descarta la conexion")
            fragmento = self._conexion.recv(4096)
            if not fragmento:
                return None
            self._buffer += fragmento

        linea, _, self._buffer = self._buffer.partition(separador)
        try:
            return linea.decode(CODIFICACION).strip()
        except UnicodeDecodeError as error:
            raise ErrorMarco("la linea recibida no es UTF-8 valido") from error
