"""Capa de presentacion: texto <-> bits ASCII."""

BITS_POR_CARACTER = 8
LIMITE_ASCII = 128


def codificar_mensaje(texto: str) -> str:
    """Convierte texto a una cadena de bits ASCII (8 bits por caracter)."""
    for caracter in texto:
        if ord(caracter) >= LIMITE_ASCII:
            raise ValueError(f"caracter no ASCII: {caracter!r}")
    return "".join(format(ord(c), f"0{BITS_POR_CARACTER}b") for c in texto)


def decodificar_mensaje(bits: str) -> str:
    """Convierte una cadena de bits ASCII de vuelta a texto."""
    if len(bits) % BITS_POR_CARACTER != 0:
        raise ValueError("la longitud de bits debe ser multiplo de 8")
    caracteres = (bits[i : i + BITS_POR_CARACTER] for i in range(0, len(bits), BITS_POR_CARACTER))
    return "".join(chr(int(byte, 2)) for byte in caracteres)
