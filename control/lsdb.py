"""Base de datos de estado de enlace: el ultimo LSA conocido de cada origen.

De aqui sale el grafo completo de la red sobre el que se corre Dijkstra, y aqui
se corta el flooding. La regla es la de la seccion 4 del protocolo: se guarda el
mayor `seq` visto por origen, se descarta sin reenviar todo LSA que traiga uno
menor o igual, y solo el que trae uno mayor se guarda y se reenvia.
"""

import threading
import time
from dataclasses import dataclass, field

import bitacora

_log = bitacora.obtener("control")


@dataclass(frozen=True)
class Anuncio:
    """Un LSA ya aceptado, guardado como la version vigente de su origen."""

    origen: str
    seq: int
    enlaces: dict[str, int]
    recibido_en: float = field(default_factory=time.monotonic)


class BaseEstadoEnlaces:
    """Almacen de anuncios con control de version, seguro entre hilos."""

    def __init__(self):
        self._candado = threading.Lock()
        self._anuncios: dict[str, Anuncio] = {}
        self._version = 0

    @property
    def version(self) -> int:
        """Sube con cada cambio real del grafo; sirve para saber si recalcular."""
        with self._candado:
            return self._version

    def registrar(self, origen: str, seq: int, enlaces: dict[str, int]) -> bool:
        """Guarda el anuncio si es mas nuevo. Devuelve True si hay que reenviarlo."""
        with self._candado:
            vigente = self._anuncios.get(origen)
            if vigente is not None and seq <= vigente.seq:
                return False

            cambio_el_grafo = vigente is None or vigente.enlaces != enlaces
            self._anuncios[origen] = Anuncio(origen=origen, seq=seq, enlaces=dict(enlaces))
            if cambio_el_grafo:
                self._version += 1

        if cambio_el_grafo:
            _log.info("grafo actualizado por %s (seq %s): %s", origen, seq, enlaces)
        return True

    def seq_de(self, origen: str) -> int | None:
        with self._candado:
            anuncio = self._anuncios.get(origen)
            return None if anuncio is None else anuncio.seq

    def anuncios(self) -> list[Anuncio]:
        with self._candado:
            return list(self._anuncios.values())

    def grafo(self) -> dict[str, dict[str, int]]:
        """Grafo no dirigido de la red segun los anuncios vigentes.

        Solo se toma el enlace que ambos extremos anuncian. Un enlace declarado
        de un solo lado suele ser un anuncio que quedo viejo, y usarlo daria
        rutas que en la practica no existen; cuando los dos costos difieren se
        toma el mayor, que es la lectura conservadora.
        """
        with self._candado:
            declarados = {anuncio.origen: dict(anuncio.enlaces) for anuncio in self._anuncios.values()}

        grafo: dict[str, dict[str, int]] = {nodo: {} for nodo in declarados}
        for nodo, enlaces in declarados.items():
            for vecino, costo in enlaces.items():
                reciproco = declarados.get(vecino, {}).get(nodo)
                if reciproco is None:
                    continue
                acordado = max(costo, reciproco)
                grafo[nodo][vecino] = acordado
                grafo.setdefault(vecino, {})[nodo] = acordado
        return grafo
