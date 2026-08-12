"""Servidor de escucha del nodo.

Un solo puerto recibe todo: los HELLO y los LSA del plano de control y las
tramas Hamming del plano de datos. El servidor no interpreta nada, solo separa
las lineas y se las pasa al despachador; quien decide que es cada cosa es
`protocolo.mensajes.clasificar`.

Cada conexion entrante vive en su propio hilo, de modo que un vecino lento
nunca frena al resto.
"""

import socket
import threading
from typing import Callable

import bitacora
from configuracion import Direccion
from transporte.marco import ErrorMarco, LectorLineas

_log = bitacora.obtener("transporte")

# El despachador recibe la linea cruda y la ip desde donde llego.
Despachador = Callable[[str, str], None]


class Servidor:
    """Acepta conexiones y entrega cada linea recibida al despachador."""

    def __init__(self, direccion: Direccion, despachar: Despachador):
        self._direccion = direccion
        self._despachar = despachar
        self._socket: socket.socket | None = None
        self._activo = threading.Event()
        self._hilos: list[threading.Thread] = []

    def iniciar(self) -> None:
        """Abre el puerto y arranca el hilo que acepta conexiones."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(self._direccion.como_tupla())
        self._socket.listen(16)
        self._activo.set()

        hilo = threading.Thread(target=self._aceptar, name="servidor", daemon=True)
        hilo.start()
        self._hilos.append(hilo)
        _log.info("escuchando en %s:%s", self._direccion.ip, self._direccion.puerto)

    def detener(self) -> None:
        self._activo.clear()
        if self._socket is not None:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None

    def _aceptar(self) -> None:
        while self._activo.is_set():
            try:
                conexion, origen = self._socket.accept()
            except OSError:
                if self._activo.is_set():
                    _log.warning("el socket de escucha fallo, se deja de aceptar")
                return

            hilo = threading.Thread(
                target=self._atender,
                args=(conexion, origen[0]),
                name=f"conexion-{origen[0]}",
                daemon=True,
            )
            hilo.start()
            self._hilos.append(hilo)

    def _atender(self, conexion: socket.socket, ip_origen: str) -> None:
        lector = LectorLineas(conexion)
        try:
            while self._activo.is_set():
                linea = lector.leer_linea()
                if linea is None:
                    break
                if not linea:
                    continue
                try:
                    self._despachar(linea, ip_origen)
                except Exception:
                    # Un mensaje malo no puede tumbar la conexion con el vecino.
                    _log.exception("error procesando un mensaje de %s", ip_origen)
        except ErrorMarco as error:
            _log.warning("problema de enmarcado con %s: %s", ip_origen, error)
        except OSError:
            pass
        finally:
            try:
                conexion.close()
            except OSError:
                pass
