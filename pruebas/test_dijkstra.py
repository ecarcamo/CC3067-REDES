"""Pruebas del cálculo de rutas de la fase 2."""

import json

from control.dijkstra import calcular


def test_dijkstra_calcula_a_mano_las_rutas_de_la_topologia_real():
    with open("config/topologia.json", encoding="utf-8") as archivo:
        grafo = json.load(archivo)

    rutas = calcular(grafo, "A")

    assert {
        destino: (ruta.costo, ruta.siguiente_salto) for destino, ruta in rutas.items()
    } == {
        "A": (0, "A"),
        "B": (7, "B"),
        "C": (7, "C"),
        "D": (7, "I"),
        "E": (8, "I"),
        "F": (8, "I"),
        "G": (11, "I"),
        "H": (12, "I"),
        "I": (1, "I"),
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
