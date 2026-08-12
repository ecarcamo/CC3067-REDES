"""Conexiones salientes hacia los vecinos.

Se mantiene una conexion TCP abierta por vecino y se reusa: con un HELLO cada
cinco segundos, abrir y cerrar un socket cada vez seria puro desperdicio, y
ademas la conexion viva es una senal temprana de que el vecino se cayo.

Cada conexion se usa en un solo sentido. Este nodo abre la suya para enviar y
el vecino abre la propia para lo mismo, asi que no hay que coordinar quien
escribe: por la conexion que yo abro, solo escribo yo.
"""

import socket
import threading

import bitacora
from configuracion import Direccion

_log = bitacora.obtener("transporte")

TIMEOUT_CONEXION = 3.0


class Enlaces:
    """Directorio de destinos alcanzables con su conexion reutilizable."""

    def __init__(self, direcciones: dict[str, Direccion] | None = None):
        self._direcciones: dict[str, Direccion] = dict(direcciones or {})
        self._conexiones: dict[str, socket.socket] = {}
        self._candados: dict[str, threading.Lock] = {}
        self._candado_maestro = threading.Lock()

    def registrar(self, nombre: str, direccion: Direccion) -> None:
        """Agrega un destino que no venia en la configuracion inicial."""
        with self._candado_maestro:
            self._direcciones[nombre] = direccion

    def enviar(self, destino: str, datos: bytes) -> bool:
        """Envia los bytes ya serializados. Devuelve False si el destino no responde.

        Que un vecino no responda es parte del funcionamiento normal, no un
        error del programa: el plano de control se entera por el vencimiento del
        HELLO y reacciona anunciando un LSA sin ese enlace.
        """
        direccion = self._direcciones.get(destino)
        if direccion is None:
            _log.warning("no hay direccion registrada para %s", destino)
            return False

        with self._candado_de(destino):
            for reintento in (False, True):
                conexion = self._conexiones.get(destino)
                if conexion is None:
                    conexion = self._conectar(destino, direccion)
                    if conexion is None:
                        return False
                try:
                    conexion.sendall(datos)
                    return True
                except OSError as error:
                    self._descartar(destino)
                    if reintento:
                        _log.debug("no se pudo enviar a %s: %s", destino, error)
                        return False
                    # La conexion cacheada estaba muerta; se reabre y se reintenta.
        return False

    def difundir(self, destinos, datos: bytes) -> list[str]:
        """Envia lo mismo a varios destinos. Devuelve los que si recibieron."""
        return [destino for destino in destinos if self.enviar(destino, datos)]

    def cerrar(self, destino: str) -> None:
        with self._candado_de(destino):
            self._descartar(destino)

    def cerrar_todo(self) -> None:
        for destino in list(self._conexiones):
            self.cerrar(destino)

    def _candado_de(self, destino: str) -> threading.Lock:
        with self._candado_maestro:
            return self._candados.setdefault(destino, threading.Lock())

    def _conectar(self, destino: str, direccion: Direccion) -> socket.socket | None:
        try:
            conexion = socket.create_connection(direccion.como_tupla(), timeout=TIMEOUT_CONEXION)
        except OSError as error:
            _log.debug("no se pudo conectar con %s: %s", destino, error)
            return None
        # Se quita el timeout: aplica al establecimiento, no al envio.
        conexion.settimeout(None)
        self._conexiones[destino] = conexion
        _log.debug("conexion abierta hacia %s", destino)
        return conexion

    def _descartar(self, destino: str) -> None:
        conexion = self._conexiones.pop(destino, None)
        if conexion is not None:
            try:
                conexion.close()
            except OSError:
                pass
