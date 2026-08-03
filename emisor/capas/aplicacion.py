"""Capa de aplicacion: interaccion con el usuario del cajero automatico."""

import json

from algoritmos.contrato import EstadoVerificacion, ResultadoVerificacion

ALGORITMOS_VALIDOS = ("hamming", "crc32", "fletcher")


def _solicitar_entero(mensaje: str, validos: set[int] | None = None) -> int:
    while True:
        try:
            valor = int(input(mensaje).strip())
            if valor >= 1 and (validos is None or valor in validos):
                return valor
        except ValueError:
            pass
        print(">> Configuracion invalida.")


def solicitar_configuracion() -> tuple[str, float, dict]:
    """Pide el algoritmo de integridad y la tasa de error para toda la sesion."""
    algoritmo = ""
    while algoritmo not in ALGORITMOS_VALIDOS:
        algoritmo = input(f"Algoritmo ({'/'.join(ALGORITMOS_VALIDOS)}): ").strip().lower()

    parametros = {}
    if algoritmo == "hamming":
        parametros["m"] = _solicitar_entero("Bits de datos por bloque m (ej. 4/8/11/16): ")
    elif algoritmo == "fletcher":
        parametros["tamano_bloque"] = _solicitar_entero(
            "Tamano de bloque Fletcher (8/16/32): ", {8, 16, 32}
        )

    while True:
        try:
            probabilidad = float(input("Tasa de error por bit (ej. 0.01): ").strip())
            if 0 <= probabilidad <= 1:
                break
        except ValueError:
            pass
        print(">> La tasa debe estar entre 0 y 1.")
    return algoritmo, probabilidad, parametros


def solicitar_login() -> str:
    """Pide numero de tarjeta y PIN. Devuelve el mensaje de aplicacion (JSON) para el banco."""
    card = input("Numero de tarjeta: ").strip()
    pin = input("PIN: ").strip()
    return json.dumps({"action": "login", "data": {"card": card, "pin": pin}})


def solicitar_opcion_menu() -> str:
    """Muestra el menu del cajero y pide una opcion."""
    print("\n--- MENU ---")
    print("1) Retirar dinero")
    print("2) Salir")
    return input("Elige una opcion: ").strip()


def solicitar_retiro() -> str:
    """Pide el monto a retirar. Devuelve el mensaje de aplicacion (JSON) para el banco."""
    monto = float(input("Monto a retirar: ").strip())
    return json.dumps({"action": "withdraw", "data": {"amount": monto}})


def mensaje_logout() -> str:
    """Mensaje de aplicacion (JSON) para cerrar sesion."""
    return json.dumps({"action": "logout", "data": {}})


def es_login_exitoso(texto: str) -> bool:
    return json.loads(texto).get("action") == "login_ok"


def mostrar_mensaje(texto: str | None, resultado: ResultadoVerificacion) -> None:
    """Imprime la respuesta del banco, o el motivo si no se pudo recuperar el mensaje."""
    if texto is None:
        print(f">> Error de transmision: {resultado.detalle}")
        return

    if resultado.estado == EstadoVerificacion.CORREGIDO:
        print(f">> (se corrigio un error de transmision: {resultado.detalle})")

    try:
        respuesta = json.loads(texto)
    except json.JSONDecodeError:
        print(">> Respuesta corrupta del banco")
        return
    data = respuesta.get("data", {})

    if respuesta.get("action") == "withdraw_ok":
        print(f">> Por favor tome sus ${data['amount']:.2f}")
        print(f">> Saldo restante: ${data['balance']:.2f}")
    else:
        print(">> " + data.get("message", str(data)))
