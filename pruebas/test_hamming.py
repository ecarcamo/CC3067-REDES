"""Pruebas del codec Hamming(7,4) contra lo que fija la seccion 5 del protocolo."""

import pytest

from protocolo import hamming


def test_el_bloque_sigue_el_orden_acordado():
    """El nibble 1011 produce p1 p2 d1 p3 d2 d3 d4 con paridad par."""
    # d1=1 d2=0 d3=1 d4=1  ->  p1=d1^d2^d4=0, p2=d1^d3^d4=1, p3=d2^d3^d4=0
    assert hamming.codificar_nibble(0b1011) == "0110011"


def test_cada_byte_ocupa_catorce_bits():
    assert len(hamming.codificar_bytes(b"A")) == 14
    assert len(hamming.codificar_texto("hola")) == 4 * 14


def test_el_nibble_alto_va_primero():
    """La definicion pide partir cada byte desde el mas significativo."""
    bits = hamming.codificar_bytes(bytes([0xA5]))
    assert bits[:7] == hamming.codificar_nibble(0xA)
    assert bits[7:] == hamming.codificar_nibble(0x5)


@pytest.mark.parametrize("nibble", range(16))
def test_ida_y_vuelta_de_todos_los_nibbles(nibble):
    recuperado, sindrome = hamming.decodificar_bloque(hamming.codificar_nibble(nibble))
    assert (recuperado, sindrome) == (nibble, 0)


@pytest.mark.parametrize("nibble", range(16))
@pytest.mark.parametrize("posicion", range(7))
def test_corrige_un_error_en_cualquier_posicion(nibble, posicion):
    """Hamming(7,4) corrige un bit volteado, este donde este dentro del bloque."""
    bloque = list(hamming.codificar_nibble(nibble))
    bloque[posicion] = "1" if bloque[posicion] == "0" else "0"

    recuperado, sindrome = hamming.decodificar_bloque("".join(bloque))
    assert recuperado == nibble
    assert sindrome == posicion + 1


def test_ida_y_vuelta_de_un_texto_con_acentos():
    texto = '{"op": "auth", "user": "Esteban Cárcamo", "pin": "1234"}'
    recuperado, correcciones = hamming.decodificar_texto(hamming.codificar_texto(texto))
    assert recuperado == texto
    assert correcciones == 0


def test_corrige_un_bit_por_bloque_en_un_mensaje_completo():
    texto = '{"type": "message", "to": "E"}'
    bits = list(hamming.codificar_texto(texto))
    # Un error por bloque de siete bits es justo lo que el algoritmo garantiza.
    for inicio in range(0, len(bits), 7):
        bits[inicio] = "1" if bits[inicio] == "0" else "0"

    recuperado, correcciones = hamming.decodificar_texto("".join(bits))
    assert recuperado == texto
    assert correcciones == len(bits) // 7


def test_rechaza_una_trama_de_longitud_invalida():
    with pytest.raises(hamming.ErrorHamming):
        hamming.decodificar_bytes("0110011")  # medio byte


def test_rechaza_caracteres_que_no_son_bits():
    with pytest.raises(hamming.ErrorHamming):
        hamming.decodificar_bloque("011x011")


def test_distingue_una_trama_de_bits_de_un_json():
    assert hamming.es_trama_de_bits("0110011")
    assert not hamming.es_trama_de_bits('{"type": "HELLO"}')
    assert not hamming.es_trama_de_bits("")
