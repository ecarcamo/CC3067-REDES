"""Pruebas de la carga de configuracion y de la topologia que se entrega."""

import json
from pathlib import Path

import pytest

import configuracion

RAIZ = Path(__file__).resolve().parent.parent
TOPOLOGIA = RAIZ / "config" / "topologia.json"
NOMBRES = RAIZ / "config" / "nombres.json"

# Los seis enlaces de la topologia acordada, un nodo por integrante.
NODOS = "uvwxyz"
COSTOS_ACORDADOS = {
    ("u", "v"): 1,
    ("u", "w"): 1,
    ("u", "x"): 1,
    ("v", "w"): 1,
    ("x", "y"): 1,
    ("y", "z"): 1,
}


def test_la_topologia_entregada_es_la_acordada():
    """Si esto falla, la red deja de interoperar con las otras dos parejas."""
    topologia = json.loads(TOPOLOGIA.read_text(encoding="utf-8"))

    enlaces = {
        (min(nodo, vecino), max(nodo, vecino)): costo
        for nodo, adyacentes in topologia.items()
        for vecino, costo in adyacentes.items()
    }
    assert enlaces == COSTOS_ACORDADOS
    assert sorted(topologia) == list(NODOS)


def test_cada_nodo_carga_su_propia_vista():
    config = configuracion.cargar("v", TOPOLOGIA, NOMBRES)
    assert config.vecinos == {"u": 1, "w": 1}
    assert config.direccion_propia.puerto == 6002


def test_el_archivo_compartido_no_declara_equipos_terminales():
    """El ATM y el banco se declaran al levantar el nodo, no en el archivo.

    `nombres.json` es el acuerdo de direcciones de las tres parejas y solo lleva
    routers; quien haga de cajero o de banco lo indica con `--host-tipo` y
    `--host-puerto`, de modo que mover un equipo terminal no obliga a nadie a
    editar el archivo compartido.
    """
    for identificador in NODOS:
        assert configuracion.cargar(identificador, TOPOLOGIA, NOMBRES).host is None


def test_todos_los_nodos_de_la_topologia_arrancan():
    for identificador in NODOS:
        config = configuracion.cargar(identificador, TOPOLOGIA, NOMBRES)
        assert config.identificador == identificador
        assert config.vecinos


def _escribir(directorio: Path, topologia: dict, nombres: dict) -> tuple[Path, Path]:
    ruta_topologia = directorio / "topologia.json"
    ruta_nombres = directorio / "nombres.json"
    ruta_topologia.write_text(json.dumps(topologia), encoding="utf-8")
    ruta_nombres.write_text(json.dumps(nombres), encoding="utf-8")
    return ruta_topologia, ruta_nombres


def test_rechaza_un_enlace_con_costos_distintos_en_cada_extremo(tmp_path):
    """Un grafo asimetrico daria rutas validas en un solo sentido."""
    rutas = _escribir(
        tmp_path,
        {"A": {"B": 7}, "B": {"A": 9}},
        {"A": {"ip": "127.0.0.1", "puerto": 5001}, "B": {"ip": "127.0.0.1", "puerto": 5002}},
    )
    with pytest.raises(configuracion.ErrorConfiguracion, match="costos distintos"):
        configuracion.cargar("A", *rutas)


def test_rechaza_un_enlace_declarado_de_un_solo_lado(tmp_path):
    rutas = _escribir(
        tmp_path,
        {"A": {"B": 7}, "B": {}},
        {"A": {"ip": "127.0.0.1", "puerto": 5001}, "B": {"ip": "127.0.0.1", "puerto": 5002}},
    )
    with pytest.raises(configuracion.ErrorConfiguracion, match="no declara de vuelta"):
        configuracion.cargar("A", *rutas)


def test_rechaza_un_vecino_sin_direccion(tmp_path):
    rutas = _escribir(
        tmp_path,
        {"A": {"B": 7}, "B": {"A": 7}},
        {"A": {"ip": "127.0.0.1", "puerto": 5001}},
    )
    with pytest.raises(configuracion.ErrorConfiguracion, match="no hay direccion"):
        configuracion.cargar("A", *rutas)


def test_rechaza_un_nodo_que_no_esta_en_la_topologia(tmp_path):
    rutas = _escribir(
        tmp_path,
        {"A": {"B": 7}, "B": {"A": 7}},
        {"A": {"ip": "127.0.0.1", "puerto": 5001}, "B": {"ip": "127.0.0.1", "puerto": 5002}},
    )
    with pytest.raises(configuracion.ErrorConfiguracion, match="no aparece en la topologia"):
        configuracion.cargar("Z", *rutas)


def test_rechaza_un_puerto_invalido(tmp_path):
    rutas = _escribir(
        tmp_path,
        {"A": {"B": 7}, "B": {"A": 7}},
        {"A": {"ip": "127.0.0.1", "puerto": 99999}, "B": {"ip": "127.0.0.1", "puerto": 5002}},
    )
    with pytest.raises(configuracion.ErrorConfiguracion, match="puerto valido"):
        configuracion.cargar("A", *rutas)


def test_con_host_cuelga_un_equipo_terminal_sin_editar_el_archivo():
    """El rol de ATM o banco se decide al levantar el nodo, no en nombres.json."""
    config = configuracion.cargar("v", TOPOLOGIA, NOMBRES)
    assert config.host is None

    con_cajero = configuracion.con_host(config, "atm", 7003)
    assert con_cajero.host == configuracion.HostLocal(
        tipo="atm", ip=config.direccion_propia.ip, puerto=7003
    )
    # El resto de la vista del nodo no se toca.
    assert con_cajero.vecinos == config.vecinos
    assert con_cajero.direcciones == config.direcciones


def test_con_host_acepta_un_equipo_en_otra_maquina():
    config = configuracion.cargar("v", TOPOLOGIA, NOMBRES)
    con_banco = configuracion.con_host(config, "banco", 7004, "100.64.0.9")
    assert con_banco.host.ip == "100.64.0.9"
    assert con_banco.host.tipo == "banco"


def test_con_host_rechaza_un_puerto_invalido():
    config = configuracion.cargar("v", TOPOLOGIA, NOMBRES)
    with pytest.raises(configuracion.ErrorConfiguracion, match="puerto valido"):
        configuracion.con_host(config, "atm", 0)
