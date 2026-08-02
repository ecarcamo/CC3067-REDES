"""Algoritmo de deteccion CRC-32 (IEEE 802.3). Implementacion pendiente (Hito 1)."""

from algoritmos.contrato import ResultadoVerificacion, TramaCodificada


class Crc32:
    nombre = "crc32"

    def calcular(self, bits: str) -> TramaCodificada:
        raise NotImplementedError

    def verificar(self, trama: str, parametros: dict) -> ResultadoVerificacion:
        raise NotImplementedError
