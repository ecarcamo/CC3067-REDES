"""Proceso de un router de la topologia.

Levanta el nodo completo y deja corriendo en paralelo los dos planos que pide el
enunciado: el de routing, que descubre vecinos e inunda los LSA hasta armar el
grafo, y el de forwarding, que atiende el puerto y reenvia los mensajes de
datos. Ambos comparten el socket de escucha y se comunican a traves de la tabla
de enrutamiento.

Uso:

    python3 nodo.py --id A
    python3 nodo.py --id B --topologia config/topologia.json --nombres config/nombres.json
"""

import argparse
import sys
import threading

import bitacora
import configuracion
from configuracion import Configuracion, Direccion, ErrorConfiguracion
from control import dijkstra, tabla
from control.plano import PlanoControl
from datos.reenvio import CLAVE_HOST_LOCAL, PlanoDatos
from protocolo import mensajes
from transporte.enlaces import Enlaces
from transporte.servidor import Servidor


class Nodo:
    """Arma las piezas del router y las mantiene vivas."""

    def __init__(self, config: Configuracion):
        self._config = config
        self._log = bitacora.obtener("nodo")

        self._enlaces = Enlaces(config.direcciones)
        if config.host is not None:
            # El host local (ATM o banco) no es un router y no participa del
            # plano de control, pero se le entrega igual que a un vecino.
            self._enlaces.registrar(
                CLAVE_HOST_LOCAL, Direccion(config.host.ip, config.host.puerto)
            )

        self._datos = PlanoDatos(config, self._enlaces)
        self._control = PlanoControl(config, self._enlaces, al_cambiar_grafo=self._recalcular_tabla)
        self._servidor = Servidor(config.direccion_propia, self._despachar)

    def iniciar(self) -> None:
        self._servidor.iniciar()
        self._control.iniciar()
        if self._config.host is not None:
            self._log.info(
                "host local %s en %s:%s",
                self._config.host.tipo,
                self._config.host.ip,
                self._config.host.puerto,
            )

    def detener(self) -> None:
        self._control.detener()
        self._servidor.detener()
        self._enlaces.cerrar_todo()
        self._log.info("nodo detenido")

    def _despachar(self, linea: str, ip_origen: str) -> None:
        """Separa los dos planos segun el contenido de la linea recibida."""
        clase = mensajes.clasificar(linea)
        if clase == mensajes.CONTROL:
            self._control.manejar(mensajes.deserializar_control(linea), ip_origen)
        elif clase == mensajes.DATOS:
            self._datos.manejar_trama(linea, ip_origen)
        else:
            self._log.warning("linea no reconocida desde %s, se descarta", ip_origen)

    def _recalcular_tabla(self, grafo: dict[str, dict[str, int]]) -> None:
        """Corre el calculo de rutas y deja la tabla lista para el plano de datos."""
        self._log.info("grafo conocido: %s", _resumir(grafo))
        rutas = dijkstra.calcular(grafo, self._config.identificador)
        archivo = tabla.escribir(
            self._config.identificador, rutas, self._config.direcciones
        )
        self._log.info("tabla escrita en %s con %s destinos", archivo, len(rutas))


def _resumir(grafo: dict[str, dict[str, int]]) -> str:
    """Grafo en una linea, para poder seguir la convergencia en la bitacora."""
    if not grafo:
        return "vacio"
    enlaces = {
        f"{min(nodo, vecino)}-{max(nodo, vecino)}={costo}"
        for nodo, adyacentes in grafo.items()
        for vecino, costo in adyacentes.items()
    }
    return f"{len(grafo)} nodos, {len(enlaces)} enlaces [{' '.join(sorted(enlaces))}]"


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description="Router con protocolo Link State")
    analizador.add_argument("--id", required=True, help="identificador del nodo, por ejemplo A")
    analizador.add_argument("--topologia", default=str(configuracion.RUTA_TOPOLOGIA))
    analizador.add_argument("--nombres", default=str(configuracion.RUTA_NOMBRES))
    analizador.add_argument(
        "--detallado", action="store_true", help="bitacora con el detalle de cada mensaje"
    )
    argumentos = analizador.parse_args(argv)

    bitacora.configurar(argumentos.id, argumentos.detallado)
    log = bitacora.obtener("nodo")

    try:
        config = configuracion.cargar(argumentos.id, argumentos.topologia, argumentos.nombres)
    except ErrorConfiguracion as error:
        print(f"Error de configuracion: {error}", file=sys.stderr)
        return 1

    nodo = Nodo(config)
    try:
        nodo.iniciar()
    except OSError as error:
        print(f"No se pudo levantar el nodo: {error}", file=sys.stderr)
        return 1

    log.info("nodo %s en linea, Ctrl+C para detener", config.identificador)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        log.info("interrupcion recibida")
    finally:
        nodo.detener()
    return 0


if __name__ == "__main__":
    sys.exit(main())
