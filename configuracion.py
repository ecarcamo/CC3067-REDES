"""Carga de la configuracion inicial del nodo.

Cada nodo arranca conociendo unicamente dos cosas: quienes son sus vecinos con
el costo del enlace (`config/topologia.json`) y en que IP y puerto escucha cada
nodo de la red (`config/nombres.json`). Todo lo demas lo aprende por HELLO y
por LSA.

Los costos no se miden, se leen de la topologia compartida y son simetricos,
tal como quedo acordado en la definicion grupal.
"""

import json
from dataclasses import dataclass, replace
from pathlib import Path

RUTA_TOPOLOGIA = Path("config/topologia.json")
RUTA_NOMBRES = Path("config/nombres.json")


class ErrorConfiguracion(Exception):
    """La configuracion es incoherente y el nodo no puede arrancar con ella."""


@dataclass(frozen=True)
class Direccion:
    """Donde escucha un nodo router."""

    ip: str
    puerto: int

    def como_tupla(self) -> tuple[str, int]:
        return (self.ip, self.puerto)


@dataclass(frozen=True)
class HostLocal:
    """Equipo terminal colgado de este router: el ATM o el servidor bancario.

    No es un router y no participa del plano de control; se conecta por sockets
    a su puerta de enlace predeterminada, que es este nodo.
    """

    tipo: str
    ip: str
    puerto: int

    def como_tupla(self) -> tuple[str, int]:
        return (self.ip, self.puerto)


@dataclass(frozen=True)
class Configuracion:
    identificador: str
    vecinos: dict[str, int]
    direcciones: dict[str, Direccion]
    topologia: dict[str, dict[str, int]]
    host: HostLocal | None

    @property
    def direccion_propia(self) -> Direccion:
        return self.direcciones[self.identificador]

    def direccion_de(self, nodo: str) -> Direccion | None:
        return self.direcciones.get(nodo)


def cargar(
    identificador: str,
    ruta_topologia: Path | str = RUTA_TOPOLOGIA,
    ruta_nombres: Path | str = RUTA_NOMBRES,
) -> Configuracion:
    """Lee ambos archivos y devuelve la vista que le corresponde a este nodo."""
    topologia = _leer_json(Path(ruta_topologia))
    nombres = _leer_json(Path(ruta_nombres))

    if identificador not in topologia:
        raise ErrorConfiguracion(f"el nodo {identificador} no aparece en la topologia")
    if identificador not in nombres:
        raise ErrorConfiguracion(f"el nodo {identificador} no tiene direccion asignada")

    _validar_topologia(topologia)

    direcciones = {nodo: _leer_direccion(nodo, datos) for nodo, datos in nombres.items()}
    vecinos = dict(topologia[identificador])

    faltantes = sorted(vecino for vecino in vecinos if vecino not in direcciones)
    if faltantes:
        raise ErrorConfiguracion(
            f"no hay direccion para los vecinos de {identificador}: {', '.join(faltantes)}"
        )

    return Configuracion(
        identificador=identificador,
        vecinos=vecinos,
        direcciones=direcciones,
        topologia=topologia,
        host=_leer_host(nombres[identificador].get("host")),
    )


def con_host(
    config: Configuracion, tipo: str, puerto: int, ip: str | None = None
) -> Configuracion:
    """Declara el equipo terminal desde la linea de comandos, sin tocar el archivo.

    `config/nombres.json` es el acuerdo compartido con las otras parejas, asi que
    conviene no editarlo para mover el ATM o el banco a otro router: basta con
    levantar ese router y su equipo terminal con las mismas opciones.

    Sin `ip` el equipo se asume en la misma maquina que su puerta de enlace, que
    es como corren el cajero y el servidor en la topologia acordada.
    """
    host = _leer_host(
        {"tipo": tipo, "ip": ip or config.direccion_propia.ip, "puerto": puerto}
    )
    return replace(config, host=host)


def _leer_json(ruta: Path) -> dict:
    if not ruta.exists():
        raise ErrorConfiguracion(f"no existe el archivo de configuracion {ruta}")
    try:
        contenido = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ErrorConfiguracion(f"{ruta} no es JSON valido: {error}") from error
    if not isinstance(contenido, dict):
        raise ErrorConfiguracion(f"{ruta} debe contener un objeto JSON")
    return contenido


def _validar_topologia(topologia: dict) -> None:
    """Exige que cada enlace este declarado en los dos extremos y con el mismo costo.

    Un grafo asimetrico produciria rutas que existen en un sentido y no en el
    otro, asi que preferimos fallar al arrancar antes que depurarlo en la red.
    """
    for nodo, enlaces in topologia.items():
        if not isinstance(enlaces, dict):
            raise ErrorConfiguracion(f"los enlaces de {nodo} deben ser un objeto {{vecino: costo}}")
        for vecino, costo in enlaces.items():
            if isinstance(costo, bool) or not isinstance(costo, (int, float)) or costo <= 0:
                raise ErrorConfiguracion(f"costo invalido en el enlace {nodo}-{vecino}: {costo!r}")
            if vecino not in topologia:
                raise ErrorConfiguracion(f"{nodo} declara al vecino {vecino}, que no existe")
            reciproco = topologia[vecino].get(nodo)
            if reciproco is None:
                raise ErrorConfiguracion(f"{vecino} no declara de vuelta el enlace con {nodo}")
            if reciproco != costo:
                raise ErrorConfiguracion(
                    f"el enlace {nodo}-{vecino} tiene costos distintos en cada extremo: "
                    f"{costo} y {reciproco}"
                )


def _leer_direccion(nodo: str, datos: object) -> Direccion:
    if not isinstance(datos, dict):
        raise ErrorConfiguracion(f"la entrada de {nodo} en nombres.json debe ser un objeto")
    ip = datos.get("ip")
    puerto = datos.get("puerto")
    if not isinstance(ip, str) or not ip:
        raise ErrorConfiguracion(f"{nodo} no tiene una ip valida")
    if isinstance(puerto, bool) or not isinstance(puerto, int) or not 0 < puerto < 65536:
        raise ErrorConfiguracion(f"{nodo} no tiene un puerto valido")
    return Direccion(ip=ip, puerto=puerto)


def _leer_host(datos: object) -> HostLocal | None:
    if datos is None:
        return None
    if not isinstance(datos, dict):
        raise ErrorConfiguracion("la entrada 'host' debe ser un objeto")
    tipo = datos.get("tipo")
    ip = datos.get("ip")
    puerto = datos.get("puerto")
    if not isinstance(tipo, str) or not tipo:
        raise ErrorConfiguracion("el host local necesita un 'tipo' (atm o banco)")
    if not isinstance(ip, str) or not ip:
        raise ErrorConfiguracion("el host local necesita una ip")
    if isinstance(puerto, bool) or not isinstance(puerto, int) or not 0 < puerto < 65536:
        raise ErrorConfiguracion("el host local necesita un puerto valido")
    return HostLocal(tipo=tipo, ip=ip, puerto=puerto)
