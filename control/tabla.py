"""Escritura y lectura de `<nodo>_tabla_enrutamiento.csv`.

PENDIENTE — FASE 2 (Felipe).

Este archivo es la frontera entre los dos planos: el de control lo escribe cada
vez que el grafo cambia y el de datos lo consulta para cada mensaje que reenvia.
El enunciado pide expresamente que de aqui salgan la IP y el puerto del
siguiente salto, asi que las direcciones se resuelven al escribir y el plano de
datos no vuelve a tocar `config/nombres.json`.

Formato acordado, con encabezado y una fila por destino:

    destino,siguiente_salto,costo,ip,puerto
    B,I,8,127.0.0.1,5009
    C,C,7,127.0.0.1,5003

`ip` y `puerto` son los del **siguiente salto**, no los del destino final: es a
esa direccion a la que se abre el socket. La fila del propio nodo se escribe con
costo 0 y siguiente salto igual a si mismo.
"""

from dataclasses import dataclass
from pathlib import Path

from configuracion import Direccion
from control.dijkstra import Ruta

COLUMNAS = ("destino", "siguiente_salto", "costo", "ip", "puerto")


@dataclass(frozen=True)
class EntradaTabla:
    """Una fila ya leida del CSV, lista para usar en el reenvio."""

    destino: str
    siguiente_salto: str
    costo: float
    ip: str
    puerto: int


def ruta_archivo(identificador: str) -> Path:
    """Nombre del archivo que le toca a este nodo."""
    return Path(f"{identificador}_tabla_enrutamiento.csv")


def escribir(
    identificador: str,
    rutas: dict[str, Ruta],
    direcciones: dict[str, Direccion],
) -> Path:
    """Vuelca las rutas al CSV y devuelve la ruta del archivo escrito.

    Conviene escribir a un archivo temporal y renombrarlo al final: el plano de
    datos lee este mismo archivo desde otro hilo y no debe encontrarlo a medio
    escribir. Un destino cuyo siguiente salto no tenga direccion conocida se
    omite, porque una fila sin ip ni puerto no sirve para reenviar.
    """
    raise NotImplementedError("Fase 2: escribir la tabla de enrutamiento en CSV")


def cargar(identificador: str) -> dict[str, EntradaTabla]:
    """Lee el CSV y devuelve las entradas indexadas por destino.

    Si el archivo todavia no existe se devuelve un diccionario vacio: significa
    que el plano de control aun no converge y el mensaje no se puede rutear.
    """
    raise NotImplementedError("Fase 2: leer la tabla de enrutamiento desde el CSV")
