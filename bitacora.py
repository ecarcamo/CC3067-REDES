"""Bitacora comun a todos los modulos del nodo.

Con varios hilos escribiendo a la vez, la salida sin prefijo se vuelve
ilegible, asi que todo pasa por aqui y sale con hora, nodo y modulo.
"""

import logging
import sys

_FORMATO = "%(asctime)s [%(nodo)s] %(name)-12s %(message)s"
_FORMATO_HORA = "%H:%M:%S"


def configurar(identificador: str, detallado: bool = False) -> None:
    """Deja la bitacora lista. Se llama una sola vez, al arrancar el nodo."""
    manejador = logging.StreamHandler(sys.stdout)
    manejador.setFormatter(logging.Formatter(_FORMATO, datefmt=_FORMATO_HORA))
    manejador.addFilter(_AgregarNodo(identificador))

    raiz = logging.getLogger("nodo")
    raiz.handlers.clear()
    raiz.addHandler(manejador)
    raiz.setLevel(logging.DEBUG if detallado else logging.INFO)
    raiz.propagate = False


def obtener(nombre: str) -> logging.Logger:
    """Devuelve la bitacora de un modulo (`control`, `transporte`, ...)."""
    return logging.getLogger(f"nodo.{nombre}")


class _AgregarNodo(logging.Filter):
    def __init__(self, identificador: str):
        super().__init__()
        self._identificador = identificador

    def filter(self, registro: logging.LogRecord) -> bool:
        registro.nodo = self._identificador
        return True
