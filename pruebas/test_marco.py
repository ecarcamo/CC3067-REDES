"""Pruebas de la delimitacion de mensajes sobre el flujo TCP."""

import socket

import pytest

from transporte.marco import ErrorMarco, LectorLineas


@pytest.fixture
def par_de_sockets():
    emisor, receptor = socket.socketpair()
    try:
        yield emisor, receptor
    finally:
        emisor.close()
        receptor.close()


def test_lee_mensajes_completos(par_de_sockets):
    emisor, receptor = par_de_sockets
    emisor.sendall(b'{"type": "HELLO"}\n{"type": "LSA"}\n')

    lector = LectorLineas(receptor)
    assert lector.leer_linea() == '{"type": "HELLO"}'
    assert lector.leer_linea() == '{"type": "LSA"}'


def test_arma_un_mensaje_partido_en_varios_envios(par_de_sockets):
    """Un recv puede devolver medio mensaje: el lector espera al delimitador."""
    emisor, receptor = par_de_sockets
    emisor.sendall(b'{"type": ')
    emisor.sendall(b'"HELLO"}')
    emisor.sendall(b"\n")

    assert LectorLineas(receptor).leer_linea() == '{"type": "HELLO"}'


def test_devuelve_none_cuando_cierran_la_conexion(par_de_sockets):
    emisor, receptor = par_de_sockets
    emisor.sendall(b"unica\n")
    emisor.close()

    lector = LectorLineas(receptor)
    assert lector.leer_linea() == "unica"
    assert lector.leer_linea() is None


def test_una_trama_de_bits_pasa_intacta(par_de_sockets):
    """El delimitador no colisiona con el plano de datos: solo hay ceros y unos."""
    emisor, receptor = par_de_sockets
    emisor.sendall(b"01100110000111\n")

    assert LectorLineas(receptor).leer_linea() == "01100110000111"


def test_rechaza_lo_que_no_es_utf8(par_de_sockets):
    emisor, receptor = par_de_sockets
    emisor.sendall(b"\xff\xfe\n")

    with pytest.raises(ErrorMarco):
        LectorLineas(receptor).leer_linea()
