"""Plano de datos: reenvio de los mensajes entre el ATM y el servidor bancario.

PENDIENTE — FASE 2 (Felipe).

El enunciado describe el ciclo completo de un mensaje que atraviesa un router, y
es exactamente lo que toca implementar en `manejar_trama`:

1. llega una cadena de bits por el socket,
2. se detectan y corrigen errores sobre todos los bits (Hamming 7,4),
3. se extraen los bits de datos,
4. se deserializa y se lee el destino,
5. se consulta la tabla de ruteo,
6. se abre la conexion segun la ip y el puerto que devolvio la tabla,
7. se vuelve a serializar,
8. se aplica Hamming(7,4) a todos los bits,
9. se envian los bits por el socket.

Los pasos 1 a 4 y 7 a 9 ya estan resueltos en `protocolo.mensajes`
(`deserializar_datos` y `serializar_datos`) y el envio en `transporte.enlaces`;
lo que falta es la decision del medio.

Reglas del protocolo que hay que hacer cumplir:

* El router solo lee `to`. El `payload` no se abre nunca: es el mensaje de
  aplicacion entre el ATM y el banco y ningun nodo intermedio lo interpreta.
* Antes de reenviar se agrega el propio nombre a `hops` y se resta uno al `ttl`.
* Si el `ttl` llega a cero, el mensaje se descarta.
* Si el nodo se encuentra a si mismo en `hops`, se descarta por bucle de ruteo.
* Si `to` es este mismo nodo, el mensaje no se reenvia: se entrega al host local
  (el ATM o el servidor bancario colgado de este router, que viene en
  `configuracion.host`). Si `to` es este nodo y no hay host local, se descarta.
"""

import bitacora
from configuracion import Configuracion
from transporte.enlaces import Enlaces

_log = bitacora.obtener("datos")

# Nombre con el que se registra el host local en `transporte.enlaces.Enlaces`,
# para poder entregarle mensajes igual que a un vecino.
CLAVE_HOST_LOCAL = "__host_local__"


class PlanoDatos:
    """Recibe tramas Hamming y decide si entregarlas o reenviarlas."""

    def __init__(self, configuracion: Configuracion, enlaces: Enlaces):
        self._configuracion = configuracion
        self._identificador = configuracion.identificador
        self._enlaces = enlaces

    def manejar_trama(self, linea: str, ip_origen: str) -> None:
        """Punto de entrada del plano de datos: una linea de bits recibida."""
        raise NotImplementedError("Fase 2: implementar el reenvio del plano de datos")

    def enviar(self, sobre: dict) -> bool:
        """Inyecta un sobre nuevo en la red, consultando la tabla como uno recibido.

        La usa el router cuando su host local (el ATM o el banco) le entrega un
        mensaje para que lo curse hacia el otro extremo.
        """
        raise NotImplementedError("Fase 2: implementar la inyeccion de sobres a la red")
