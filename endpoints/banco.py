"""Servidor bancario: el nodo servidor de la red.

PENDIENTE — FASE 2 (Felipe).

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


def main() -> int:
    raise NotImplementedError("Fase 2: implementar el servidor bancario")
