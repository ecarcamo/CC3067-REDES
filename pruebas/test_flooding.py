"""Pruebas del flooding del LSA y del manejo de ciclos en el plano de control."""

import json

import pytest

from configuracion import Configuracion
from control.plano import PlanoControl
from protocolo import mensajes

VECINOS = {"B": 7, "I": 1, "C": 7}


class EnlacesFalsos:
    """Sustituto de `transporte.Enlaces` que solo anota lo que se habria enviado."""

    def __init__(self):
        self.enviados: list[tuple[str, dict]] = []

    def enviar(self, destino: str, datos: bytes) -> bool:
        self.enviados.append((destino, json.loads(datos.decode("utf-8"))))
        return True

    def difundir(self, destinos, datos: bytes) -> list[str]:
        return [destino for destino in destinos if self.enviar(destino, datos)]

    def destinos_de(self, tipo: str) -> list[str]:
        return [destino for destino, mensaje in self.enviados if mensaje.get("type") == tipo]

    def ultimo(self, tipo: str) -> dict:
        for _, mensaje in reversed(self.enviados):
            if mensaje.get("type") == tipo:
                return mensaje
        raise AssertionError(f"no se envio ningun {tipo}")


def crear_plano(directorio, vivos=tuple(VECINOS)) -> tuple[PlanoControl, EnlacesFalsos]:
    """Arma un plano de control aislado, con los vecinos que se le indiquen vivos."""
    configuracion = Configuracion(
        identificador="A",
        vecinos=dict(VECINOS),
        direcciones={},
        topologia={},
        host=None,
    )
    enlaces = EnlacesFalsos()
    plano = PlanoControl(configuracion, enlaces, directorio_estado=directorio)
    for vecino in vivos:
        plano.vecinos.registrar_hello(vecino)
    enlaces.enviados.clear()
    return plano, enlaces


@pytest.fixture
def plano_y_enlaces(tmp_path):
    return crear_plano(tmp_path)


def test_reenvia_a_todos_los_vecinos_menos_al_que_lo_mando(plano_y_enlaces):
    plano, enlaces = plano_y_enlaces
    lsa = mensajes.crear_lsa("F", 1, {"B": 2, "D": 1})
    lsa["from"] = "B"

    plano.manejar(lsa, "127.0.0.1")

    assert sorted(enlaces.destinos_de("LSA")) == ["C", "I"]


def test_al_reenviar_baja_el_ttl_y_cambia_el_remitente(plano_y_enlaces):
    plano, enlaces = plano_y_enlaces
    lsa = mensajes.crear_lsa("F", 1, {"B": 2})
    lsa["from"] = "B"

    plano.manejar(lsa, "127.0.0.1")

    reenviado = enlaces.ultimo("LSA")
    assert reenviado["ttl"] == 7  # arranca en 8
    assert reenviado["from"] == "A"  # cambia en cada salto
    assert reenviado["origin"] == "F"  # no cambia nunca
    assert reenviado["seq"] == 1


def test_el_repetido_no_se_reenvia(plano_y_enlaces):
    """El numero de secuencia es lo que corta el ciclo."""
    plano, enlaces = plano_y_enlaces
    lsa = mensajes.crear_lsa("F", 1, {"B": 2})
    lsa["from"] = "B"
    plano.manejar(lsa, "127.0.0.1")
    enlaces.enviados.clear()

    repetido = mensajes.crear_lsa("F", 1, {"B": 2})
    repetido["from"] = "C"
    plano.manejar(repetido, "127.0.0.1")

    assert enlaces.destinos_de("LSA") == []


def test_el_viejo_no_se_reenvia_ni_pisa_el_grafo(plano_y_enlaces):
    plano, enlaces = plano_y_enlaces
    nuevo = mensajes.crear_lsa("F", 5, {"B": 2})
    nuevo["from"] = "B"
    plano.manejar(nuevo, "127.0.0.1")
    enlaces.enviados.clear()

    viejo = mensajes.crear_lsa("F", 3, {"B": 2, "D": 1})
    viejo["from"] = "C"
    plano.manejar(viejo, "127.0.0.1")

    assert enlaces.destinos_de("LSA") == []
    assert plano.lsdb.seq_de("F") == 5


def test_el_ttl_agotado_corta_el_reenvio(plano_y_enlaces):
    """Respaldo del seq para el nodo que reinicia y vuelve a numerar bajo."""
    plano, enlaces = plano_y_enlaces
    lsa = mensajes.crear_lsa("F", 1, {"B": 2})
    lsa["from"] = "B"
    lsa["ttl"] = 1

    plano.manejar(lsa, "127.0.0.1")

    assert plano.lsdb.seq_de("F") == 1  # el anuncio si se guarda
    assert enlaces.destinos_de("LSA") == []  # pero no se propaga


def test_un_lsa_propio_mas_nuevo_hace_saltar_la_secuencia(plano_y_enlaces):
    """Pasa tras un reinicio en el que se perdio el contador en disco."""
    plano, enlaces = plano_y_enlaces
    eco = mensajes.crear_lsa("A", 9, {"B": 7})
    eco["from"] = "B"

    plano.manejar(eco, "127.0.0.1")

    emitido = enlaces.ultimo("LSA")
    assert emitido["origin"] == "A"
    assert emitido["seq"] == 10
    assert plano.lsdb.seq_de("A") == 10


def test_un_eco_propio_viejo_no_provoca_nada(plano_y_enlaces):
    """Si no, cada vuelta del eco dispararia un anuncio nuevo sin parar."""
    plano, enlaces = plano_y_enlaces
    plano.secuencia.alcanzar(4)
    eco = mensajes.crear_lsa("A", 2, {"B": 7})
    eco["from"] = "B"

    plano.manejar(eco, "127.0.0.1")

    assert enlaces.enviados == []


def test_al_vecino_que_se_levanta_se_le_manda_lo_que_ya_sabemos(tmp_path):
    """Acorta la convergencia sin tocar el formato del protocolo."""
    plano, enlaces = crear_plano(tmp_path, vivos=())
    plano.lsdb.registrar("F", 3, {"B": 2, "D": 1})
    plano.lsdb.registrar("D", 2, {"F": 1})

    plano.manejar(mensajes.crear_hello("C"), "127.0.0.1")

    assert enlaces.destinos_de("LSA") == ["C", "C"]
    origenes = {mensaje["origin"] for _, mensaje in enlaces.enviados}
    assert origenes == {"F", "D"}


def test_el_hello_de_quien_no_es_vecino_no_dispara_sincronizacion(tmp_path):
    plano, enlaces = crear_plano(tmp_path, vivos=())
    plano.lsdb.registrar("F", 3, {"B": 2})

    plano.manejar(mensajes.crear_hello("Z"), "127.0.0.1")

    assert enlaces.enviados == []


def test_un_tipo_desconocido_no_rompe_el_plano(plano_y_enlaces):
    plano, enlaces = plano_y_enlaces
    plano.manejar({"proto": "LinkState", "type": "BYE", "from": "B"}, "127.0.0.1")
    assert enlaces.enviados == []
