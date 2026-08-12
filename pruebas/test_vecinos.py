"""Pruebas del descubrimiento de vecinos por HELLO y de su vencimiento."""

import time

from control.vecinos import GestorVecinos

VECINOS = {"B": 7, "I": 1, "C": 7}


def test_un_vecino_nace_muerto_hasta_su_primer_hello():
    gestor = GestorVecinos(VECINOS)
    assert gestor.vivos() == []
    assert gestor.enlaces_activos() == {}
    assert gestor.configurados == ["B", "C", "I"]


def test_el_primer_hello_lo_activa_y_el_segundo_no_avisa_de_nuevo():
    gestor = GestorVecinos(VECINOS)
    assert gestor.registrar_hello("I") is True
    assert gestor.registrar_hello("I") is False
    assert gestor.vivos() == ["I"]


def test_se_ignora_el_hello_de_quien_no_es_vecino():
    """Sin costo en la topologia compartida no hay nada que anunciar."""
    gestor = GestorVecinos(VECINOS)
    assert gestor.registrar_hello("Z") is False
    assert gestor.vivos() == []


def test_solo_se_anuncian_los_vecinos_vivos():
    gestor = GestorVecinos(VECINOS)
    gestor.registrar_hello("I")
    gestor.registrar_hello("C")
    assert gestor.enlaces_activos() == {"C": 7, "I": 1}


def test_el_vecino_callado_vence_y_sale_del_anuncio():
    gestor = GestorVecinos(VECINOS, timeout=0.05)
    gestor.registrar_hello("I")
    gestor.registrar_hello("C")

    time.sleep(0.08)
    gestor.registrar_hello("C")  # C sigue hablando, I no

    assert gestor.vencidos() == ["I"]
    assert gestor.enlaces_activos() == {"C": 7}
    assert gestor.esta_vivo("I") is False


def test_un_vecino_solo_vence_una_vez():
    """El vencimiento dispara un unico LSA, no uno por cada revision."""
    gestor = GestorVecinos(VECINOS, timeout=0.01)
    gestor.registrar_hello("B")
    time.sleep(0.03)

    assert gestor.vencidos() == ["B"]
    assert gestor.vencidos() == []


def test_un_vecino_puede_revivir():
    gestor = GestorVecinos(VECINOS, timeout=0.01)
    gestor.registrar_hello("B")
    time.sleep(0.03)
    gestor.vencidos()

    assert gestor.registrar_hello("B") is True
    assert gestor.enlaces_activos() == {"B": 7}
