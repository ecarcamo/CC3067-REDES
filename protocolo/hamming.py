"""Hamming(7,4) tal como quedo definido en la seccion 5 del protocolo grupal.

El JSON del sobre de datos se pasa a bytes UTF-8, cada byte se parte en dos
nibbles empezando por el mas significativo, y cada nibble `d1 d2 d3 d4` produce
el bloque `p1 p2 d1 p3 d2 d3 d4` con paridad par. Son catorce bits exactos por
byte, sin relleno y sin metadatos: el receptor sabe reconstruir el mensaje
unicamente a partir de la cadena de bits.
"""

BITS_POR_BLOQUE = 7
BITS_POR_BYTE = 2 * BITS_POR_BLOQUE

# Posiciones (1-indexadas, como en la definicion del protocolo) que cubre cada
# bit de paridad dentro del bloque p1 p2 d1 p3 d2 d3 d4.
_COBERTURA = {1: (3, 5, 7), 2: (3, 6, 7), 4: (5, 6, 7)}


class ErrorHamming(ValueError):
    """La cadena recibida no es una trama Hamming(7,4) valida."""


def codificar_nibble(nibble: int) -> str:
    """Codifica cuatro bits de datos en un bloque de siete bits."""
    if not 0 <= nibble <= 0xF:
        raise ErrorHamming(f"nibble fuera de rango: {nibble}")

    d1 = (nibble >> 3) & 1
    d2 = (nibble >> 2) & 1
    d3 = (nibble >> 1) & 1
    d4 = nibble & 1

    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p3 = d2 ^ d3 ^ d4

    return f"{p1}{p2}{d1}{p3}{d2}{d3}{d4}"


def decodificar_bloque(bloque: str) -> tuple[int, int]:
    """Corrige (si hace falta) un bloque de siete bits.

    Devuelve el nibble de datos y el sindrome: 0 significa que llego intacto y
    cualquier otro valor es la posicion 1-indexada del bit que se corrigio.
    """
    if len(bloque) != BITS_POR_BLOQUE:
        raise ErrorHamming(f"el bloque debe tener {BITS_POR_BLOQUE} bits, trae {len(bloque)}")

    bits = [_a_bit(caracter) for caracter in bloque]

    # El sindrome se arma con la paridad fallida de cada grupo, ponderada por la
    # posicion del bit de paridad correspondiente.
    sindrome = 0
    for posicion_paridad, cubiertas in _COBERTURA.items():
        paridad = bits[posicion_paridad - 1]
        for posicion in cubiertas:
            paridad ^= bits[posicion - 1]
        if paridad:
            sindrome += posicion_paridad

    if sindrome:
        bits[sindrome - 1] ^= 1

    nibble = (bits[2] << 3) | (bits[4] << 2) | (bits[5] << 1) | bits[6]
    return nibble, sindrome


def codificar_bytes(datos: bytes) -> str:
    """Codifica una secuencia de bytes: catorce bits por cada byte."""
    bloques = []
    for byte in datos:
        bloques.append(codificar_nibble(byte >> 4))
        bloques.append(codificar_nibble(byte & 0x0F))
    return "".join(bloques)


def decodificar_bytes(bits: str) -> tuple[bytes, int]:
    """Decodifica una trama completa. Devuelve los bytes y cuantos bits corrigio."""
    if len(bits) % BITS_POR_BYTE != 0:
        raise ErrorHamming(
            f"la trama debe medir un multiplo de {BITS_POR_BYTE} bits, mide {len(bits)}"
        )

    datos = bytearray()
    correcciones = 0
    for inicio in range(0, len(bits), BITS_POR_BYTE):
        alto, sindrome_alto = decodificar_bloque(bits[inicio : inicio + BITS_POR_BLOQUE])
        bajo, sindrome_bajo = decodificar_bloque(
            bits[inicio + BITS_POR_BLOQUE : inicio + BITS_POR_BYTE]
        )
        correcciones += (sindrome_alto != 0) + (sindrome_bajo != 0)
        datos.append((alto << 4) | bajo)

    return bytes(datos), correcciones


def codificar_texto(texto: str) -> str:
    """Atajo para el caso real: un JSON en texto hacia su trama de bits."""
    return codificar_bytes(texto.encode("utf-8"))


def decodificar_texto(bits: str) -> tuple[str, int]:
    """Inverso de `codificar_texto`. Devuelve el texto y los bits corregidos."""
    datos, correcciones = decodificar_bytes(bits)
    try:
        return datos.decode("utf-8"), correcciones
    except UnicodeDecodeError as error:
        # Con mas de un error por bloque, Hamming(7,4) "corrige" hacia un bloque
        # equivocado y lo que sale no es UTF-8 valido.
        raise ErrorHamming("los bytes recuperados no son UTF-8 valido") from error


def es_trama_de_bits(linea: str) -> bool:
    """True si la linea parece una trama Hamming y no un JSON de control."""
    return len(linea) > 0 and all(caracter in "01" for caracter in linea)


def _a_bit(caracter: str) -> int:
    if caracter not in "01":
        raise ErrorHamming(f"caracter invalido en la trama: {caracter!r}")
    return int(caracter)
