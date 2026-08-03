"""Algoritmo de correccion Hamming generico (n, m)."""

from algoritmos.contrato import EstadoVerificacion, ResultadoVerificacion, TramaCodificada


def calcular_bits_paridad(m: int) -> int:
    """Devuelve el r mas chico que cumple m + r + 1 <= 2**r."""
    r = 0
    while m + r + 1 > 2**r:
        r += 1
    return r


def _es_potencia_de_dos(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def codificar_bloque(bits_datos: str) -> str:
    """Inserta bits de paridad par en las posiciones potencia de 2 (1, 2, 4, ...)."""
    m = len(bits_datos)
    r = calcular_bits_paridad(m)
    n = m + r

    bloque = [""] * (n + 1)  # 1-indexado; bloque[0] no se usa
    datos = iter(bits_datos)
    for pos in range(1, n + 1):
        bloque[pos] = "0" if _es_potencia_de_dos(pos) else next(datos)

    for i in range(r):
        pos_paridad = 2**i
        paridad = 0
        for pos in range(1, n + 1):
            if pos != pos_paridad and pos & pos_paridad:
                paridad ^= int(bloque[pos])
        bloque[pos_paridad] = str(paridad)

    return "".join(bloque[1:])


def decodificar_bloque(bloque: str) -> tuple[str, int]:
    """Recalcula el sindrome. Devuelve (bits_datos, posicion_error); 0 = sin error."""
    n = len(bloque)
    r = 0
    while 2**r < n + 1:
        r += 1

    b = [""] + list(bloque)
    sindrome = 0
    for i in range(r):
        pos_paridad = 2**i
        paridad = 0
        for pos in range(1, n + 1):
            if pos & pos_paridad:
                paridad ^= int(b[pos])
        if paridad != 0:
            sindrome += pos_paridad

    if 0 < sindrome <= n:
        b[sindrome] = "1" if b[sindrome] == "0" else "0"

    posiciones_paridad = {2**i for i in range(r)}
    bits_datos = "".join(b[pos] for pos in range(1, n + 1) if pos not in posiciones_paridad)
    return bits_datos, sindrome


class Hamming:
    nombre = "hamming"

    def __init__(self, m: int = 8):
        if m < 1:
            raise ValueError("m debe ser mayor que cero")
        self.m = m

    def calcular(self, bits: str) -> TramaCodificada:
        m = self.m
        bits_datos = len(bits)
        bits = bits + "0" * ((-bits_datos) % m)
        bloques_datos = [bits[i : i + m] for i in range(0, len(bits), m)]
        trama = "".join(codificar_bloque(bloque) for bloque in bloques_datos)
        return TramaCodificada(bits=trama, parametros={"m": m, "bloques": len(bloques_datos), "bits_datos": bits_datos})

    def verificar(self, trama: str, parametros: dict) -> ResultadoVerificacion:
        m = parametros["m"]
        n = m + calcular_bits_paridad(m)
        bloques = [trama[i : i + n] for i in range(0, len(trama), n)]

        bits_datos = []
        correcciones = []
        for indice, bloque in enumerate(bloques):
            datos, posicion_error = decodificar_bloque(bloque)
            bits_datos.append(datos)
            if posicion_error != 0:
                correcciones.append(f"bloque {indice}: bit {posicion_error} corregido")

        if correcciones:
            estado = EstadoVerificacion.CORREGIDO
            detalle = "; ".join(correcciones)
        else:
            estado = EstadoVerificacion.SIN_ERROR
            detalle = "sin errores detectados"

        recuperados = "".join(bits_datos)
        recuperados = recuperados[: parametros.get("bits_datos", len(recuperados))]
        return ResultadoVerificacion(estado=estado, bits=recuperados, detalle=detalle)
