import json

import pytest

from algoritmos.contrato import EstadoVerificacion, ResultadoVerificacion
from capas.aplicacion import mostrar_mensaje
from capas.presentacion import codificar_mensaje, decodificar_mensaje
from capas.ruido import aplicar_ruido
from capas.transmision import LectorLineas, recibir_informacion


class SocketFalso:
    def __init__(self, fragmentos): self.fragmentos = iter(fragmentos)
    def recv(self, _): return next(self.fragmentos, b"")


def test_presentacion_ascii_y_errores():
    assert decodificar_mensaje(codificar_mensaje("Redes")) == "Redes"
    with pytest.raises(ValueError): decodificar_mensaje("1")
    with pytest.raises(ValueError): codificar_mensaje("ñ")


def test_ruido_limites_semilla_y_proporcion():
    bits = "01" * 5000
    assert aplicar_ruido(bits, 0) == (bits, [])
    assert aplicar_ruido("010", 1) == ("101", [0, 1, 2])
    assert aplicar_ruido(bits, .5, 7) == aplicar_ruido(bits, .5, 7)
    assert .47 < len(aplicar_ruido(bits, .5, 7)[1]) / len(bits) < .53


def test_lector_fragmenta_pega_y_cierra():
    lector = LectorLineas(SocketFalso([b'{"a"', b':1}\n{"b":2}\n']))
    assert lector.leer_linea() == '{"a":1}'
    assert lector.leer_linea() == '{"b":2}'
    assert LectorLineas(SocketFalso([b"incompleto"])).leer_linea() is None


@pytest.mark.parametrize("sobre", [{"version": 2, "algoritmo": "crc32", "parametros": {}, "trama": "0"}, {"version": 1, "algoritmo": "crc32", "parametros": {}, "trama": "02"}])
def test_rechaza_sobres_invalidos(sobre):
    lector = LectorLineas(SocketFalso([(json.dumps(sobre) + "\n").encode()]))
    with pytest.raises(ValueError): recibir_informacion(lector)


def test_aplicacion_maneja_json_corrupto(capsys):
    mostrar_mensaje("{", ResultadoVerificacion(EstadoVerificacion.SIN_ERROR, "", ""))
    assert "Respuesta corrupta" in capsys.readouterr().out
