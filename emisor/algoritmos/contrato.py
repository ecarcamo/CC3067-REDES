"""Contrato que debe cumplir todo algoritmo de integridad (corrección o detección)."""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class EstadoVerificacion(Enum):
    SIN_ERROR = "sin_error"
    CORREGIDO = "corregido"
    ERROR_NO_CORREGIBLE = "error_no_corregible"


@dataclass(frozen=True)
class TramaCodificada:
    """Resultado de calcular(): trama completa (datos + redundancia) y parametros para el receptor."""
    bits: str
    parametros: dict


@dataclass(frozen=True)
class ResultadoVerificacion:
    """Resultado de verificar(): estado, bits de datos recuperados (o None) y detalle legible."""
    estado: EstadoVerificacion
    bits: str | None
    detalle: str


class AlgoritmoIntegridad(Protocol):
    nombre: str

    def calcular(self, bits: str) -> TramaCodificada: ...

    def verificar(self, trama: str, parametros: dict) -> ResultadoVerificacion: ...
