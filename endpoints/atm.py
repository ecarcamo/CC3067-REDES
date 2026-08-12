"""Cajero automatico: el nodo cliente de la red.

PENDIENTE — FASE 2 (Felipe).

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

Falta acordar con las otras dos parejas el payload de las respuestas del banco:
la definicion grupal solo fija los de ida (auth, withdraw, error y logout).
"""


def main() -> int:
    raise NotImplementedError("Fase 2: implementar el cajero automatico")
