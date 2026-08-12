"""Pruebas del numero de secuencia persistente del LSA propio."""

from control.secuencia import Secuencia


def test_arranca_en_cero_y_avanza_de_uno_en_uno(tmp_path):
    secuencia = Secuencia("A", tmp_path)
    assert secuencia.actual == 0
    assert secuencia.siguiente() == 1
    assert secuencia.siguiente() == 2
    assert secuencia.actual == 2


def test_al_reiniciar_sigue_desde_el_ultimo_valor_conocido(tmp_path):
    """La definicion grupal lo pide explicito: no se vuelve a numerar desde cero."""
    primera = Secuencia("A", tmp_path)
    primera.siguiente()
    primera.siguiente()

    reiniciada = Secuencia("A", tmp_path)
    assert reiniciada.actual == 2
    assert reiniciada.siguiente() == 3


def test_cada_nodo_lleva_su_propio_contador(tmp_path):
    Secuencia("A", tmp_path).siguiente()
    assert Secuencia("B", tmp_path).actual == 0


def test_alcanzar_supera_un_valor_que_la_red_recuerda(tmp_path):
    secuencia = Secuencia("A", tmp_path)
    secuencia.alcanzar(9)
    assert secuencia.siguiente() == 10


def test_alcanzar_no_retrocede(tmp_path):
    secuencia = Secuencia("A", tmp_path)
    secuencia.alcanzar(9)
    secuencia.alcanzar(3)
    assert secuencia.actual == 9


def test_un_archivo_corrupto_no_impide_arrancar(tmp_path):
    (tmp_path / "A_seq.txt").write_text("no es un numero", encoding="utf-8")
    assert Secuencia("A", tmp_path).actual == 0
