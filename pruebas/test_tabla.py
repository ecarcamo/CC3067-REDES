"""Pruebas de la frontera CSV entre routing y forwarding."""

from configuracion import Direccion
from control.dijkstra import Ruta
from control import tabla


def test_tabla_se_escribe_y_carga_sin_perder_datos(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rutas = {
        "A": Ruta("A", 0, "A"),
        "E": Ruta("E", 8, "I"),
        "Z": Ruta("Z", 9, "SIN_DIRECCION"),
    }
    direcciones = {
        "A": Direccion("127.0.0.1", 5001),
        "I": Direccion("100.1.2.3", 5009),
    }

    archivo = tabla.escribir("A", rutas, direcciones)
    entradas = tabla.cargar("A")

    assert archivo.name == "A_tabla_enrutamiento.csv"
    assert archivo.read_text(encoding="utf-8").splitlines()[0] == \
        "destino,siguiente_salto,costo,ip,puerto"
    assert entradas["E"] == tabla.EntradaTabla("E", "I", 8.0, "100.1.2.3", 5009)
    assert "Z" not in entradas


def test_cargar_devuelve_vacio_antes_de_la_convergencia(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert tabla.cargar("A") == {}
