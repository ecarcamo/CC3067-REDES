"""Pruebas del cálculo de rutas de la fase 2."""

import json

from control.dijkstra import calcular


def test_dijkstra_calcula_a_mano_las_rutas_desde_el_cajero():
    """Desde z, el extremo del ATM: la unica salida es y y de ahi todo es cadena."""
    with open("config/topologia.json", encoding="utf-8") as archivo:
        grafo = json.load(archivo)

    rutas = calcular(grafo, "z")

    assert {
        destino: (ruta.costo, ruta.siguiente_salto) for destino, ruta in rutas.items()
    } == {
        "z": (0, "z"),
        "y": (1, "y"),
        "x": (2, "y"),
        "u": (3, "y"),
        "v": (4, "y"),
        "w": (4, "y"),
    }


def test_dijkstra_calcula_a_mano_las_rutas_desde_el_banco():
    """Desde v, el extremo del banco: u y w estan a un salto y el resto cuelga de u."""
    with open("config/topologia.json", encoding="utf-8") as archivo:
        grafo = json.load(archivo)

    rutas = calcular(grafo, "v")

    assert {
        destino: (ruta.costo, ruta.siguiente_salto) for destino, ruta in rutas.items()
    } == {
        "v": (0, "v"),
        "u": (1, "u"),
        "w": (1, "w"),
        "x": (2, "u"),
        "y": (3, "u"),
        "z": (4, "u"),
    }


def test_dijkstra_omite_inalcanzables_y_desempata_por_primer_salto():
    grafo = {
        "A": {"C": 1, "B": 1},
        "B": {"A": 1, "D": 1},
        "C": {"A": 1, "D": 1},
        "D": {"B": 1, "C": 1},
        "Z": {},
    }

    rutas = calcular(grafo, "A")

    assert rutas["D"].siguiente_salto == "B"
    assert "Z" not in rutas
