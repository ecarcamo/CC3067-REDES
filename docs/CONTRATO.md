# Contrato de capas y de algoritmo

Fuente de verdad de las interfaces compartidas entre el emisor (Python) y el
receptor (Node). Ambos lados deben respetar exactamente estas firmas.

## Contrato del algoritmo de integridad

Todo algoritmo (corrección o detección) expone **dos operaciones puras**.
Ninguna hace I/O, ninguna imprime, ninguna conoce sockets.

- `calcular(bits: str) -> TramaCodificada`
  Recibe los bits de datos (payload ya en binario) y devuelve la trama
  completa (datos + redundancia) junto con los parámetros que el receptor
  necesitará para decodificar.

- `verificar(trama: str, parametros: dict) -> ResultadoVerificacion`
  Recibe la trama (posiblemente con ruido) y los parámetros que generó
  `calcular()`. Devuelve el estado de la verificación, los bits de datos
  recuperados (si fue posible) y un detalle legible.

### Tipos

```python
class EstadoVerificacion(Enum):
    SIN_ERROR = "sin_error"
    CORREGIDO = "corregido"
    ERROR_NO_CORREGIBLE = "error_no_corregible"

@dataclass(frozen=True)
class TramaCodificada:
    bits: str            # trama completa: datos + redundancia
    parametros: dict      # info que el receptor necesita para decodificar

@dataclass(frozen=True)
class ResultadoVerificacion:
    estado: EstadoVerificacion
    bits: str | None      # bits de datos originales, o None si no se pudo recuperar
    detalle: str          # texto legible: "error corregido en bloque 2, posicion 5"
```

El espejo en JavaScript (`receptor/algoritmos/contrato.js`) usa constantes de
cadena idénticas (`"sin_error"`, `"corregido"`, `"error_no_corregible"`) y
objetos planos con las mismas llaves: `{ bits, parametros }` y
`{ estado, bits, detalle }`.

Reglas del algoritmo de detección (CRC-32): `verificar()` solo puede devolver
`SIN_ERROR` o `ERROR_NO_CORREGIBLE`. Nunca `CORREGIDO`, porque un algoritmo de
detección no corrige.

## Contrato de capas (emisor)

| Capa | Archivo | Responsabilidad |
|---|---|---|
| Aplicación | `capas/aplicacion.py` | Pide texto/algoritmo/tasa de error al usuario, muestra el resultado |
| Presentación | `capas/presentacion.py` | Texto ⟷ bits ASCII |
| Enlace | `capas/enlace.py` | Delega en `algoritmos/registro.py` para calcular/verificar integridad |
| Ruido | `capas/ruido.py` | Voltea bits con una probabilidad configurable (simula el medio físico) |
| Transmisión | `capas/transmision.py` | Serializa/deserializa el sobre JSON sobre el socket TCP |

El receptor implementa las mismas capas **excepto ruido** (el ruido solo se
aplica del lado del emisor).

## Registro de algoritmos

`algoritmos/registro.py` (y su espejo `algoritmos/registro.js`) mapean el
nombre del algoritmo (`"hamming"` / `"crc32"`) a su instancia. Agregar un
algoritmo nuevo es una línea en el registro; la capa de enlace no cambia.

Ver también [`docs/PROTOCOLO.md`](PROTOCOLO.md) para el formato exacto de la
trama en el socket, y [`docs/vectores.json`](vectores.json) para los casos de
prueba compartidos entre Python y JS.
