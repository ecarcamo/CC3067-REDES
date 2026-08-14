"""Servidor bancario: el nodo servidor de la red.

Espejo del ATM. Escucha en su puerto, recibe tramas Hamming desde su puerta de
enlace (en la configuracion que dejamos, el nodo E), decodifica el sobre, y solo
entonces abre el `payload`, que es lo unico que le toca interpretar: ningun
router lo hace.

Debe atender las operaciones de la seccion 5 del protocolo:

* `auth` con usuario y pin,
* `withdraw` con el monto, validando saldo y monto positivo,
* `logout`,
* y responder con `payload_error` cuando la operacion no procede.

La respuesta se manda como un sobre nuevo con `from` y `to` intercambiados
respecto al que llego, y vuelve por la red igual que fue: el banco se lo entrega
a su puerta de enlace y esa lo rutea de vuelta al router del ATM.

Las cuentas de prueba pueden ser las mismas del laboratorio 2, hardcodeadas en
memoria; el laboratorio no pide persistencia.
"""

import argparse
import sys
import threading

import bitacora
import configuracion
from protocolo import mensajes
from transporte.enlaces import Enlaces
from transporte.servidor import Servidor

CUENTAS = {
    "4111111111111111": {"pin": "1234", "balance": 500.0},
    "5500005555555559": {"pin": "0000", "balance": 1200.5},
    "23016": {"pin": "123456789", "balance": 400.0},
}


class LogicaBanco:
    """Cuentas y sesión en memoria; no contiene detalles de transporte."""

    def __init__(self, cuentas: dict | None = None):
        origen = cuentas if cuentas is not None else CUENTAS
        self._cuentas = {usuario: dict(cuenta) for usuario, cuenta in origen.items()}
        self._usuario: str | None = None
        self._candado = threading.Lock()

    def procesar(self, payload: dict) -> dict:
        with self._candado:
            operacion = payload.get("op")
            if operacion == "auth":
                self._usuario = None
                usuario = payload.get("user")
                cuenta = self._cuentas.get(usuario)
                if cuenta is None or cuenta["pin"] != payload.get("pin"):
                    return mensajes.payload_error("AUTH", "Usuario o PIN inválido")
                self._usuario = usuario
                return {"op": "auth", "ok": True, "msg": "Autenticación exitosa"}

            if operacion == "withdraw":
                if self._usuario is None:
                    return mensajes.payload_error("SESSION", "No autenticado")
                monto = payload.get("amount")
                if isinstance(monto, bool) or not isinstance(monto, (int, float)) or monto <= 0:
                    return mensajes.payload_error("AMOUNT", "Monto inválido")
                cuenta = self._cuentas[self._usuario]
                if monto > cuenta["balance"]:
                    return mensajes.payload_error("FUNDS", "Fondos insuficientes")
                cuenta["balance"] -= monto
                return {
                    "op": "withdraw",
                    "ok": True,
                    "amount": monto,
                    "balance": cuenta["balance"],
                    "msg": "Retiro aprobado",
                }

            if operacion == "logout":
                self._usuario = None
                return {"op": "logout", "ok": True, "msg": "Sesión cerrada"}

            return mensajes.payload_error("OP", "Operación desconocida")


class Banco:
    """Host servidor que responde sobres mediante su puerta de enlace."""

    def __init__(self, config: configuracion.Configuracion):
        if config.host is None or config.host.tipo != "banco":
            raise configuracion.ErrorConfiguracion(
                f"el nodo {config.identificador} no tiene un banco configurado"
            )
        self._gateway = config.identificador
        self._logica = LogicaBanco()
        self._enlaces = Enlaces({self._gateway: config.direccion_propia})
        self._servidor = Servidor(
            configuracion.Direccion(config.host.ip, config.host.puerto), self._recibir
        )

    def iniciar(self) -> None:
        self._servidor.iniciar()

    def detener(self) -> None:
        self._servidor.detener()
        self._enlaces.cerrar_todo()

    def _recibir(self, linea: str, _ip_origen: str) -> None:
        try:
            sobre, _ = mensajes.deserializar_datos(linea)
            mensajes.validar_sobre(sobre)
        except ValueError:
            return
        if sobre["to"] != self._gateway:
            return

        respuesta = mensajes.crear_sobre(
            sobre["to"], sobre["from"], self._logica.procesar(sobre["payload"])
        )
        if "request_id" in sobre:
            respuesta["request_id"] = sobre["request_id"]
        self._enlaces.enviar(self._gateway, mensajes.serializar_datos(respuesta))


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description="Servidor bancario del laboratorio")
    analizador.add_argument("--gateway", default="E", help="router conectado al banco")
    analizador.add_argument("--topologia", default=str(configuracion.RUTA_TOPOLOGIA))
    analizador.add_argument("--nombres", default=str(configuracion.RUTA_NOMBRES))
    analizador.add_argument(
        "--host-puerto",
        type=int,
        help="puerto del banco, si no viene declarado en nombres.json",
    )
    analizador.add_argument("--host-ip", help="ip del banco (por defecto, la del gateway)")
    argumentos = analizador.parse_args(argv)
    bitacora.configurar("BANCO")

    try:
        config = configuracion.cargar(
            argumentos.gateway, argumentos.topologia, argumentos.nombres
        )
        if argumentos.host_puerto:
            config = configuracion.con_host(
                config, "banco", argumentos.host_puerto, argumentos.host_ip
            )
        banco = Banco(config)
        banco.iniciar()
    except (configuracion.ErrorConfiguracion, OSError) as error:
        print(f"No se pudo iniciar el banco: {error}", file=sys.stderr)
        return 1
    print("Banco en línea. Ctrl+C para detener.")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        banco.detener()
    return 0


if __name__ == "__main__":
    sys.exit(main())
