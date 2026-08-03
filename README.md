# CC3067-REDES

## Laboratorio 2 — Esquemas de detección y corrección de errores

Simulación de un cajero automático (emisor, Python) que se comunica por TCP
con un servidor bancario (receptor, Node.js), aplicando ruido configurable
al canal y protegiendo cada mensaje con uno de tres algoritmos de integridad:

- **Hamming genérico `(n, m)`** — corrección, con `m` configurable.
- **CRC-32 (IEEE 802.3)** — detección de errores.
- **Fletcher** — detección con palabras de 8, 16 o 32 bits.

Ver [`docs/CONTRATO.md`](docs/CONTRATO.md) para las interfaces de capa y de
algoritmo, y [`docs/PROTOCOLO.md`](docs/PROTOCOLO.md) para el formato exacto
de la trama en el socket.

## Requisitos

- Python 3.11+
- Node.js 20+

Instalar Python: `python3 -m pip install -r requirements.txt`. El receptor no
requiere paquetes externos.

## Estructura

```
emisor/       cajero automático (Python) — aplicacion, presentacion, enlace, ruido, transmision
receptor/     servidor bancario (Node)   — aplicacion, presentacion, enlace, transmision (sin ruido)
docs/         contratos, protocolo y vectores de prueba compartidos
pruebas/      motor de simulaciones y generación de gráficas
```

## Cómo ejecutar

**1. Levantar el receptor (banco):**

```bash
cd receptor
node main.js
```

**2. Levantar el emisor (cajero), en otra terminal:**

```bash
python3 emisor/main.py
```

El emisor pedirá el algoritmo (`hamming`, `crc32` o `fletcher`), su
configuración cuando corresponda, la tasa de error y luego el flujo normal del
cajero: número de tarjeta, PIN, y el menú de retiro/salida.

Tarjetas de prueba (`receptor/capas/aplicacion.js`):

| Tarjeta | PIN | Saldo inicial |
|---|---|---|
| `4111111111111111` | `1234` | $500.00 |
| `5500005555555559` | `0000` | $1200.50 |
| `23016` | `123456789` | $400.00 |

## Ejemplo de sesión

```
Algoritmo (hamming/crc32/fletcher): hamming
Bits de datos por bloque m (ej. 4/8/11/16): 8
Tasa de error por bit (ej. 0.01): 0.001
[EMISOR] Conectado a 127.0.0.1:2705
Numero de tarjeta: 23016
PIN: 123456789
>> Autenticacion exitosa

--- MENU ---
1) Retirar dinero
2) Salir
Elige una opcion: 1
Monto a retirar: 25
>> Por favor tome sus $25.00
>> Saldo restante: $375.00

--- MENU ---
1) Retirar dinero
2) Salir
Elige una opcion: 2
>> Hasta luego
```

## Pruebas unitarias

```bash
# Python (emisor + algoritmos)
python3 -m pytest emisor/tests/ -q

# JavaScript (receptor + algoritmos)
cd receptor && node --test tests/*.test.js
```

Ambos lados verifican los mismos vectores de [`docs/vectores.json`](docs/vectores.json).

## Motor de pruebas y gráficas

```bash
python3 pruebas/motor.py        # genera 58,800 casos identificados por configuracion
python3 pruebas/graficas.py     # lee el CSV y genera pruebas/graficas/*.png
```

Ver [`docs/evidencias/matriz_de_humo.md`](docs/evidencias/matriz_de_humo.md)
para la evidencia de la integración end-to-end (Hito 3).

## Limitación conocida

Hamming simple (SEC, *single-error-correcting*) no detecta de forma
confiable errores dobles dentro de un mismo bloque: puede reportar
`corregido` y aun así entregar datos incorrectos. Es una limitación real
del algoritmo, documentada también en las pruebas
(`test_voltear_dos_bits_no_garantiza_el_resultado_correcto`) y visible en
la gráfica de falsos negativos de `pruebas/graficas.py`.
