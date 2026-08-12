"""Calculo de las rutas mas cortas sobre el grafo aprendido por LSA.

Entra el grafo que arma `control.lsdb.BaseEstadoEnlaces.grafo()`, que es un
diccionario no dirigido `{nodo: {vecino: costo}}` con los enlaces que ambos
extremos anuncian, y sale una ruta por cada destino alcanzable.

Lo que necesita el plano de datos no es el camino completo sino el primer salto:
al reenviar un mensaje, el nodo solo decide a que vecino se lo entrega. Por eso
`Ruta.siguiente_salto` es el vecino directo por donde arranca el camino optimo,
no el destino final.

Detalles a respetar:

* El origen queda en la tabla con costo 0 y `siguiente_salto` igual a si mismo;
  el plano de datos lo lee como "este mensaje es para mi, entregalo local".
* Los destinos inalcanzables simplemente no aparecen en el resultado.
* Ante dos caminos de igual costo conviene desempatar por orden alfabetico del
  siguiente salto, para que dos nodos que corren el mismo calculo lleguen a la
  misma decision y la ruta sea estable entre ejecuciones.
"""

import heapq
from dataclasses import dataclass


@dataclass(frozen=True)
class Ruta:
    """Una fila de la tabla de enrutamiento, antes de escribirla al CSV."""

    destino: str
    costo: float
    siguiente_salto: str


def calcular(grafo: dict[str, dict[str, int]], origen: str) -> dict[str, Ruta]:
    """Devuelve la mejor ruta hacia cada destino alcanzable desde `origen`.

    Sugerencia de implementacion: Dijkstra con `heapq`, arrastrando el primer
    salto junto con el costo acumulado. Cuando se relaja un vecino directo del
    origen, su primer salto es el vecino mismo; en cualquier otro caso se hereda
    el primer salto del nodo desde el que se llego.
    """
    mejores: dict[str, tuple[float, str]] = {origen: (0, origen)}
    pendientes: list[tuple[float, str, str]] = [(0, origen, origen)]

    while pendientes:
        costo, primer_salto, nodo = heapq.heappop(pendientes)
        if mejores.get(nodo) != (costo, primer_salto):
            continue

        for vecino, costo_enlace in grafo.get(nodo, {}).items():
            if vecino == origen:
                continue
            siguiente = vecino if nodo == origen else primer_salto
            candidato = (costo + costo_enlace, siguiente)
            if vecino not in mejores or candidato < mejores[vecino]:
                mejores[vecino] = candidato
                heapq.heappush(pendientes, (*candidato, vecino))

    return {
        destino: Ruta(destino=destino, costo=costo, siguiente_salto=siguiente)
        for destino, (costo, siguiente) in mejores.items()
    }
