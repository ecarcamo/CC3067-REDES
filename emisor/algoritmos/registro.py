"""Mapea el nombre de un algoritmo (string del protocolo) a su instancia."""

from algoritmos.contrato import AlgoritmoIntegridad
from algoritmos.crc32 import Crc32
from algoritmos.fletcher import Fletcher
from algoritmos.hamming import Hamming

_ALGORITMOS: dict[str, AlgoritmoIntegridad] = {
    "hamming": Hamming(),
    "crc32": Crc32(),
    "fletcher": Fletcher(),
}


def obtener_algoritmo(nombre: str, configuracion: dict | None = None) -> AlgoritmoIntegridad:
    """Devuelve la instancia registrada para `nombre`, o lanza KeyError si no existe."""
    try:
        if nombre == "hamming" and configuracion:
            return Hamming(configuracion.get("m", 8))
        if nombre == "fletcher" and configuracion:
            return Fletcher(configuracion.get("tamano_bloque", 16))
        return _ALGORITMOS[nombre]
    except KeyError:
        raise KeyError(f"Algoritmo desconocido: {nombre!r}") from None
