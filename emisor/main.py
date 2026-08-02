"""Cajero automatico (emisor). Orquesta: aplicacion -> presentacion -> enlace -> ruido -> transmision."""

import socket

from capas import aplicacion, enlace, presentacion, ruido, transmision
from algoritmos.contrato import ResultadoVerificacion

HOST = "127.0.0.1"
PORT = 2705


def enviar(sock: socket.socket, texto: str, algoritmo: str, probabilidad: float) -> None:
    bits = presentacion.codificar_mensaje(texto)
    trama_codificada = enlace.calcular_integridad(bits, algoritmo)
    trama_con_ruido, _ = ruido.aplicar_ruido(trama_codificada.bits, probabilidad)
    transmision.enviar_informacion(sock, trama_con_ruido, algoritmo, trama_codificada.parametros)


def recibir(lector: transmision.LectorLineas) -> tuple[str | None, ResultadoVerificacion]:
    sobre = transmision.recibir_informacion(lector)
    if sobre is None:
        raise ConnectionError("El banco cerro la conexion")

    resultado = enlace.verificar_integridad(sobre["trama"], sobre["algoritmo"], sobre["parametros"])
    texto = presentacion.decodificar_mensaje(resultado.bits) if resultado.bits is not None else None
    return texto, resultado


def login(sock: socket.socket, lector: transmision.LectorLineas, algoritmo: str, probabilidad: float) -> bool:
    """Pide tarjeta y PIN, reintenta hasta autenticar."""
    while True:
        enviar(sock, aplicacion.solicitar_login(), algoritmo, probabilidad)
        texto, resultado = recibir(lector)
        aplicacion.mostrar_mensaje(texto, resultado)

        if texto is not None and aplicacion.es_login_exitoso(texto):
            return True
        print("   Intenta de nuevo.\n")


def menu(sock: socket.socket, lector: transmision.LectorLineas, algoritmo: str, probabilidad: float) -> None:
    """Muestra el menu y maneja las opciones del usuario."""
    while True:
        opcion = aplicacion.solicitar_opcion_menu()

        if opcion == "1":
            enviar(sock, aplicacion.solicitar_retiro(), algoritmo, probabilidad)
        elif opcion == "2":
            enviar(sock, aplicacion.mensaje_logout(), algoritmo, probabilidad)
            texto, resultado = recibir(lector)
            aplicacion.mostrar_mensaje(texto, resultado)
            break
        else:
            print(">> Opcion invalida.")
            continue

        texto, resultado = recibir(lector)
        aplicacion.mostrar_mensaje(texto, resultado)


def main() -> None:
    algoritmo, probabilidad = aplicacion.solicitar_configuracion()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print(f"[EMISOR] Conectado a {HOST}:{PORT}")
        lector = transmision.LectorLineas(sock)

        if login(sock, lector, algoritmo, probabilidad):
            menu(sock, lector, algoritmo, probabilidad)


if __name__ == "__main__":
    main()
