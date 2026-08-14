"""Cajero automatico: el nodo cliente de la red.

El ATM no rutea. Arma el sobre de datos, lo codifica con Hamming(7,4) y se lo
entrega a su puerta de enlace, que es el router que lo declara como `host` en
`config/nombres.json` (en la configuracion que dejamos, el nodo A).

Como el router necesita poder devolverle la respuesta, el ATM tambien escucha en
su propio puerto, igual que hace un router: la conexion de ida y la de vuelta
son independientes, cada punta abre la suya para escribir. `transporte.Servidor`
y `transporte.Enlaces` sirven tal cual para las dos direcciones.

Flujo de una sesion, con los payload de la seccion 5 del protocolo:

1. pedir usuario y pin, mandar `payload_auth` y esperar la respuesta del banco,
2. mostrar el menu de retiro y salida,
3. mandar `payload_withdraw` con el monto y mostrar lo que responda el banco,
4. al salir, mandar `payload_logout`.

El sobre se arma con `protocolo.mensajes.crear_sobre(origen, destino, payload)`,
donde `origen` es el router del ATM y `destino` el del banco: son los nombres de
nodo que viajan en `from` y `to`, y son los que el plano de datos consulta en la
tabla de enrutamiento.

Las respuestas exitosas conservan la operacion solicitada, agregan `ok: true`
y los datos del resultado; las fallidas usan el `payload_error` acordado.
"""

import argparse
from queue import Empty, Queue
import sys
import time
import uuid

import bitacora
import configuracion
from protocolo import mensajes
from transporte.enlaces import Enlaces
from transporte.servidor import Servidor

TIMEOUT_RESPUESTA = 15.0


class Cajero:
    """Terminal interactiva conectada a un único router de puerta de enlace."""

    def __init__(self, config: configuracion.Configuracion, destino: str):
        if config.host is None or config.host.tipo != "atm":
            raise configuracion.ErrorConfiguracion(
                f"el nodo {config.identificador} no tiene un ATM configurado"
            )
        self._gateway = config.identificador
        self._destino = destino
        self._respuestas: Queue[dict] = Queue()
        self._enlaces = Enlaces({self._gateway: config.direccion_propia})
        self._servidor = Servidor(
            configuracion.Direccion(config.host.ip, config.host.puerto), self._recibir
        )

    def iniciar(self) -> None:
        self._servidor.iniciar()

    def detener(self) -> None:
        self._servidor.detener()
        self._enlaces.cerrar_todo()

    def solicitar(self, payload: dict) -> dict | None:
        sobre = mensajes.crear_sobre(self._gateway, self._destino, payload)
        solicitud = uuid.uuid4().hex
        sobre["request_id"] = solicitud
        if not self._enlaces.enviar(self._gateway, mensajes.serializar_datos(sobre)):
            print(">> No se pudo contactar la puerta de enlace.")
            return None
        limite = time.monotonic() + TIMEOUT_RESPUESTA
        while (restante := limite - time.monotonic()) > 0:
            try:
                respuesta = self._respuestas.get(timeout=restante)
            except Empty:
                break
            if respuesta.get("request_id") == solicitud:
                return respuesta["payload"]
        print(">> El banco no respondió a tiempo.")
        return None

    def _recibir(self, linea: str, _ip_origen: str) -> None:
        try:
            sobre, correcciones = mensajes.deserializar_datos(linea)
            mensajes.validar_sobre(sobre)
        except ValueError:
            return
        if sobre["to"] != self._gateway or sobre["from"] != self._destino:
            return
        if correcciones:
            print(f">> Se corrigieron {correcciones} error(es) de transmisión.")
        self._respuestas.put(sobre)


def _mostrar(respuesta: dict | None) -> bool:
    if respuesta is None:
        return False
    if respuesta.get("op") == "error":
        print(f">> Error: {respuesta.get('msg', 'operación rechazada')}")
        return False
    print(f">> {respuesta.get('msg', 'Operación exitosa')}")
    if respuesta.get("op") == "withdraw":
        print(f">> Retiro: ${respuesta['amount']:.2f} · Saldo: ${respuesta['balance']:.2f}")
    return bool(respuesta.get("ok"))


def _ejecutar(cajero: Cajero) -> None:
    usuario = input("Usuario: ").strip()
    pin = input("PIN: ").strip()
    if not _mostrar(cajero.solicitar(mensajes.payload_auth(usuario, pin))):
        return

    while True:
        print("\n1) Retirar dinero\n2) Salir")
        opcion = input("Opción: ").strip()
        if opcion == "1":
            try:
                monto = float(input("Monto a retirar: ").strip())
            except ValueError:
                print(">> Monto inválido.")
                continue
            _mostrar(cajero.solicitar(mensajes.payload_withdraw(monto)))
        elif opcion == "2":
            _mostrar(cajero.solicitar(mensajes.payload_logout()))
            return
        else:
            print(">> Opción inválida.")


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description="Cajero automático del laboratorio")
    analizador.add_argument("--gateway", default="A", help="router conectado al ATM")
    analizador.add_argument("--destino", default="E", help="router conectado al banco")
    analizador.add_argument("--topologia", default=str(configuracion.RUTA_TOPOLOGIA))
    analizador.add_argument("--nombres", default=str(configuracion.RUTA_NOMBRES))
    analizador.add_argument(
        "--host-puerto",
        type=int,
        help="puerto del cajero, si no viene declarado en nombres.json",
    )
    analizador.add_argument("--host-ip", help="ip del cajero (por defecto, la del gateway)")
    argumentos = analizador.parse_args(argv)
    bitacora.configurar("ATM")

    try:
        config = configuracion.cargar(
            argumentos.gateway, argumentos.topologia, argumentos.nombres
        )
        if argumentos.host_puerto:
            config = configuracion.con_host(
                config, "atm", argumentos.host_puerto, argumentos.host_ip
            )
        cajero = Cajero(config, argumentos.destino)
        cajero.iniciar()
    except (configuracion.ErrorConfiguracion, OSError) as error:
        print(f"No se pudo iniciar el ATM: {error}", file=sys.stderr)
        return 1
    try:
        _ejecutar(cajero)
    except (EOFError, KeyboardInterrupt):
        print()
    finally:
        cajero.detener()
    return 0


if __name__ == "__main__":
    sys.exit(main())
