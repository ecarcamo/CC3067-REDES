import json
import zlib
from pathlib import Path

import pytest

from algoritmos.contrato import EstadoVerificacion
from algoritmos.crc32 import Crc32, calcular_crc

RUTA_VECTORES = Path(__file__).resolve().parents[2] / "docs" / "vectores.json"


def cargar_vectores() -> list[dict]:
    with open(RUTA_VECTORES, encoding="utf-8") as archivo:
        return json.load(archivo)["crc32"]


def _texto_a_bits(texto: str) -> str:
    return "".join(format(ord(c), "08b") for c in texto)


def test_calcular_crc_coincide_con_zlib():
    bits = _texto_a_bits("Hola")
    assert calcular_crc(bits) == zlib.crc32("Hola".encode("ascii"))


def test_codificar_y_verificar_sin_error_recupera_bits_identicos():
    crc32 = Crc32()
    bits = _texto_a_bits("Hola")
    trama_codificada = crc32.calcular(bits)

    resultado = crc32.verificar(trama_codificada.bits, trama_codificada.parametros)
    assert resultado.estado == EstadoVerificacion.SIN_ERROR
    assert resultado.bits == bits


def test_bit_alterado_se_detecta_como_error_no_corregible():
    crc32 = Crc32()
    bits = _texto_a_bits("Hola")
    trama_codificada = crc32.calcular(bits)

    trama_con_error = list(trama_codificada.bits)
    trama_con_error[0] = "1" if trama_con_error[0] == "0" else "0"

    resultado = crc32.verificar("".join(trama_con_error), trama_codificada.parametros)
    assert resultado.estado == EstadoVerificacion.ERROR_NO_CORREGIBLE
    assert resultado.bits is None


def test_crc_nunca_devuelve_corregido():
    """CRC-32 es un algoritmo de deteccion: nunca corrige, solo detecta."""
    crc32 = Crc32()
    bits = _texto_a_bits("X")
    trama_codificada = crc32.calcular(bits)

    trama_con_error = list(trama_codificada.bits)
    trama_con_error[3] = "1" if trama_con_error[3] == "0" else "0"
    resultado = crc32.verificar("".join(trama_con_error), trama_codificada.parametros)

    assert resultado.estado != EstadoVerificacion.CORREGIDO


@pytest.mark.parametrize("vector", cargar_vectores())
def test_vectores_compartidos(vector):
    crc32 = Crc32()
    resultado = crc32.verificar(vector["trama_recibida"], vector["parametros"])
    assert resultado.estado.value == vector["estado_esperado"]
    if vector["estado_esperado"] == "sin_error":
        assert resultado.bits == vector["bits_esperados"]
