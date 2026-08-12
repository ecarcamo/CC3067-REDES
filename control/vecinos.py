"""Estado de los vecinos directos, alimentado por los HELLO.

Un vecino se considera vivo desde que llega su primer HELLO y se da por caido
si pasan quince segundos sin recibir otro, tal como fija la definicion grupal.
El costo del enlace no se mide: se lee de la topologia compartida y es
simetrico, asi que el HELLO solo aporta la senal de vida.
"""

import threading
import time
from dataclasses import dataclass, field

import bitacora

from protocolo.constantes import TIMEOUT_VECINO

_log = bitacora.obtener("control")


@dataclass
class EstadoVecino:
    nombre: str
    costo: int
    vivo: bool = False
    ultimo_hello: float = field(default=0.0)


class GestorVecinos:
    """Lleva la cuenta de que vecinos estan vivos en este momento."""

    def __init__(self, vecinos: dict[str, int], timeout: float = TIMEOUT_VECINO):
        self._timeout = timeout
        self._candado = threading.Lock()
        self._vecinos = {
            nombre: EstadoVecino(nombre=nombre, costo=costo) for nombre, costo in vecinos.items()
        }

    @property
    def configurados(self) -> list[str]:
        """Todos los vecinos de la configuracion, esten vivos o no."""
        return sorted(self._vecinos)

    def registrar_hello(self, vecino: str) -> bool:
        """Anota el HELLO recibido. Devuelve True si el vecino acaba de revivir."""
        with self._candado:
            estado = self._vecinos.get(vecino)
            if estado is None:
                # Un HELLO de alguien que no es vecino nuestro no aporta costo y
                # no se puede anunciar, asi que se ignora sin ruido.
                _log.debug("HELLO de %s, que no es vecino configurado", vecino)
                return False

            estado.ultimo_hello = time.monotonic()
            if estado.vivo:
                return False

            estado.vivo = True
            _log.info("vecino %s activo (costo %s)", vecino, estado.costo)
            return True

    def vencidos(self) -> list[str]:
        """Marca como caidos a los vecinos vencidos y devuelve cuales fueron."""
        ahora = time.monotonic()
        caidos = []
        with self._candado:
            for estado in self._vecinos.values():
                if estado.vivo and ahora - estado.ultimo_hello > self._timeout:
                    estado.vivo = False
                    caidos.append(estado.nombre)
        for vecino in caidos:
            _log.warning("vecino %s caido: %.0fs sin HELLO", vecino, self._timeout)
        return caidos

    def vivos(self) -> list[str]:
        with self._candado:
            return sorted(nombre for nombre, estado in self._vecinos.items() if estado.vivo)

    def esta_vivo(self, vecino: str) -> bool:
        with self._candado:
            estado = self._vecinos.get(vecino)
            return estado is not None and estado.vivo

    def enlaces_activos(self) -> dict[str, int]:
        """Los `links` que se anuncian en el LSA propio: solo vecinos vivos."""
        with self._candado:
            return {
                nombre: estado.costo
                for nombre, estado in sorted(self._vecinos.items())
                if estado.vivo
            }
