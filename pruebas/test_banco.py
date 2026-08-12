"""Pruebas de la lógica de negocio reutilizada del laboratorio 2."""

from endpoints.banco import LogicaBanco
from protocolo import mensajes


def test_banco_autentica_retira_y_cierra_sesion():
    banco = LogicaBanco({"usuario": {"pin": "1234", "balance": 100.0}})

    assert banco.procesar(mensajes.payload_auth("usuario", "1234"))["ok"] is True
    retiro = banco.procesar(mensajes.payload_withdraw(40))
    assert retiro["amount"] == 40
    assert retiro["balance"] == 60
    assert banco.procesar(mensajes.payload_logout())["ok"] is True
    assert banco.procesar(mensajes.payload_withdraw(1))["code"] == "SESSION"


def test_banco_rechaza_credenciales_monto_y_fondos_invalidos():
    banco = LogicaBanco({"usuario": {"pin": "1234", "balance": 100.0}})

    assert banco.procesar(mensajes.payload_auth("usuario", "malo"))["code"] == "AUTH"
    banco.procesar(mensajes.payload_auth("usuario", "1234"))
    assert banco.procesar(mensajes.payload_withdraw(0))["code"] == "AMOUNT"
    assert banco.procesar(mensajes.payload_withdraw(101))["code"] == "FUNDS"


def test_autenticacion_fallida_invalida_una_sesion_anterior():
    banco = LogicaBanco({"usuario": {"pin": "1234", "balance": 100.0}})
    banco.procesar(mensajes.payload_auth("usuario", "1234"))

    banco.procesar(mensajes.payload_auth("usuario", "incorrecto"))

    assert banco.procesar(mensajes.payload_withdraw(1))["code"] == "SESSION"
