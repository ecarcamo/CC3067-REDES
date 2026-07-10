# Laboratorio #1 – Esquemas de comunicación e introducción a Wireshark
## Parte 1: Esquemas de comunicación (Reporte grupal)

**Pareja:**
- Esteban Cárcamo — Carné 23016
- Jorge Luis Felipe Aguilar — Carné 23195

**Otra pareja (parte 3.3):**
- Fernando Rueda — 23748
- Fernando Hernández — 23645

---

## Introducción

En este laboratorio se exploraron distintos esquemas de comunicación utilizados históricamente en la telegrafía —código Morse y código Baudot— con el objetivo de identificar sus ventajas, desventajas y complejidad al momento de transmitir información. La actividad se dividió en tres partes: primero se practicó el envío y recepción de mensajes en tiempo real utilizando ambos esquemas mediante una estación de telégrafo virtual y comunicación por voz; luego se repitió la dinámica utilizando el esquema más fácil, pero enviando los mensajes de forma "empaquetada" mediante notas de voz; y finalmente se simuló un esquema de conmutación de mensajes, cooperando con otra pareja, donde un integrante actuó como conmutador y los demás como clientes. A lo largo de las tres partes se registraron los aciertos y errores de cada transmisión para comparar cuantitativamente el desempeño de cada esquema y forma de envío.

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

Para esta parte, el grupo se organizó de la siguiente manera:

- **Conmutador:** Esteban (E)
- **Clientes:** Jorge Luis Felipe Aguilar (J), Fernando Rueda (R), Fernando Hernández (F)

### Protocolo utilizado

Cada cliente identificó con una **letra distintiva** (la inicial de su nombre) tanto a sí mismo como a los demás clientes: J para Jorge Luis Felipe, R para Rueda, F para Fernando Hernández y E para Esteban (conmutador). Con esto se definió el siguiente protocolo:

1. **Direccionamiento del mensaje:** cada nota de voz enviada al conmutador comenzaba con una sola letra que indicaba el **destinatario final** del mensaje (por ejemplo, una nota de voz que iniciaba con "R" debía ser reenviada por el conmutador al cliente Rueda). El conmutador escuchaba esa primera letra de la nota recibida y, con base en ella, decidía a quién reenviarla.
2. **Señal de "listo para recibir" (control de flujo):** el conmutador solo podía atender a un cliente a la vez, por lo que se estableció una señal de control: el conmutador enviaba una nota de voz con solo la letra **"Y"** al cliente que debía transmitir a continuación, indicando "ya estoy libre, puedes enviar tu mensaje ahora". El cliente que recibía la "Y" quedaba habilitado para enviar su nota de voz con el mensaje dirigido a otro cliente.
3. **Ciclo de atención:** al recibir una nota de un cliente, el conmutador (a) leía la primera letra para saber el destino, (b) reenviaba el audio a ese destinatario, y (c) enviaba una "Y" al siguiente cliente en turno para habilitar su envío. Este ciclo se repetía secuencialmente, de forma que en todo momento solo un cliente tenía "permiso" para transmitir, evitando que dos clientes enviaran audios al conmutador al mismo tiempo.

De esta forma, el destino se determinó mediante un **identificador explícito al inicio del mensaje** (similar a una dirección de destino en un encabezado de paquete), y la sobrecarga del conmutador se evitó mediante un **esquema de turnos controlado por una señal explícita de disponibilidad** (análogo a un mecanismo de control de flujo/token de acceso al medio), en vez de dejar que los clientes enviaran mensajes de forma libre y simultánea.

### ¿Qué posibilidades incluye la introducción de un conmutador en el sistema?

Un conmutador permite que los clientes se comuniquen **sin necesidad de un canal directo entre cada par de ellos**: en lugar de que cada cliente tenga que coordinar y mantener una conexión individual con todos los demás (lo cual crecería rápidamente en complejidad conforme aumenta el número de clientes), basta con que cada uno tenga una única conexión hacia el conmutador. Esto centraliza el enrutamiento de los mensajes y hace que sea el conmutador quien decida hacia dónde reenviar cada transmisión según la información de direccionamiento (en nuestro caso, la letra inicial del mensaje). También facilita escalar el sistema agregando nuevos clientes sin rediseñar toda la red, ya que solo se necesita una nueva conexión hacia el conmutador existente, y permite implementar reglas de control (como nuestro esquema de turnos con la señal "Y") para ordenar el acceso al medio y evitar colisiones o sobrecarga.

### ¿Qué ventajas/desventajas se tienen al momento de agregar más conmutadores al sistema?

**Ventajas:**
- Se reduce la carga sobre un único conmutador al distribuir los clientes entre varios, disminuyendo la probabilidad de que se convierta en un cuello de botella.
- Se gana redundancia: si un conmutador falla o se satura, otro puede seguir atendiendo parte de la red.
- Permite escalar geográficamente o por grupos, conectando conmutadores entre sí en lugar de que todos los clientes dependan de un solo punto central.

**Desventajas:**
- Aumenta la complejidad del enrutamiento, ya que ahora un mensaje puede requerir varios saltos (cliente → conmutador A → conmutador B → cliente destino) en lugar de un solo salto.
- Cada salto adicional introduce más retraso y más oportunidades de error o pérdida en la transmisión (como se evidenció en la parte 3.2, donde incluso un solo salto ya generaba errores de recepción).
- Se requiere coordinación adicional entre los conmutadores (saber qué conmutador atiende a qué clientes), lo que añade overhead de gestión que no existe con un único conmutador.

---

## Conclusiones

- El código Morse resultó más fácil de recibir que el código Baudot porque se apoya en un patrón rítmico (duración e intervalos de pulsos) que el oído humano reconoce con mayor naturalidad, mientras que Baudot exige contar con exactitud una secuencia de 5 bits por carácter sin ninguna pista rítmica que ayude a diferenciarlos. Esto se reflejó directamente en la tasa de error: 50.0% en Morse frente a 66.7% en Baudot durante la transmisión en tiempo real.
- El formato "empaquetado" (notas de voz) no mejoró la tasa de error frente a la transmisión en vivo con Morse (se mantuvo en 50.0%), pero sí cambió la naturaleza de las dificultades: al no existir retroalimentación en tiempo real ni posibilidad de pausar o pedir aclaración a media transmisión, un solo error de conteo en el receptor podía arruinar la interpretación del resto del mensaje, y la corrección solo era posible reenviando la nota completa.
- La introducción de un conmutador permitió que los tres clientes se comunicaran entre sí sin necesidad de un canal directo entre cada par, centralizando el enrutamiento mediante un identificador simple (la letra inicial del destinatario) y evitando colisiones mediante una señal explícita de turno ("Y"). Esto evidenció, a pequeña escala, los mismos principios que utilizan los conmutadores y routers reales para direccionar y controlar el flujo de paquetes en una red.
- Agregar más conmutadores a un sistema implica un balance entre robustez/escalabilidad (menor carga por conmutador, redundancia) y complejidad operativa (más saltos, más retrasos, más coordinación entre conmutadores), un compromiso que también aplica a las redes de computadoras reales al decidir su topología.
- En general, la actividad permitió comprobar de forma práctica que la elección de un esquema de codificación y la forma en que se empaqueta y enruta la información tienen un impacto medible en la tasa de error y en la complejidad de la comunicación, incluso en un sistema tan simple como el simulado en este laboratorio.
