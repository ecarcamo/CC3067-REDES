"""Plano de control: HELLO, construccion del LSA propio y flooding.

Es el hilo de routing del nodo. Corre en paralelo al de forwarding y su unico
producto es el grafo de la red; a partir de ahi el plano de datos recibe la
tabla ya calculada y no vuelve a saber de LSA ni de secuencias.

Reparte el trabajo en tres temporizadores independientes:

* los HELLO, que salen cada cinco segundos hacia todos los vecinos configurados,
* la vigilancia, que da por caido al vecino que lleva quince segundos callado y
  emite el LSA propio cuando la vecindad cambia o toca refrescarlo,
* el recalculo, que avisa al plano de datos cuando el grafo se movio.
"""

import threading
import time
from typing import Callable

import bitacora
from configuracion import Configuracion
from control.lsdb import BaseEstadoEnlaces
from control.secuencia import Secuencia
from control.vecinos import GestorVecinos
from protocolo import mensajes
from protocolo.constantes import (
    ESPERA_PRIMER_LSA,
    INTERVALO_HELLO,
    INTERVALO_REFRESCO_LSA,
    INTERVALO_REVISION,
    TIPO_HELLO,
    TIPO_LSA,
    TTL_LSA,
)
from transporte.enlaces import Enlaces

_log = bitacora.obtener("control")

# Se llama con el grafo completo cada vez que la topologia conocida cambia.
AlCambiarGrafo = Callable[[dict[str, dict[str, int]]], None]


class PlanoControl:
    def __init__(
        self,
        configuracion: Configuracion,
        enlaces: Enlaces,
        al_cambiar_grafo: AlCambiarGrafo | None = None,
    ):
        self._configuracion = configuracion
        self._identificador = configuracion.identificador
        self._enlaces = enlaces
        self._al_cambiar_grafo = al_cambiar_grafo

        self.vecinos = GestorVecinos(configuracion.vecinos)
        self.lsdb = BaseEstadoEnlaces()
        self.secuencia = Secuencia(self._identificador)

        self._detener = threading.Event()
        self._arrancado = threading.Event()
        self._vecindad_cambio = threading.Event()
        self._ultimo_lsa = 0.0
        self._hilos: list[threading.Thread] = []

    # --- Ciclo de vida ------------------------------------------------------

    def iniciar(self) -> None:
        for objetivo, nombre in (
            (self._ciclo_hellos, "hellos"),
            (self._ciclo_vigilancia, "vigilancia"),
            (self._ciclo_rutas, "rutas"),
        ):
            hilo = threading.Thread(target=objetivo, name=nombre, daemon=True)
            hilo.start()
            self._hilos.append(hilo)
        _log.info(
            "plano de control activo, vecinos configurados: %s",
            ", ".join(self.vecinos.configurados),
        )

    def detener(self) -> None:
        self._detener.set()

    # --- Entrada de mensajes ------------------------------------------------

    def manejar(self, mensaje: dict, ip_origen: str) -> None:
        """Punto de entrada de todo el plano de control."""
        tipo = mensaje.get("type")
        if tipo == TIPO_HELLO:
            self._manejar_hello(mensaje)
        elif tipo == TIPO_LSA:
            self._manejar_lsa(mensaje)
        else:
            # Un tipo que no conocemos se ignora: puede ser una extension de
            # otro grupo y no es motivo para descartar nada mas.
            _log.debug("mensaje de control ignorado, tipo %r desde %s", tipo, ip_origen)

    def _manejar_hello(self, mensaje: dict) -> None:
        mensajes.validar_hello(mensaje)
        vecino = mensaje["from"]
        if not self.vecinos.registrar_hello(vecino):
            return

        # Vecino nuevo o recuperado: se le manda de una todo lo que sabemos para
        # que no tenga que esperar al proximo refresco para armar su grafo.
        self._sincronizar_con(vecino)
        self._vecindad_cambio.set()

    def _manejar_lsa(self, mensaje: dict) -> None:
        mensajes.validar_lsa(mensaje)
        origen = mensaje["origin"]
        seq = mensaje["seq"]

        if origen == self._identificador:
            # Es un eco de un anuncio nuestro. Solo importa si la red recuerda
            # una version mas nueva que la que tenemos, cosa que pasa cuando el
            # nodo reinicio y perdio el contador.
            if seq > self.secuencia.actual:
                _log.warning("la red conoce un LSA propio mas nuevo (seq %s), se supera", seq)
                self.secuencia.alcanzar(seq)
                self._emitir_lsa("secuencia recuperada de la red")
            return

        if not self.lsdb.registrar(origen, seq, mensaje["links"]):
            # Repetido o viejo: aqui muere el ciclo.
            return

        self._reenviar_lsa(mensaje)

    # --- Flooding -----------------------------------------------------------

    def _reenviar_lsa(self, mensaje: dict) -> None:
        """Reenvia a todos los vecinos vivos menos al que nos lo mando."""
        ttl = int(mensaje.get("ttl", TTL_LSA)) - 1
        if ttl <= 0:
            _log.debug("LSA de %s descartado por ttl agotado", mensaje.get("origin"))
            return

        remitente = mensaje.get("from")
        copia = dict(mensaje)
        copia["ttl"] = ttl
        copia["from"] = self._identificador

        destinos = [vecino for vecino in self.vecinos.vivos() if vecino != remitente]
        if destinos:
            self._enlaces.difundir(destinos, mensajes.serializar_control(copia))

    def _emitir_lsa(self, motivo: str) -> None:
        """Construye el LSA propio con los vecinos vivos y lo inunda."""
        enlaces_activos = self.vecinos.enlaces_activos()
        seq = self.secuencia.siguiente()
        lsa = mensajes.crear_lsa(self._identificador, seq, enlaces_activos)

        self.lsdb.registrar(self._identificador, seq, enlaces_activos)
        self._ultimo_lsa = time.monotonic()

        destinos = self.vecinos.vivos()
        _log.info("LSA propio seq %s (%s): %s", seq, motivo, enlaces_activos or "sin vecinos")
        if destinos:
            self._enlaces.difundir(destinos, mensajes.serializar_control(lsa))

    def _sincronizar_con(self, vecino: str) -> None:
        """Le manda a un vecino recien levantado todos los anuncios que tenemos."""
        for anuncio in self.lsdb.anuncios():
            lsa = mensajes.crear_lsa(anuncio.origen, anuncio.seq, anuncio.enlaces)
            lsa["from"] = self._identificador
            self._enlaces.enviar(vecino, mensajes.serializar_control(lsa))

    # --- Temporizadores -----------------------------------------------------

    def _ciclo_hellos(self) -> None:
        """El HELLO va a todos los vecinos configurados, vivos o no: asi se descubren."""
        hello = mensajes.serializar_control(mensajes.crear_hello(self._identificador))
        while not self._detener.is_set():
            self._enlaces.difundir(self.vecinos.configurados, hello)
            self._detener.wait(INTERVALO_HELLO)

    def _ciclo_vigilancia(self) -> None:
        # El primer anuncio espera una ronda de HELLO para no salir vacio.
        self._detener.wait(ESPERA_PRIMER_LSA)
        if self._detener.is_set():
            return
        self._arrancado.set()
        self._vecindad_cambio.clear()
        self._emitir_lsa("anuncio inicial")

        while not self._detener.is_set():
            self._detener.wait(INTERVALO_REVISION)
            if self._detener.is_set():
                return

            caidos = self.vecinos.vencidos()
            if caidos:
                # La definicion grupal lo pide explicito: al dar por caido a un
                # vecino se emite un LSA propio con el seq aumentado y sin ese enlace.
                self._emitir_lsa(f"caida de {', '.join(caidos)}")
                self._vecindad_cambio.clear()
            elif self._vecindad_cambio.is_set():
                self._vecindad_cambio.clear()
                self._emitir_lsa("vecino nuevo")
            elif time.monotonic() - self._ultimo_lsa >= INTERVALO_REFRESCO_LSA:
                self._emitir_lsa("refresco periodico")

    def _ciclo_rutas(self) -> None:
        """Avisa al plano de datos cuando el grafo cambio, sin recalcular de mas."""
        ultima_version = -1
        while not self._detener.is_set():
            version = self.lsdb.version
            if version != ultima_version and self._al_cambiar_grafo is not None:
                ultima_version = version
                try:
                    self._al_cambiar_grafo(self.lsdb.grafo())
                except Exception:
                    _log.exception("fallo el recalculo de la tabla de enrutamiento")
            self._detener.wait(INTERVALO_REVISION)
