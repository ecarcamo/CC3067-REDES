# Protocolo implementado

Este documento describe exactamente lo que esta implementacion pone en el
socket. La base es la definicion que acordamos entre las tres parejas de la
topologia; lo que aqui se agrega son las decisiones que esa definicion dejaba
abiertas y que hubo que cerrar para poder programar. Todas están marcadas como
tales y ninguna cambia el formato de los mensajes, así que no rompen la
interoperabilidad.

## 1. Los dos planos comparten el puerto

Cada nodo escucha en un solo puerto. Por ahí entran los mensajes de control
(HELLO y LSA), que viajan como una línea JSON en UTF-8 terminada en `\n`, y los
mensajes de datos, que viajan siempre codificados con Hamming(7,4).

**Decisión de implementación.** El protocolo dice que el plano de datos no lleva
ninguna marca que lo anuncie, así que la clasificación es por contenido:

| La línea recibida | Se trata como |
|---|---|
| Solo contiene `0` y `1` | Trama Hamming, plano de datos |
| Empieza con `{` | JSON, plano de control |
| Cualquier otra cosa | Se descarta y se anota en la bitácora |

Las dos formas son excluyentes, así que la regla no tiene casos ambiguos. Está
en `protocolo.mensajes.clasificar`.

**Decisión de implementación.** Los bits de una trama Hamming viajan como texto
`'0'`/`'1'` y también terminan en `\n`. Hacía falta un delimitador porque TCP es
un flujo sin fronteras, y `\n` no colisiona con el alfabeto de la trama.

## 2. HELLO

```json
{ "proto": "LinkState", "type": "HELLO", "from": "A", "ttl": 1 }
```

Sale cada **5 segundos** hacia todos los vecinos configurados, estén vivos o no:
así es como se descubren. Un vecino se da por caído a los **15 segundos** sin
recibir uno, y en ese momento el nodo emite un LSA propio con el `seq` aumentado
y sin ese enlace. El `ttl` vale 1 porque un HELLO nunca se reenvía.

El HELLO solo aporta la señal de vida. El costo del enlace no se mide: se lee de
la topología compartida y es simétrico. Un HELLO de alguien que no es vecino
configurado se ignora, porque no habría costo con el cual anunciarlo.

## 3. LSA y flooding

```json
{ "proto": "LinkState", "type": "LSA", "origin": "A", "seq": 3,
  "links": { "B": 7, "I": 1, "C": 7 }, "from": "A", "ttl": 8 }
```

`origin` es el dueño del anuncio y no cambia nunca; `from` es el vecino que lo
reenvió y cambia en cada salto; `links` lleva los vecinos **vivos** del origen
con su costo.

Al recibir un LSA:

1. Si `seq` es menor o igual al mayor visto de ese `origin`, se descarta sin
   reenviar. Aquí muere el ciclo.
2. Si es mayor, se guarda, se actualiza el grafo y se reenvía a todos los
   vecinos vivos menos al que lo mandó.
3. Antes de reenviar se resta uno al `ttl` y se descarta en cero. Es el respaldo
   que cubre al nodo que reinicia con un `seq` bajo.

El `seq` propio se guarda en `estado/<nodo>_seq.txt`, porque un nodo que
reinicia no vuelve a numerar desde cero sino desde el último valor conocido más
uno. Si aun así la red recuerda un LSA nuestro más nuevo que el que creemos
haber emitido, el contador lo supera y se reanuncia de inmediato.

### Agregados de esta implementación

- **Refresco periódico.** El LSA propio se reanuncia cada 30 segundos aunque
  nada haya cambiado. Sin esto, un nodo que arranca tarde tendría que esperar un
  cambio de topología para enterarse de las partes lejanas de la red.
- **Sincronización con el vecino que se levanta.** Cuando llega el primer HELLO
  de un vecino, se le envían de una todos los anuncios que ya tenemos guardados.
  Son LSA normales, así que cualquier implementación del grupo los procesa sin
  cambios; simplemente acorta bastante la convergencia.
- **Primer anuncio diferido.** El LSA inicial espera 6 segundos, una ronda de
  HELLO, para no salir con la lista de vecinos vacía.

## 4. Construcción del grafo

**Decisión de implementación.** Solo se toma el enlace que **ambos extremos
anuncian**. Si `A` anuncia `B` pero `B` no anuncia `A`, el enlace no entra al
grafo.

La razón es que el protocolo no define envejecimiento de los LSA: el anuncio de
un nodo que se cayó se queda guardado para siempre en la base de los demás.
Exigir que los dos extremos coincidan hace que los vecinos vivos del nodo caído
lo desconecten con su propio LSA actualizado, y el nodo muerto queda fuera de
todo camino sin necesidad de un mecanismo de expiración. Cuando los dos costos
anunciados difieren se toma el mayor, que es la lectura conservadora.

## 5. Sobre de datos

```json
{ "type": "message", "from": "A", "to": "E", "ttl": 16,
  "hops": ["A"], "payload": { "op": "withdraw", "amount": 500 } }
```

El sobre completo se codifica con Hamming(7,4) antes de mandarlo. Los routers
solo leen `to`; el `payload` es el mensaje entre el ATM y el banco y ningún nodo
intermedio lo abre. Al reenviar, el nodo se agrega a `hops` y resta uno al
`ttl`; descarta si el `ttl` llega a cero o si se encuentra a sí mismo en `hops`,
que sería un bucle de ruteo.

Los `payload` acordados son `auth` (usuario y pin), `withdraw` (monto), `logout`
y `error` (código y mensaje). La operación va en `op` para no chocar con el
`type` del sobre.

**Pendiente de acordar con las otras dos parejas:** la definición grupal solo
fija los `payload` de ida. Falta el formato de las respuestas del banco hacia el
ATM.

### Qué son `from` y `to`

**Decisión de implementación.** Son los **nodos router** de cada extremo: `A`,
la puerta de enlace del ATM, y `E`, la del servidor bancario. La definición
grupal usa esas letras en su ejemplo y a la vez aclara que el ATM y el banco no
son routers, así que se resolvió de la forma que respeta ambas cosas: el equipo
terminal no tiene identificador propio en la red y cuando un router ve que `to`
es él mismo, no reenvía sino que entrega al host local que tiene declarado en
`config/nombres.json`.

## 6. Hamming(7,4)

El JSON se pasa a bytes UTF-8 y cada byte se parte en dos nibbles empezando por
el más significativo. Cada nibble `d1 d2 d3 d4` produce el bloque
`p1 p2 d1 p3 d2 d3 d4` con paridad par:

```
p1 = d1 ^ d2 ^ d4        cubre las posiciones 1, 3, 5, 7
p2 = d1 ^ d3 ^ d4        cubre las posiciones 2, 3, 6, 7
p3 = d2 ^ d3 ^ d4        cubre las posiciones 4, 5, 6, 7
```

Son **14 bits exactos por byte**, sin relleno y sin metadatos: el receptor
reconstruye el mensaje solo a partir de la cadena de bits. Al decodificar, el
síndrome da la posición 1-indexada del bit a corregir, o cero si el bloque llegó
intacto. Corrige un bit por bloque de siete; con dos o más el bloque se
"corrige" hacia un valor equivocado, y eso se detecta al fallar la
decodificación UTF-8 o el parseo del JSON.

## 7. Costos de enlace

| Enlace | Costo | Enlace | Costo |
|---|---|---|---|
| A–B | 7 | D–E | 1 |
| A–C | 7 | D–F | 1 |
| A–I | 1 | D–I | 6 |
| B–F | 2 | E–G | 4 |
| C–D | 5 | F–G | 3 |
| | | F–H | 4 |

Están en `config/topologia.json` y una prueba unitaria verifica que el archivo
siga coincidiendo con esta tabla, para que un cambio accidental no rompa la
interoperabilidad en silencio.

> Nota: estos son los costos de la definición grupal. En el diagrama del
> enunciado, los enlaces B–F, D–E y F–G se leen con valores distintos porque los
> números son difíciles de distinguir en la imagen. Conviene confirmarlo con las
> otras dos parejas antes de las pruebas: basta con que las tres usemos la misma
> tabla.
