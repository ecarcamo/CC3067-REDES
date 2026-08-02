"""Mapea el nombre de un algoritmo (string del protocolo) a su instancia."""

from algoritmos.contrato import AlgoritmoIntegridad
from algoritmos.crc32 import Crc32
from algoritmos.hamming import Hamming

_ALGORITMOS: dict[str, AlgoritmoIntegridad] = {
    "hamming": Hamming(),
    "crc32": Crc32(),
}


def obtener_algoritmo(nombre: str) -> AlgoritmoIntegridad:
    """Devuelve la instancia registrada para `nombre`, o lanza KeyError si no existe."""
    try:
        return _ALGORITMOS[nombre]
    except KeyError:
        raise KeyError(f"Algoritmo desconocido: {nombre!r}") from None
