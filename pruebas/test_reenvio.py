"""Pruebas de las decisiones del plano de datos."""

from configuracion import Configuracion, Direccion, HostLocal
from control import tabla
from datos.reenvio import CLAVE_HOST_LOCAL, PlanoDatos
from protocolo import mensajes


class EnlacesFalsos:
    def __init__(self):
        self.registrados = {}
        self.envios = []

    def registrar(self, nombre, direccion):
        self.registrados[nombre] = direccion

    def enviar(self, destino, datos):
        self.envios.append((destino, datos))
        return True


def _plano(monkeypatch):
    config = Configuracion(
        identificador="A",
        vecinos={"I": 1},
        direcciones={"A": Direccion("127.0.0.1", 5001)},
        topologia={},
        host=None,
    )
    enlaces = EnlacesFalsos()
    monkeypatch.setattr(
        tabla,
        "cargar",
        lambda _identificador: {
            "E": tabla.EntradaTabla("E", "I", 8, "100.0.0.9", 5009)
        },
    )
    return PlanoDatos(config, enlaces), enlaces


def test_descarta_cuando_el_ttl_llega_a_cero(monkeypatch):
    plano, enlaces = _plano(monkeypatch)
    sobre = mensajes.crear_sobre("B", "E", {"op": "logout"}, ttl=1, hops=["B"])

    plano.manejar_trama(mensajes.serializar_datos(sobre).decode().strip(), "127.0.0.1")

    assert enlaces.envios == []


def test_descarta_un_bucle_si_el_nodo_ya_aparece_en_hops(monkeypatch):
    plano, enlaces = _plano(monkeypatch)
    sobre = mensajes.crear_sobre("B", "E", {"op": "logout"}, hops=["B", "A"])

    plano.manejar_trama(mensajes.serializar_datos(sobre).decode().strip(), "127.0.0.1")

    assert enlaces.envios == []


def test_inyeccion_local_consulta_csv_y_reenvia_sin_falso_bucle(monkeypatch):
    plano, enlaces = _plano(monkeypatch)
    sobre = mensajes.crear_sobre("A", "E", {"op": "logout"})

    plano.manejar_trama(mensajes.serializar_datos(sobre).decode().strip(), "127.0.0.1")

    destino, trama = enlaces.envios[0]
    reenviado, _ = mensajes.deserializar_datos(trama.decode().strip())
    assert destino == "I"
    assert reenviado["ttl"] == 15
    assert reenviado["hops"] == ["A"]
    assert enlaces.registrados["I"] == Direccion("100.0.0.9", 5009)


def test_entrega_local_no_consume_ttl(monkeypatch):
    plano, enlaces = _plano(monkeypatch)
    plano._configuracion = Configuracion(
        identificador="A",
        vecinos={},
        direcciones={"A": Direccion("127.0.0.1", 5001)},
        topologia={},
        host=HostLocal("atm", "127.0.0.1", 6001),
    )
    sobre = mensajes.crear_sobre("E", "A", {"op": "logout"}, ttl=1, hops=["E"])

    plano.manejar_trama(mensajes.serializar_datos(sobre).decode().strip(), "127.0.0.1")

    destino, trama = enlaces.envios[0]
    entregado, _ = mensajes.deserializar_datos(trama.decode().strip())
    assert destino == CLAVE_HOST_LOCAL
    assert entregado["ttl"] == 1
    assert entregado["hops"] == ["E"]
