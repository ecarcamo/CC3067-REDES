"""Checksum Fletcher configurable para palabras de 8, 16 o 32 bits."""

from algoritmos.contrato import EstadoVerificacion, ResultadoVerificacion, TramaCodificada


class Fletcher:
    nombre = "fletcher"

    def __init__(self, tamano_bloque: int = 16):
        if tamano_bloque not in (8, 16, 32):
            raise ValueError("tamano_bloque debe ser 8, 16 o 32")
        self.tamano_bloque = tamano_bloque

    @staticmethod
    def _checksum(bits: str, tamano: int) -> int:
        modulo = 2**tamano - 1
        suma1 = suma2 = 0
        for i in range(0, len(bits), tamano):
            suma1 = (suma1 + int(bits[i : i + tamano], 2)) % modulo
            suma2 = (suma2 + suma1) % modulo
        return (suma2 << tamano) | suma1

    def calcular(self, bits: str) -> TramaCodificada:
        relleno = (-len(bits)) % self.tamano_bloque
        datos_rellenos = bits + "0" * relleno
        checksum = self._checksum(datos_rellenos, self.tamano_bloque)
        trama = datos_rellenos + format(checksum, f"0{2 * self.tamano_bloque}b")
        parametros = {"tamano_bloque": self.tamano_bloque, "bits_datos": len(bits)}
        return TramaCodificada(trama, parametros)

    def verificar(self, trama: str, parametros: dict) -> ResultadoVerificacion:
        tamano = parametros["tamano_bloque"]
        bits_datos = parametros["bits_datos"]
        longitud_rellena = bits_datos + (-bits_datos) % tamano
        datos = trama[:longitud_rellena]
        recibido = trama[longitud_rellena:]
        esperado = format(self._checksum(datos, tamano), f"0{2 * tamano}b")
        if recibido == esperado:
            return ResultadoVerificacion(EstadoVerificacion.SIN_ERROR, datos[:bits_datos], "checksum coincide")
        return ResultadoVerificacion(EstadoVerificacion.ERROR_NO_CORREGIBLE, None, "checksum Fletcher no coincide")
