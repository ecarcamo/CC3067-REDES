"""Capa de enlace: calcula y verifica la integridad delegando en el algoritmo del registro."""

from algoritmos.contrato import ResultadoVerificacion, TramaCodificada
from algoritmos.registro import obtener_algoritmo


def calcular_integridad(bits: str, nombre_algoritmo: str) -> TramaCodificada:
    """Delega en el algoritmo del registro y devuelve la trama con redundancia."""
    return obtener_algoritmo(nombre_algoritmo).calcular(bits)


def verificar_integridad(trama: str, nombre_algoritmo: str, parametros: dict) -> ResultadoVerificacion:
    """Verifica (y corrige si el algoritmo puede) la trama recibida."""
    return obtener_algoritmo(nombre_algoritmo).verificar(trama, parametros)
