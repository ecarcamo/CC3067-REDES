import json
from pathlib import Path

import pytest

from algoritmos.contrato import EstadoVerificacion
from algoritmos.fletcher import Fletcher

VECTORES = json.loads((Path(__file__).parents[2] / "docs/vectores.json").read_text())["fletcher"]


@pytest.mark.parametrize("vector", VECTORES)
def test_vectores_compartidos(vector):
    resultado = Fletcher().verificar(vector["trama_recibida"], vector["parametros"])
    assert resultado.estado.value == vector["estado_esperado"]
    assert resultado.bits == vector["bits_esperados"]


@pytest.mark.parametrize("tamano", [8, 16, 32])
def test_detecta_bit_alterado_y_preserva_longitud(tamano):
    codificada = Fletcher(tamano).calcular("10101")
    alterada = ("1" if codificada.bits[0] == "0" else "0") + codificada.bits[1:]
    assert Fletcher().verificar(alterada, codificada.parametros).estado == EstadoVerificacion.ERROR_NO_CORREGIBLE
    assert Fletcher().verificar(codificada.bits, codificada.parametros).bits == "10101"
