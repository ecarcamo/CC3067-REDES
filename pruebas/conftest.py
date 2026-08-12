"""Configuracion comun de las pruebas."""

import logging

import pytest


@pytest.fixture(autouse=True, scope="session")
def _silenciar_bitacora():
    """Evita que la bitacora del nodo ensucie la salida de pytest."""
    registro = logging.getLogger("nodo")
    registro.addHandler(logging.NullHandler())
    registro.propagate = False
