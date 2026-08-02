# Evidencia — Hito 3: integración end-to-end

Matriz de humo ejecutada conectando `emisor/main.py` con `receptor/main.js`
sobre `127.0.0.1:2705`. Sesión: login con tarjeta `23016` / PIN
`123456789`, retiro y logout.

## 1. Hamming, probabilidad 0.00 — mensaje llega intacto

```
[EMISOR] Conectado a 127.0.0.1:2705
>> Autenticacion exitosa
--- MENU ---
1) Retirar dinero
2) Salir
>> Por favor tome sus $50.00
>> Saldo restante: $350.00
>> Hasta luego
```

```
[RECEPTOR] Recibido: {"action":"login","data":{"card":"23016","pin":"123456789"}}
[RECEPTOR] Recibido: {"action":"withdraw","data":{"amount":50}}
[RECEPTOR] Recibido: {"action":"logout","data":{}}
```

## 2. Hamming, probabilidad 0.001 — se corrige, el receptor lo reporta

```
Algoritmo (hamming/crc32): hamming
Tasa de error por bit (ej. 0.01): 0.001
>> Autenticacion exitosa
--- MENU ---
>> Por favor tome sus $25.00
>> Saldo restante: $375.00
>> Hasta luego
```

A tasas más altas (ej. `0.02`) sobre un mensaje JSON largo, es frecuente
que algún bloque de 12 bits reciba **2 bits volteados**: Hamming reporta
`corregido` pero el bloque queda mal reconstruido y el JSON deja de ser
válido. El receptor detecta este caso (falla al parsear) y responde
`"Mensaje corrupto"` en vez de caerse — comportamiento esperado, ver
"Limitación conocida" en el `README.md` principal.

## 3. CRC-32, probabilidad 0.00 — mensaje llega intacto

```
Algoritmo (hamming/crc32): crc32
Tasa de error por bit (ej. 0.01): 0.0
>> Autenticacion exitosa
>> Por favor tome sus $10.00
>> Saldo restante: $365.00
>> Hasta luego
```

## 4. CRC-32, probabilidad 0.05 — se detecta el error y se reporta a la aplicación

```
Algoritmo (hamming/crc32): crc32
Tasa de error por bit (ej. 0.01): 0.05
>> Trama corrupta: checksum no coincide: la trama llego corrupta
   Intenta de nuevo.
```

```
[RECEPTOR] Trama corrupta: checksum no coincide: la trama llego corrupta
```

CRC-32 nunca corrige (por diseño): ante cualquier bit alterado, el
checksum recalculado no coincide y la capa de enlace reporta
`error_no_corregible`. La capa de aplicación lo refleja al usuario y pide
reintentar el login, sin procesar la operación.
