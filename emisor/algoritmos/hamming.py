"""Algoritmo de corrección Hamming generico (n, m). Implementacion pendiente (Hito 1)."""

from algoritmos.contrato import ResultadoVerificacion, TramaCodificada


class Hamming:
    nombre = "hamming"

    def calcular(self, bits: str) -> TramaCodificada:
        raise NotImplementedError

    def verificar(self, trama: str, parametros: dict) -> ResultadoVerificacion:
        raise NotImplementedError
