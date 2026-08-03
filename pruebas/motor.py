"""Simulador sin sockets: corre codificar -> calcular_integridad -> aplicar_ruido -> verificar_integridad
miles de veces, variando algoritmo, longitud del mensaje y probabilidad de error."""

import csv
import random
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "emisor"))

from capas import enlace, presentacion, ruido  # noqa: E402

LONGITUDES_CHARS = [4, 8, 16, 32, 64, 128]
PROBABILIDADES = [0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1]
CONFIGURACIONES = [
    ("hamming", {"m": m}, f"m={m}") for m in (4, 8, 16)
] + [
    ("fletcher", {"tamano_bloque": t}, f"bloque={t}") for t in (8, 16, 32)
] + [("crc32", {}, "IEEE")]
REPETICIONES = 200
SEMILLA_BASE = 12345

RUTA_SALIDA = Path(__file__).resolve().parent / "resultados" / "resultados.csv"

COLUMNAS = [
    "algoritmo",
    "configuracion",
    "longitud_chars",
    "probabilidad",
    "repeticion",
    "bits_datos",
    "bits_totales",
    "overhead_pct",
    "bits_alterados",
    "estado",
    "mensaje_correcto",
]

ALFABETO = string.ascii_letters + string.digits + " "


def generar_texto(longitud: int, semilla: int) -> str:
    """Genera texto ASCII imprimible de la longitud dada, reproducible por semilla."""
    generador = random.Random(semilla)
    return "".join(generador.choice(ALFABETO) for _ in range(longitud))


def correr_una_simulacion(texto: str, algoritmo: str, probabilidad: float, semilla: int, configuracion=None) -> dict:
    """Ejecuta un ciclo completo (sin sockets) y devuelve una fila de resultados."""
    bits = presentacion.codificar_mensaje(texto)
    trama_codificada = enlace.calcular_integridad(bits, algoritmo, configuracion)
    trama_con_ruido, posiciones_alteradas = ruido.aplicar_ruido(
        trama_codificada.bits, probabilidad, semilla=semilla
    )
    resultado = enlace.verificar_integridad(trama_con_ruido, algoritmo, trama_codificada.parametros)

    bits_totales = len(trama_codificada.bits)
    overhead_pct = (bits_totales - len(bits)) / len(bits) * 100

    return {
        "algoritmo": algoritmo,
        "longitud_chars": len(texto),
        "probabilidad": probabilidad,
        "bits_datos": len(bits),
        "bits_totales": bits_totales,
        "overhead_pct": round(overhead_pct, 2),
        "bits_alterados": len(posiciones_alteradas),
        "estado": resultado.estado.value,
        "mensaje_correcto": resultado.bits == bits,
    }


def correr_barrido() -> list[dict]:
    """Recorre todas las combinaciones de algoritmo x longitud x probabilidad x repeticion."""
    filas = []
    for algoritmo, parametros, etiqueta in CONFIGURACIONES:
        for longitud in LONGITUDES_CHARS:
            for probabilidad in PROBABILIDADES:
                for repeticion in range(REPETICIONES):
                    semilla = SEMILLA_BASE + repeticion
                    texto = generar_texto(longitud, semilla)

                    fila = correr_una_simulacion(texto, algoritmo, probabilidad, semilla, parametros)
                    fila["configuracion"] = etiqueta
                    fila["repeticion"] = repeticion
                    filas.append(fila)
    return filas


def guardar_csv(filas: list[dict]) -> None:
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(RUTA_SALIDA, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)


def main() -> None:
    filas = correr_barrido()
    guardar_csv(filas)
    print(f"[MOTOR] {len(filas)} simulaciones -> {RUTA_SALIDA}")


if __name__ == "__main__":
    main()
