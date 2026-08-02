"""Algoritmo de deteccion CRC-32 (IEEE 802.3, polinomio reflejado 0xEDB88320)."""

from algoritmos.contrato import EstadoVerificacion, ResultadoVerificacion, TramaCodificada

POLINOMIO_REFLEJADO = 0xEDB88320
VALOR_INICIAL = 0xFFFFFFFF
BITS_POR_BYTE = 8
BITS_CHECKSUM = 32


def _bits_a_bytes(bits: str) -> list[int]:
    return [int(bits[i : i + BITS_POR_BYTE], 2) for i in range(0, len(bits), BITS_POR_BYTE)]


def calcular_crc(bits_datos: str) -> int:
    """CRC-32 reflejado (mismo algoritmo que Ethernet FCS / zlib.crc32), bit a bit."""
    crc = VALOR_INICIAL
    for byte in _bits_a_bytes(bits_datos):
        crc ^= byte
        for _ in range(BITS_POR_BYTE):
            if crc & 1:
                crc = (crc >> 1) ^ POLINOMIO_REFLEJADO
            else:
                crc >>= 1
    return crc ^ VALOR_INICIAL


class Crc32:
    nombre = "crc32"

    def calcular(self, bits: str) -> TramaCodificada:
        checksum = calcular_crc(bits)
        trama = bits + format(checksum, f"0{BITS_CHECKSUM}b")
        return TramaCodificada(bits=trama, parametros={"bits_datos": len(bits)})

    def verificar(self, trama: str, parametros: dict) -> ResultadoVerificacion:
        n = parametros["bits_datos"]
        bits_datos = trama[:n]
        checksum_recibido = trama[n:]
        checksum_calculado = format(calcular_crc(bits_datos), f"0{BITS_CHECKSUM}b")

        if checksum_calculado == checksum_recibido:
            return ResultadoVerificacion(
                estado=EstadoVerificacion.SIN_ERROR, bits=bits_datos, detalle="checksum coincide"
            )

        return ResultadoVerificacion(
            estado=EstadoVerificacion.ERROR_NO_CORREGIBLE,
            bits=None,
            detalle="checksum no coincide: la trama llego corrupta",
        )
