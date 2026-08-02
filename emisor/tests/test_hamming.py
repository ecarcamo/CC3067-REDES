import json
from pathlib import Path

import pytest

from algoritmos.contrato import EstadoVerificacion
from algoritmos.hamming import Hamming, calcular_bits_paridad, codificar_bloque, decodificar_bloque

RUTA_VECTORES = Path(__file__).resolve().parents[2] / "docs" / "vectores.json"


def cargar_vectores() -> list[dict]:
    with open(RUTA_VECTORES, encoding="utf-8") as archivo:
        return json.load(archivo)["hamming"]


def test_calcular_bits_paridad_para_un_caracter_ascii():
    assert calcular_bits_paridad(8) == 4


def test_codificar_y_decodificar_sin_error_recupera_bits_identicos():
    bits_datos = "01000001"  # 'A'
    trama = codificar_bloque(bits_datos)
    recuperado, posicion_error = decodificar_bloque(trama)
    assert recuperado == bits_datos
    assert posicion_error == 0


def test_voltear_un_bit_en_cada_posicion_siempre_corrige():
    bits_datos = "01000001"
    trama = codificar_bloque(bits_datos)
    for posicion in range(len(trama)):
        trama_con_error = list(trama)
        trama_con_error[posicion] = "1" if trama_con_error[posicion] == "0" else "0"
        recuperado, posicion_error = decodificar_bloque("".join(trama_con_error))
        assert recuperado == bits_datos
        assert posicion_error == posicion + 1


def test_voltear_dos_bits_no_garantiza_el_resultado_correcto():
    """Limitacion conocida: Hamming simple (SEC) no detecta errores dobles de forma confiable."""
    bits_datos = "01000001"
    trama = codificar_bloque(bits_datos)
    trama_con_error = list(trama)
    trama_con_error[0] = "1" if trama_con_error[0] == "0" else "0"
    trama_con_error[1] = "1" if trama_con_error[1] == "0" else "0"
    recuperado, _ = decodificar_bloque("".join(trama_con_error))
    assert recuperado != bits_datos


def test_mensaje_de_varios_caracteres_procesa_todos_los_bloques():
    hamming = Hamming()
    bits = "".join(format(ord(c), "08b") for c in "Hola")
    trama_codificada = hamming.calcular(bits)
    assert trama_codificada.parametros["bloques"] == 4

    resultado = hamming.verificar(trama_codificada.bits, trama_codificada.parametros)
    assert resultado.estado == EstadoVerificacion.SIN_ERROR
    assert resultado.bits == bits


@pytest.mark.parametrize("vector", cargar_vectores())
def test_vectores_compartidos(vector):
    hamming = Hamming()
    resultado = hamming.verificar(vector["trama_recibida"], vector["parametros"])
    assert resultado.estado.value == vector["estado_esperado"]
    assert resultado.bits == vector["bits_esperados"]
