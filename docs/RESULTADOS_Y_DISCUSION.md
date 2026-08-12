# Resultados y discusión

## Resultados

Se ejecutaron los nueve routers en procesos independientes, el servidor
bancario conectado a E y el ATM conectado a A. Luego de 12 segundos de
convergencia, la cuenta `23016` se autenticó correctamente, retiró `$50.00` de
un saldo inicial de `$400.00` y cerró sesión. El ATM presentó un saldo final de
`$350.00`.

La bitácora registró la ruta óptima de ida y su retorno:

```text
A: mensaje hacia E reenviado por I; ruta=['A']
I: mensaje hacia E reenviado por D; ruta=['A', 'I']
D: mensaje hacia E reenviado por E; ruta=['A', 'I', 'D']
E: mensaje entregado al host local; ruta=['A', 'I', 'D', 'E']

E: mensaje hacia A reenviado por D; ruta=['E']
D: mensaje hacia A reenviado por I; ruta=['E', 'D']
I: mensaje hacia A reenviado por A; ruta=['E', 'D', 'I']
A: mensaje entregado al host local; ruta=['E', 'D', 'I', 'A']
```

El costo de A→I→D→E fue `1 + 6 + 1 = 8`. La tabla generada por A confirmó que
el primer salto hacia E es I:

| destino | siguiente salto | costo | IP | puerto |
|---|---|---:|---|---:|
| A | A | 0 | 127.0.0.1 | 5001 |
| B | B | 7 | 127.0.0.1 | 5002 |
| C | C | 7 | 127.0.0.1 | 5003 |
| D | I | 7 | 127.0.0.1 | 5009 |
| E | I | 8 | 127.0.0.1 | 5009 |
| F | I | 8 | 127.0.0.1 | 5009 |
| G | I | 11 | 127.0.0.1 | 5009 |
| H | I | 12 | 127.0.0.1 | 5009 |
| I | I | 1 | 127.0.0.1 | 5009 |

Las 201 pruebas automatizadas finalizaron satisfactoriamente. Incluyen la
topología real calculada manualmente, desempates, destinos inalcanzables,
persistencia CSV, descarte por TTL, detección de bucles y operaciones del banco.

## Discusión

Los resultados comprueban que el plano de control y el de datos operan en
paralelo y se comunican exclusivamente mediante la tabla CSV. La escritura
atómica evita lecturas parciales mientras el grafo reconverge. El siguiente
salto, y no la dirección final, determina el socket usado en cada router.

La ruta observada coincide con Dijkstra y demuestra que el tráfico no sigue el
enlace directo aparente A→C, cuyo recorrido hasta E cuesta 13. El TTL y la lista
`hops` aportan defensas complementarias: el primero limita cualquier circulación
y la segunda detecta inmediatamente el retorno a un router ya visitado.

La prueba se realizó sobre localhost. Para Tailscale únicamente deben cambiarse
las IP de `config/nombres.json`. Antes de interoperar con las otras parejas se
deben homologar los costos ambiguos del diagrama, los identificadores y el
formato de respuesta exitoso del banco; estas decisiones no afectan la validez
de la corrida local.
