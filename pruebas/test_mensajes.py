"""Pruebas del formato de los mensajes acordado entre las tres parejas."""

import json

import pytest

from protocolo import mensajes
from protocolo.constantes import TTL_DATOS, TTL_HELLO, TTL_LSA


def test_el_hello_lleva_los_campos_de_la_definicion():
    assert mensajes.crear_hello("A") == {
        "proto": "LinkState",
        "type": "HELLO",
        "from": "A",
        "ttl": TTL_HELLO,
    }


def test_el_lsa_lleva_los_campos_de_la_definicion():
    lsa = mensajes.crear_lsa("A", 3, {"B": 7, "I": 1, "C": 7})
    assert lsa == {
        "proto": "LinkState",
        "type": "LSA",
        "origin": "A",
        "seq": 3,
        "links": {"B": 7, "I": 1, "C": 7},
        "from": "A",
        "ttl": TTL_LSA,
    }


def test_el_sobre_de_datos_arranca_con_el_origen_en_hops():
    sobre = mensajes.crear_sobre("A", "E", mensajes.payload_withdraw(500))
    assert sobre["type"] == "message"
    assert sobre["from"] == "A"
    assert sobre["to"] == "E"
    assert sobre["ttl"] == TTL_DATOS
    assert sobre["hops"] == ["A"]
    assert sobre["payload"] == {"op": "withdraw", "amount": 500}


def test_el_control_viaja_como_una_linea_json():
    crudo = mensajes.serializar_control(mensajes.crear_hello("A"))
    assert crudo.endswith(b"\n")
    assert crudo.count(b"\n") == 1
    assert json.loads(crudo.decode("utf-8"))["type"] == "HELLO"


def test_el_sobre_de_datos_viaja_codificado_con_hamming():
    sobre = mensajes.crear_sobre("A", "E", mensajes.payload_auth("23016", "1234"))
    crudo = mensajes.serializar_datos(sobre)

    linea = crudo.decode("utf-8").strip()
    assert set(linea) <= {"0", "1"}

    recuperado, correcciones = mensajes.deserializar_datos(linea)
    assert recuperado == sobre
    assert correcciones == 0


def test_clasificar_separa_los_dos_planos():
    hello = mensajes.serializar_control(mensajes.crear_hello("A")).decode().strip()
    datos = mensajes.serializar_datos(mensajes.crear_sobre("A", "E", {"op": "logout"})).decode().strip()

    assert mensajes.clasificar(hello) == mensajes.CONTROL
    assert mensajes.clasificar(datos) == mensajes.DATOS
    assert mensajes.clasificar("cualquier cosa") == mensajes.DESCONOCIDO
    assert mensajes.clasificar("") == mensajes.DESCONOCIDO


def test_un_campo_desconocido_no_descarta_la_trama():
    """La definicion es explicita: lo que no reconocemos se ignora."""
    lsa = mensajes.crear_lsa("A", 1, {"B": 7})
    lsa["metrica_experimental"] = 42
    lsa["proto"] = "LinkStateExtendido"

    mensajes.validar_lsa(lsa)  # no debe levantar


def test_valida_lo_que_el_protocolo_exige():
    with pytest.raises(mensajes.ErrorProtocolo):
        mensajes.validar_lsa({"type": "LSA", "origin": "A", "seq": 1})  # sin links
    with pytest.raises(mensajes.ErrorProtocolo):
        mensajes.validar_lsa({"type": "LSA", "origin": "A", "from": "A", "seq": 1, "links": []})
    with pytest.raises(mensajes.ErrorProtocolo):
        mensajes.validar_hello({"type": "HELLO"})  # sin from
    with pytest.raises(mensajes.ErrorProtocolo):
        mensajes.validar_sobre({"type": "message", "from": "A", "to": "E", "ttl": 16})


def test_un_seq_booleano_no_pasa_por_entero():
    """En Python True es 1, y aceptarlo desordenaria la comparacion de versiones."""
    with pytest.raises(mensajes.ErrorProtocolo):
        mensajes.validar_lsa({"type": "LSA", "origin": "A", "from": "A", "seq": True, "links": {}})


def test_una_linea_de_control_rota_se_reporta():
    with pytest.raises(mensajes.ErrorProtocolo):
        mensajes.deserializar_control("{esto no es json")
    with pytest.raises(mensajes.ErrorProtocolo):
        mensajes.deserializar_control("[1, 2, 3]")
