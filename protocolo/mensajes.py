"""Construccion, validacion y serializacion de los mensajes del protocolo.

Aqui vive la unica traduccion entre un diccionario de Python y lo que viaja por
el socket. Dos reglas de la definicion grupal mandan sobre todo el modulo:

* El plano de control (HELLO y LSA) viaja como una linea JSON en UTF-8
  terminada en `\\n`. El plano de datos viaja siempre codificado con
  Hamming(7,4), sin ninguna marca extra que lo anuncie.
* Un campo que no reconocemos se ignora, no descartamos la trama. Por eso la
  validacion solo exige lo que el protocolo declara obligatorio y deja pasar
  cualquier agregado de los otros grupos.
"""

import json

from protocolo import hamming
from protocolo.constantes import (
    CODIFICACION,
    DELIMITADOR,
    PROTO,
    TIPO_HELLO,
    TIPO_LSA,
    TIPO_MENSAJE,
    TTL_DATOS,
    TTL_HELLO,
    TTL_LSA,
)

CONTROL = "control"
DATOS = "datos"
DESCONOCIDO = "desconocido"


class ErrorProtocolo(ValueError):
    """El mensaje no cumple el minimo que exige la definicion grupal."""


# --- Construccion -----------------------------------------------------------


def crear_hello(origen: str) -> dict:
    """HELLO de descubrimiento. Nace con ttl 1 porque nunca se reenvia."""
    return {"proto": PROTO, "type": TIPO_HELLO, "from": origen, "ttl": TTL_HELLO}


def crear_lsa(origen: str, seq: int, enlaces: dict[str, int]) -> dict:
    """Anuncio de estado de enlace del propio nodo, listo para inundar."""
    return {
        "proto": PROTO,
        "type": TIPO_LSA,
        "origin": origen,
        "seq": seq,
        "links": dict(enlaces),
        "from": origen,
        "ttl": TTL_LSA,
    }


def crear_sobre(
    origen: str,
    destino: str,
    payload: dict,
    ttl: int = TTL_DATOS,
    hops: list[str] | None = None,
) -> dict:
    """Sobre de datos entre el ATM y el servidor bancario."""
    return {
        "type": TIPO_MENSAJE,
        "from": origen,
        "to": destino,
        "ttl": ttl,
        "hops": list(hops) if hops is not None else [origen],
        "payload": dict(payload),
    }


# --- Payloads de aplicacion (seccion 5 del protocolo) -----------------------


def payload_auth(usuario: str, pin: str) -> dict:
    return {"op": "auth", "user": usuario, "pin": pin}


def payload_withdraw(monto: float) -> dict:
    return {"op": "withdraw", "amount": monto}


def payload_error(codigo: str, mensaje: str) -> dict:
    return {"op": "error", "code": codigo, "msg": mensaje}


def payload_logout() -> dict:
    return {"op": "logout"}


# --- Serializacion ----------------------------------------------------------


def serializar_control(mensaje: dict) -> bytes:
    """JSON en una sola linea: el plano de control no lleva Hamming."""
    return (json.dumps(mensaje, ensure_ascii=False) + DELIMITADOR).encode(CODIFICACION)


def serializar_datos(sobre: dict) -> bytes:
    """JSON -> Hamming(7,4). Los bits viajan como texto '0'/'1' terminado en `\\n`.

    El delimitador no crea ambiguedad porque una trama Hamming solo contiene
    ceros y unos, y sirve para recortar el mensaje dentro del flujo TCP.
    """
    bits = hamming.codificar_texto(json.dumps(sobre, ensure_ascii=False))
    return (bits + DELIMITADOR).encode(CODIFICACION)


def clasificar(linea: str) -> str:
    """Decide si una linea recibida es plano de control o plano de datos.

    Ambos planos comparten el puerto de escucha, y el protocolo no pide ninguna
    marca que los distinga, asi que la clasificacion es por contenido: un JSON
    de control siempre abre con '{' y una trama Hamming solo tiene '0' y '1'.
    """
    linea = linea.strip()
    if not linea:
        return DESCONOCIDO
    if hamming.es_trama_de_bits(linea):
        return DATOS
    if linea.startswith("{"):
        return CONTROL
    return DESCONOCIDO


def deserializar_control(linea: str) -> dict:
    """Convierte una linea de control en diccionario, sin validar aun el tipo."""
    try:
        mensaje = json.loads(linea)
    except json.JSONDecodeError as error:
        raise ErrorProtocolo("la linea de control no es JSON valido") from error
    if not isinstance(mensaje, dict):
        raise ErrorProtocolo("el mensaje de control debe ser un objeto JSON")
    return mensaje


def deserializar_datos(linea: str) -> tuple[dict, int]:
    """Decodifica Hamming y reconstruye el sobre. Devuelve el sobre y las correcciones."""
    texto, correcciones = hamming.decodificar_texto(linea.strip())
    try:
        sobre = json.loads(texto)
    except json.JSONDecodeError as error:
        raise ErrorProtocolo("el sobre de datos no es JSON valido tras decodificar") from error
    if not isinstance(sobre, dict):
        raise ErrorProtocolo("el sobre de datos debe ser un objeto JSON")
    return sobre, correcciones


# --- Validacion -------------------------------------------------------------


def validar_hello(mensaje: dict) -> None:
    _exigir_texto(mensaje, "from")
    if mensaje.get("type") != TIPO_HELLO:
        raise ErrorProtocolo("no es un HELLO")


def validar_lsa(mensaje: dict) -> None:
    if mensaje.get("type") != TIPO_LSA:
        raise ErrorProtocolo("no es un LSA")
    _exigir_texto(mensaje, "origin")
    _exigir_texto(mensaje, "from")
    _exigir_entero(mensaje, "seq")

    enlaces = mensaje.get("links")
    if not isinstance(enlaces, dict):
        raise ErrorProtocolo("'links' debe ser un objeto {vecino: costo}")
    for vecino, costo in enlaces.items():
        if not isinstance(vecino, str) or not vecino:
            raise ErrorProtocolo(f"nombre de vecino invalido en 'links': {vecino!r}")
        if isinstance(costo, bool) or not isinstance(costo, (int, float)):
            raise ErrorProtocolo(f"costo invalido para el enlace {vecino}: {costo!r}")


def validar_sobre(sobre: dict) -> None:
    if sobre.get("type") != TIPO_MENSAJE:
        raise ErrorProtocolo("no es un sobre de datos")
    _exigir_texto(sobre, "from")
    _exigir_texto(sobre, "to")
    _exigir_entero(sobre, "ttl")

    saltos = sobre.get("hops", [])
    if not isinstance(saltos, list) or any(not isinstance(salto, str) for salto in saltos):
        raise ErrorProtocolo("'hops' debe ser una lista de nombres de nodo")
    if not isinstance(sobre.get("payload"), dict):
        raise ErrorProtocolo("'payload' debe ser un objeto JSON")


def _exigir_texto(mensaje: dict, campo: str) -> None:
    valor = mensaje.get(campo)
    if not isinstance(valor, str) or not valor:
        raise ErrorProtocolo(f"falta el campo de texto '{campo}'")


def _exigir_entero(mensaje: dict, campo: str) -> None:
    valor = mensaje.get(campo)
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ErrorProtocolo(f"falta el campo entero '{campo}'")
