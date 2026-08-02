"""Lee pruebas/resultados/resultados.csv y genera las graficas del analisis."""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt

RUTA_CSV = Path(__file__).resolve().parent / "resultados" / "resultados.csv"
RUTA_GRAFICAS = Path(__file__).resolve().parent / "graficas"

ALGORITMOS = ["hamming", "crc32"]
COLOR_ALGORITMO = {"hamming": "#1f77b4", "crc32": "#d62728"}
COLOR_ESTADO = {"sin_error": "#2ca02c", "corregido": "#ff7f0e", "error_no_corregible": "#d62728"}


def cargar_filas() -> list[dict]:
    with open(RUTA_CSV, encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def graficar_tasa_exito_vs_probabilidad(filas: list[dict]) -> None:
    """Grafica 1: tasa de exito (mensaje recuperado identico) vs probabilidad de error."""
    conteos = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for fila in filas:
        probabilidad = float(fila["probabilidad"])
        contador = conteos[fila["algoritmo"]][probabilidad]
        contador[1] += 1
        if fila["mensaje_correcto"] == "True":
            contador[0] += 1

    plt.figure(figsize=(8, 5))
    for algoritmo in ALGORITMOS:
        probabilidades = sorted(conteos[algoritmo])
        tasas = [conteos[algoritmo][p][0] / conteos[algoritmo][p][1] for p in probabilidades]
        plt.plot(probabilidades, tasas, marker="o", label=algoritmo, color=COLOR_ALGORITMO[algoritmo])

    plt.xlabel("Probabilidad de error por bit")
    plt.ylabel("Tasa de exito")
    plt.title("Tasa de exito vs. probabilidad de error")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(RUTA_GRAFICAS / "tasa_exito_vs_probabilidad.png", dpi=150)
    plt.close()


def graficar_overhead_vs_longitud(filas: list[dict]) -> None:
    """Grafica 2: overhead % vs longitud del mensaje."""
    overheads = defaultdict(lambda: defaultdict(list))
    for fila in filas:
        longitud = int(fila["longitud_chars"])
        overheads[fila["algoritmo"]][longitud].append(float(fila["overhead_pct"]))

    plt.figure(figsize=(8, 5))
    for algoritmo in ALGORITMOS:
        longitudes = sorted(overheads[algoritmo])
        promedios = [sum(overheads[algoritmo][n]) / len(overheads[algoritmo][n]) for n in longitudes]
        plt.plot(longitudes, promedios, marker="o", label=algoritmo, color=COLOR_ALGORITMO[algoritmo])

    plt.xlabel("Longitud del mensaje (caracteres)")
    plt.ylabel("Overhead (%)")
    plt.title("Overhead vs. longitud del mensaje")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(RUTA_GRAFICAS / "overhead_vs_longitud.png", dpi=150)
    plt.close()


def graficar_distribucion_estados(filas: list[dict]) -> None:
    """Grafica 3: distribucion de estados por probabilidad, barras apiladas (una figura por algoritmo)."""
    estados = ["sin_error", "corregido", "error_no_corregible"]

    for algoritmo in ALGORITMOS:
        conteos = defaultdict(lambda: defaultdict(int))
        for fila in filas:
            if fila["algoritmo"] == algoritmo:
                conteos[float(fila["probabilidad"])][fila["estado"]] += 1

        probabilidades = sorted(conteos)
        etiquetas = [str(p) for p in probabilidades]
        base = [0] * len(probabilidades)

        plt.figure(figsize=(8, 5))
        for estado in estados:
            valores = [conteos[p][estado] for p in probabilidades]
            plt.bar(etiquetas, valores, bottom=base, label=estado, color=COLOR_ESTADO[estado])
            base = [b + v for b, v in zip(base, valores)]

        plt.xlabel("Probabilidad de error por bit")
        plt.ylabel("Cantidad de simulaciones")
        plt.title(f"Distribucion de estados por probabilidad ({algoritmo})")
        plt.legend()
        plt.tight_layout()
        plt.savefig(RUTA_GRAFICAS / f"distribucion_estados_{algoritmo}.png", dpi=150)
        plt.close()


def graficar_falsos_negativos(filas: list[dict]) -> None:
    """Grafica 4: casos donde el algoritmo dijo sin_error pero el mensaje llego corrupto."""
    conteos = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for fila in filas:
        if fila["estado"] != "sin_error":
            continue
        probabilidad = float(fila["probabilidad"])
        contador = conteos[fila["algoritmo"]][probabilidad]
        contador[1] += 1
        if fila["mensaje_correcto"] == "False":
            contador[0] += 1

    plt.figure(figsize=(8, 5))
    for algoritmo in ALGORITMOS:
        probabilidades = sorted(conteos[algoritmo])
        tasas = [
            (conteos[algoritmo][p][0] / conteos[algoritmo][p][1]) if conteos[algoritmo][p][1] else 0
            for p in probabilidades
        ]
        plt.plot(probabilidades, tasas, marker="o", label=algoritmo, color=COLOR_ALGORITMO[algoritmo])

    plt.xlabel("Probabilidad de error por bit")
    plt.ylabel("Tasa de falsos negativos (dijo sin_error, llego corrupto)")
    plt.title("Falsos negativos vs. probabilidad de error")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(RUTA_GRAFICAS / "falsos_negativos_vs_probabilidad.png", dpi=150)
    plt.close()


def main() -> None:
    RUTA_GRAFICAS.mkdir(parents=True, exist_ok=True)
    filas = cargar_filas()

    graficar_tasa_exito_vs_probabilidad(filas)
    graficar_overhead_vs_longitud(filas)
    graficar_distribucion_estados(filas)
    graficar_falsos_negativos(filas)

    print(f"[GRAFICAS] imagenes generadas en {RUTA_GRAFICAS}")


if __name__ == "__main__":
    main()
