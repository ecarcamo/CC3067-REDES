# Protocolo de la trama en el socket

El socket transporta una línea JSON terminada en `\n` (delimitador de
mensaje: TCP es un flujo de bytes sin fronteras, así que cada mensaje debe
tener un final explícito).

```json
{
  "version": 1,
  "algoritmo": "hamming",
  "parametros": { "m": 8, "bloques": 5 },
  "trama": "011010010110..."
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `version` | int | Fijo en `1` |
| `algoritmo` | string | `"hamming"` o `"crc32"` |
| `parametros` | objeto | Lo que devolvió `calcular()`. El receptor lo pasa tal cual a `verificar()` |
| `trama` | string | Solo caracteres `'0'` y `'1'`. **Ya trae el ruido aplicado** |

## Reglas

- `version`, `algoritmo` y `parametros` son metadatos de control: **no se
  les aplica ruido**.
- `trama` es lo único que pasa por la capa de ruido. Incluye los bits de
  redundancia (paridad de Hamming o checksum CRC-32).
- Un mensaje = una línea. El receptor (`main.js`) hace *buffering* hasta
  encontrar `\n` antes de parsear el JSON, porque `recv()`/`data` puede
  entregar mensajes partidos o pegados.

## Flujo de un mensaje

1. `aplicacion` obtiene el texto, el algoritmo elegido y la tasa de error.
2. `presentacion.codificar_mensaje` convierte el texto a bits ASCII (8 bits
   por carácter).
3. `enlace.calcular_integridad` delega en el algoritmo del registro y
   produce la trama con redundancia y sus `parametros`.
4. `ruido.aplicar_ruido` voltea bits de la trama según la probabilidad
   configurada (solo del lado del emisor).
5. `transmision.enviar_informacion` arma el sobre JSON de arriba y lo manda
   por el socket terminado en `\n`.
6. El receptor lee la línea, reconstruye el sobre, y llama a
   `enlace.verificar_integridad` con la `trama` y los `parametros`
   recibidos.
7. Si el algoritmo pudo corregir o el mensaje llegó intacto, `presentacion`
   decodifica los bits de datos de vuelta a texto y la capa de aplicación
   del banco procesa la operación normalmente. Si no, se reporta el error
   sin procesar la operación.
