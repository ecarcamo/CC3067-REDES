"""Numero de secuencia del LSA propio, persistido en disco.

La definicion grupal es explicita: un nodo que se reinicia no vuelve a numerar
desde cero, arranca en el ultimo valor conocido mas uno. Si volviera a empezar
en cero, los demas descartarian sus anuncios por traer un `seq` menor al que ya
tienen guardado, y el nodo quedaria invisible hasta que la red lo olvidara.
"""

import threading
from pathlib import Path

import bitacora

_log = bitacora.obtener("control")

DIRECTORIO_ESTADO = Path("estado")


class Secuencia:
    """Contador monotono que sobrevive al reinicio del proceso."""

    def __init__(self, identificador: str, directorio: Path | str = DIRECTORIO_ESTADO):
        self._ruta = Path(directorio) / f"{identificador}_seq.txt"
        self._candado = threading.Lock()
        self._valor = self._leer()
        if self._valor:
            _log.info("secuencia recuperada del reinicio anterior: %s", self._valor)

    @property
    def actual(self) -> int:
        with self._candado:
            return self._valor

    def siguiente(self) -> int:
        """Avanza el contador, lo guarda y lo devuelve."""
        with self._candado:
            self._valor += 1
            self._guardar(self._valor)
            return self._valor

    def alcanzar(self, valor: int) -> None:
        """Sube el contador por encima de `valor` si venia mas atras.

        Hace falta cuando nos llega de vuelta un LSA propio mas nuevo que el que
        creemos haber emitido: la red recuerda una version nuestra que el disco
        perdio, y hay que superarla para que el proximo anuncio sea aceptado.
        """
        with self._candado:
            if valor >= self._valor:
                self._valor = valor
                self._guardar(self._valor)

    def _leer(self) -> int:
        if not self._ruta.exists():
            return 0
        try:
            return max(0, int(self._ruta.read_text(encoding="utf-8").strip()))
        except (OSError, ValueError):
            _log.warning("no se pudo leer %s, se arranca la secuencia en cero", self._ruta)
            return 0

    def _guardar(self, valor: int) -> None:
        try:
            self._ruta.parent.mkdir(parents=True, exist_ok=True)
            self._ruta.write_text(f"{valor}\n", encoding="utf-8")
        except OSError as error:
            # Perder la persistencia degrada el reinicio, no la ejecucion actual.
            _log.warning("no se pudo guardar la secuencia: %s", error)
