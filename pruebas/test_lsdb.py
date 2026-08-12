"""Pruebas de la base de estado de enlace y del corte de ciclos por numero de secuencia."""

from control.lsdb import BaseEstadoEnlaces


def test_acepta_el_primer_anuncio():
    lsdb = BaseEstadoEnlaces()
    assert lsdb.registrar("B", 1, {"A": 7}) is True
    assert lsdb.seq_de("B") == 1


def test_descarta_el_repetido_y_el_viejo():
    """Aqui muere el flooding: un seq menor o igual no se guarda ni se reenvia."""
    lsdb = BaseEstadoEnlaces()
    lsdb.registrar("B", 5, {"A": 7})

    assert lsdb.registrar("B", 5, {"A": 7}) is False
    assert lsdb.registrar("B", 4, {"A": 7, "F": 2}) is False
    assert lsdb.seq_de("B") == 5


def test_acepta_el_mas_nuevo_y_reemplaza():
    lsdb = BaseEstadoEnlaces()
    lsdb.registrar("B", 1, {"A": 7, "F": 2})

    assert lsdb.registrar("B", 2, {"A": 7}) is True
    assert lsdb.seq_de("B") == 2
    assert lsdb.grafo().get("B") == {}  # A todavia no anuncio de vuelta


def test_la_version_solo_sube_cuando_el_grafo_cambia():
    """Un refresco con los mismos enlaces no debe disparar un recalculo."""
    lsdb = BaseEstadoEnlaces()
    lsdb.registrar("B", 1, {"A": 7})
    version = lsdb.version

    lsdb.registrar("B", 2, {"A": 7})
    assert lsdb.version == version

    lsdb.registrar("B", 3, {"A": 7, "F": 2})
    assert lsdb.version > version


def test_el_grafo_solo_toma_los_enlaces_que_ambos_extremos_anuncian():
    lsdb = BaseEstadoEnlaces()
    lsdb.registrar("A", 1, {"B": 7, "C": 7})
    lsdb.registrar("B", 1, {"A": 7})
    # C no anuncia de vuelta el enlace con A: puede haberse caido.

    grafo = lsdb.grafo()
    assert grafo["A"] == {"B": 7}
    assert grafo["B"] == {"A": 7}


def test_ante_costos_distintos_se_toma_el_mayor():
    lsdb = BaseEstadoEnlaces()
    lsdb.registrar("A", 1, {"B": 7})
    lsdb.registrar("B", 1, {"A": 9})

    grafo = lsdb.grafo()
    assert grafo["A"]["B"] == 9
    assert grafo["B"]["A"] == 9


def test_el_grafo_queda_simetrico():
    lsdb = BaseEstadoEnlaces()
    lsdb.registrar("A", 1, {"I": 1})
    lsdb.registrar("I", 1, {"A": 1, "D": 6})
    lsdb.registrar("D", 1, {"I": 6})

    grafo = lsdb.grafo()
    for nodo, adyacentes in grafo.items():
        for vecino, costo in adyacentes.items():
            assert grafo[vecino][nodo] == costo
