# Laboratorio #1 – Esquemas de comunicación e introducción a Wireshark
## Parte 1: Esquemas de comunicación (Reporte grupal)

**Pareja:**
- Esteban Cárcamo — Carné 23016
- Jorge Luis Felipe Aguilar — Carné 23195

**Otra pareja (parte 3.3):**
- Fernando Rueda — 23748
- Fernando Hernández — 23645

---

## 3.1 Transmisión de códigos

### Resultados

**Felipe**

| Esquema | Mensaje | Resultado |
|---|---|---|
| Morse | HOLA MUNDO | Falló |
| Morse | BUENOS DIAS | Acertó |
| Morse | PERRO NEGRO | Acertó |
| Baudot | CASA GRANDE | Falló |
| Baudot | SOL Y LUNA | Acertó |
| Baudot | VIVA NETO BRAN | Falló |

**Esteban**

| Esquema | Mensaje | Resultado |
|---|---|---|
| Morse | Valorant | Falló (se escuchó "HARORAYV") |
| Morse | Python | Falló (se escuchó "RWTHON") |
| Morse | CARRO ROJO | Acertó |
| Baudot | HAMBURGUESA | Acertó |
| Baudot | MAZATENANGO | Falló |
| Baudot | Computadora | Falló |

### Resumen de errores

| Esquema | Mensajes enviados | Aciertos | Errores | % de error |
|---|---|---|---|---|
| Morse | 6 | 3 | 3 | 50.0% |
| Baudot | 6 | 2 | 4 | 66.7% |

### ¿Qué esquema es más fácil? ¿Más difícil? (desde la perspectiva del receptor)

El esquema más fácil de recibir fue **Morse**, ya que al tratarse de pulsos (puntos y rayas) con duraciones y silencios claramente diferenciados, el patrón rítmico de cada letra es más sencillo de reconocer de oído, incluso cuando el emisor comete pequeñas imprecisiones al transmitir.

El esquema más difícil fue **Baudot**, porque al ser una secuencia de bits (1's y 0's) de 5 posiciones por carácter, el receptor debe contar con precisión la cantidad y el orden exacto de los pulsos dentro de cada grupo, sin ningún patrón rítmico distintivo que ayude a diferenciar una letra de otra. Un solo bit mal contado desplaza toda la interpretación del carácter.

### ¿Con cuál ocurren menos errores?

Ocurrieron menos errores con **Morse**: de los 6 mensajes enviados entre ambos integrantes, 3 fueron recibidos correctamente y 3 fallaron, para una **tasa de error del 50.0%**. En Baudot, de los 6 mensajes enviados, solo 2 fueron recibidos correctamente y 4 fallaron, para una **tasa de error del 66.7%**. Esto confirma que Morse es más robusto ante errores de recepción que Baudot en esta actividad.

---

## 3.2 Transmisión "empaquetada"

Para esta parte se utilizó el esquema **Morse**, por haber sido el más fácil de recibir en la parte 3.1. Los mensajes se enviaron mediante notas de voz (VN).

### Resultados

**Esteban → Felipe**

| Mensaje enviado | Mensaje recibido | Resultado |
|---|---|---|
| ARENA | IRENI | Falló |
| PAN CON SAL | PAN CON SAL | Acertó |
| AGUA FRESCA | AOUI LFS | Falló |

**Felipe → Esteban**

| Mensaje enviado | Mensaje recibido | Resultado |
|---|---|---|
| TRANSMITIR | TRANSMITIR | Acertó |
| LABORATORIO | LABORIO | Falló |
| REPOSITORIO | REPOSITORIO | Acertó |

### Resumen de errores

| Dirección | Mensajes enviados | Aciertos | Errores | % de error |
|---|---|---|---|---|
| Esteban → Felipe | 3 | 1 | 2 | 66.7% |
| Felipe → Esteban | 3 | 2 | 1 | 33.3% |
| **Total** | **6** | **3** | **3** | **50.0%** |

### ¿Qué dificultades involucra el enviar un mensaje de esta forma "empaquetada"?

La principal dificultad es la **pérdida de retroalimentación en tiempo real**: al grabar una nota de voz, el emisor no puede saber si el receptor está listo o si va captando el mensaje correctamente, por lo que el código debe transmitirse corrido y de forma seguida, sin poder pausar a media transmisión para confirmar que la parte anterior fue entendida ni para que el receptor pida repetir algo puntual. Si el receptor se pierde en algún punto, no hay forma de "avisar" al emisor en el momento; debe esperar a que termine toda la nota de voz y, si acaso, pedir que se reenvíe el mensaje completo desde el inicio, en lugar de solo la parte que no se entendió.

A esto se suman otras dificultades propias del formato empaquetado:

- **No hay control de flujo**: el emisor decide el ritmo de todo el mensaje de una sola vez, sin ajustarse a la velocidad de comprensión del receptor.
- **Un solo error de conteo se propaga**: al no poder interrumpir, si el receptor pierde la cuenta de los pulsos en una palabra (como ocurrió con LABORATORIO → LABORIO o ARENA → IRENI), el resto del mensaje puede escucharse afectado por la misma confusión.
- **Dependencia de la calidad de la grabación**: factores como el micrófono, el ruido de fondo o la compresión de audio de la app de mensajería pueden distorsionar los pulsos, afectando particularmente a esquemas donde el ritmo y la duración exacta de cada símbolo importan.
- **Retraso en la corrección de errores**: a diferencia de una llamada en vivo (parte 3.1), donde el error se detecta y corrige casi de inmediato, en el envío empaquetado el error solo se descubre después de escuchar la nota completa, lo que aumenta el tiempo total de la comunicación cuando hay que reenviar.

---

## 3.3 Conmutación de mensajes

### ¿Qué posibilidades incluye la introducción de un conmutador en el sistema?

[Placeholder — completar: p. ej. permite que múltiples clientes se comuniquen sin una conexión directa entre cada par, centraliza el enrutamiento de mensajes, posibilita agregar más clientes sin que cada uno necesite un canal con todos los demás, etc.]

### ¿Qué ventajas/desventajas se tienen al momento de agregar más conmutadores al sistema?

**Ventajas:** [Placeholder — p. ej. mayor redundancia, distribución de carga, menor probabilidad de cuello de botella en un único punto]

**Desventajas:** [Placeholder — p. ej. mayor complejidad de coordinación, más retrasos por saltos adicionales, mayor posibilidad de error al reenviar entre conmutadores]

### Protocolo utilizado en la parte 3.3

[Placeholder — explicar cómo determinaron el destino del mensaje (p. ej. identificador de emisor/receptor al inicio del mensaje), cómo indicaron que el conmutador estaba listo para recibir, y cómo evitaron sobrecargarlo (p. ej. turnos, confirmación de recepción antes del siguiente envío).]

---

## Conclusiones

[Placeholder — agregar conclusiones grupales sobre la actividad]
