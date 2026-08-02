"""Capa de ruido: simula el medio fisico volteando bits al azar. Solo existe del lado del emisor."""

import random


def aplicar_ruido(trama: str, probabilidad: float, semilla: int | None = None) -> tuple[str, list[int]]:
    """Voltea cada bit de la trama con la `probabilidad` dada. Devuelve la trama y las posiciones alteradas."""
    generador = random.Random(semilla)
    bits = list(trama)
    posiciones_alteradas = []

    for posicion, bit in enumerate(bits):
        if generador.random() < probabilidad:
            bits[posicion] = "1" if bit == "0" else "0"
            posiciones_alteradas.append(posicion)

    return "".join(bits), posiciones_alteradas
