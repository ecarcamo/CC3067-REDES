# Reporte Individual - Laboratorio #1
**Curso:** CC3067 - Redes  
**Nombre:** Felipe Aguilar  
**Carnet:** 23195  

---

## 1. Introducción y Descripción
El presente reporte documenta la experiencia individual adquirida en la segunda fase del Laboratorio #1, enfocada en la introducción y personalización de Wireshark. A través de esta práctica, se exploró la captura de tráfico en tiempo real utilizando el sistema operativo macOS. El objetivo principal fue familiarizarse con la interfaz de Wireshark, el manejo de perfiles, la configuración de búferes circulares (Ring Buffer) para capturas prolongadas y el análisis de la capa de aplicación mediante la inspección de paquetes HTTP.

---

## 2. Capturas y Evidencias (Segunda Parte)

### 3.4 Personalización del entorno
Se creó un perfil personalizado, se ajustó el formato de tiempo, se agregó la columna de longitud del protocolo y se aplicó un filtro de color y un botón de acceso rápido para paquetes TCP con la bandera SYN activa. Además, se limpió la vista ocultando las interfaces virtuales de macOS.


### 3.5 Configuración de la captura de paquetes (Ring Buffer)
Se configuró un Ring Buffer limitando el tamaño a 5 MB por archivo con un máximo de 10 archivos. Esto es especialmente útil para dejar capturas corriendo sin agotar el espacio en disco ni la memoria RAM del equipo.

### 3.6 Análisis de paquetes (Protocolo HTTP)
Captura realizada durante la petición a la página web de prueba.


---

## 3. Respuestas a las Preguntas Mencionadas

### Sobre el comando `ifconfig` (Sección 3.5)
Al ejecutar el comando `ifconfig` en la terminal de macOS, se despliega una lista detallada de todas las interfaces de red físicas y virtuales del equipo (lo0, en0, awdl0, utun0, etc.). En mi caso particular, la interfaz activa de conexión inalámbrica (Wi-Fi) es `en0`. El comando nos permite observar el estado de la interfaz (`status: active`), la dirección MAC (`ether`) y la dirección IP asignada (`inet`), información vital antes de iniciar una captura para saber exactamente qué interfaz debe escuchar Wireshark.

### Análisis del protocolo HTTP (Sección 3.6)
Tras analizar el paquete `HTTP GET` y su respectiva respuesta `HTTP/1.1 200 OK`, se determinó lo siguiente:

*   **a. ¿Qué versión de HTTP está ejecutando su navegador?**  
    El navegador está utilizando la versión **HTTP/1.1** (visible en el Request URI y los headers del paquete GET).
*   **b. ¿Qué versión de HTTP está ejecutando el servidor?**  
    El servidor también responde utilizando **HTTP/1.1** (visible en el inicio del paquete de respuesta 200 OK).
*   **c. ¿Qué lenguajes (si aplica) indica el navegador que acepta al servidor?**  
    Revisando el header `Accept-Language` en el paquete GET de mi captura, el navegador indica que acepta lenguajes como español e inglés (ej. `es-ES, es;q=0.9, en;q=0.8`).
*   **d. ¿Cuántos bytes de contenido fueron devueltos por el servidor?**  
    Revisando el header `Content-Length` en la respuesta del servidor, se devolvieron **128 bytes** de contenido (que corresponden al texto en HTML).
*   **e. Problemas de rendimiento y Wireshark en servidores:**  
    En caso de un problema de rendimiento, convendría "escuchar" los paquetes en los dispositivos intermedios que actúan como cuellos de botella (como los *routers* o conmutadores principales). **No es conveniente** instalar y ejecutar Wireshark directamente en un servidor de producción. Capturar paquetes es un proceso intensivo que consume mucha CPU, memoria RAM y operaciones de escritura en disco; esto degradaría aún más el rendimiento del servidor e impactaría los servicios que ofrece.

---

## 4. Discusión y Comentarios
La actividad resultó muy enriquecedora para comprender cómo la teoría de redes se aplica en la práctica. Durante la primera parte del laboratorio (esquemas de comunicación y notas de voz) pude notar las dificultades de la transmisión manual y la necesidad de protocolos estrictos para evitar pérdida de información. 

En esta segunda parte, implementar Wireshark en macOS presentó un reto inicial con los permisos de las interfaces, lo cual se solucionó instalando el paquete `ChmodBPF`. Una vez superado esto, la capacidad de personalizar el entorno comprobó ser una herramienta invaluable; tener botones de filtros (como el TCP SYN) agiliza drásticamente el análisis. La actividad de Ring Buffer me pareció una práctica excelente para escenarios de la vida real donde el tráfico de red es masivo y se requiere un monitoreo prolongado sin colapsar la computadora del analista.

---

## 5. Conclusiones
*   Wireshark es una herramienta fundamental que "traduce" la abstracción de la comunicación de red en datos legibles, permitiendo inspeccionar exactamente qué solicita el cliente y qué devuelve el servidor (como se evidenció con los headers HTTP).
*   La configuración del entorno (perfiles, filtros por colores, columnas personalizadas) no es solo estética, sino una necesidad operativa para filtrar el "ruido" en redes altamente congestionadas.
*   El uso de Ring Buffers previene el desbordamiento de memoria y almacenamiento, lo que es una práctica estándar indispensable para la recolección de evidencia en ciberseguridad o resolución de cuellos de botella.

---

## 6. Referencias Utilizadas
*   Kurose, J. F., & Ross, K. W. (s.f.). *Computer Networking: A Top-Down Approach*. 
*   Documentación oficial de Wireshark: [https://www.wireshark.org/docs/](https://www.wireshark.org/docs/)
*   Páginas manuales del sistema macOS (`man ifconfig`).