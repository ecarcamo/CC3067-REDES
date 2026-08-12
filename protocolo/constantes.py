"""Constantes fijadas por la definicion grupal del protocolo.

Los tres grupos de la topologia comparten estos valores; cambiarlos rompe la
interoperabilidad, asi que viven en un solo lugar y nadie los redefine.
"""

# --- Identificacion del protocolo -------------------------------------------

PROTO = "LinkState"

TIPO_HELLO = "HELLO"
TIPO_LSA = "LSA"
TIPO_MENSAJE = "message"

# --- Tiempos de vida iniciales ----------------------------------------------

# Un HELLO nunca se reenvia: nace y muere en el enlace.
TTL_HELLO = 1
TTL_LSA = 8
TTL_DATOS = 16

# --- Temporizadores del plano de control (segundos) -------------------------

INTERVALO_HELLO = 5.0
TIMEOUT_VECINO = 15.0

# Espera antes del primer LSA: le da tiempo a la primera ronda de HELLO para
# que el anuncio inicial salga con los vecinos que de verdad estan vivos.
ESPERA_PRIMER_LSA = 6.0

# Reanuncio periodico del LSA propio aunque nada haya cambiado, para que un
# nodo que arranca tarde termine de llenar su grafo sin esperar a un cambio
# de topologia.
INTERVALO_REFRESCO_LSA = 30.0

# Cada cuanto se revisa el vencimiento de los vecinos.
INTERVALO_REVISION = 1.0

# --- Codificacion en el socket ----------------------------------------------

CODIFICACION = "utf-8"
DELIMITADOR = "\n"
