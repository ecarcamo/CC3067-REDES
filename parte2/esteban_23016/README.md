# Laboratorio #1 – Parte 2: Introducción a Wireshark

**Nombre:** Esteban Cárcamo
**Carnet:** 23016

## Entorno

- SO: CachyOS (Arch-based) con Hyprland
- Wireshark 4.7.1 (instalado vía pacman, `wireshark-qt`)
- Usuario agregado al grupo `wireshark`
- Permisos de `dumpcap` configurados (`cap_dac_override,cap_net_admin,cap_net_raw=eip`)

## 3.4 Personalización del entorno

### Perfil de configuración

Se creó el perfil `Esteban_Carcamo` (Edit -> Configuration Profiles -> `+`), confirmado en la esquina inferior derecha de Wireshark ("Perfil: Esteban_Carcamo").

![Perfil Esteban_Carcamo](images/01_perfil.png)

### Apertura de intro-wireshark-trace1.pcap

Se abrió el archivo `intro-wireshark-trace1.pcap` (651 paquetes) con el perfil `Esteban_Carcamo` activo.

![Archivo pcap abierto](images/02_pcap_abierto.png)

### Formato de tiempo (Time of Day)

Se aplicó `View -> Time Display Format -> Time of Day` (Hora de día, `Ctrl+Alt+2`). La columna Time pasó de mostrar segundos relativos a la hora del reloj (ej. `13:22:45.438793`).

![Menú Time of Day](images/03_time_of_day_1.png)
![Columna Time con formato Hora de día](images/03_time_of_day_2.png)

### Columna de longitud del protocolo

Se agregó una columna personalizada `Protocol Length` (Preferencias -> Apariencia -> Columnas -> `+`), tipo `Custom` con expresión `frame.len`.

![Preferencias de columnas - Protocol Length](images/04_columna_longitud_1.png)
![Columna Protocol Length visible en el listado](images/04_columna_longitud_2.png)

### Columna "Longitud" oculta/eliminada

Se desmarcó el checkbox "Mostrado" de la columna `Length` en Preferencias de Columnas, dejando visible únicamente `Protocol Length`.

![Columna Length desmarcada en preferencias](images/05_sin_longitud_1.png)
![Listado de paquetes sin columna Length](images/05_sin_longitud_2.png)

### Esquema de paneles personalizado

Se cambió el layout (Preferencias -> Apariencia -> Diseño) a una disposición con el listado de paquetes ocupando toda la columna izquierda, y los paneles de detalles y bytes apilados en la columna derecha, distinto al esquema por defecto.

![Layout personalizado](images/06_layout.png)

### Regla de color TCP SYN=1

Se creó la regla `REGLA NUEVA TCP` (View -> Coloring Rules -> `+`) con el filtro `tcp.flags.syn == 1`, con un color distintivo que resalta los paquetes SYN del handshake TCP en el listado.

![Regla de color creada](images/07_regla_color_1.png)
![Paquetes SYN resaltados en el listado](images/07_regla_color_2.png)

### Botón de filtro rápido TCP SYN=1

Se aplicó el filtro `tcp.flags.syn == 1` (mostrando 4 de 651 paquetes: los SYN y SYN-ACK del handshake) y se guardó como botón `SYN` en la barra de filtros.

![Filtro aplicado mostrando paquetes SYN](images/08_boton_filtro_1.png)
![Detalle de paquete SYN filtrado](images/08_boton_filtro_2.png)
![Botón SYN creado en la barra de filtros](images/08_boton_filtro_3.png)

### Interfaces virtuales ocultas

Se ocultaron todas las interfaces virtuales/remotas (Loopback, Libvirt Bridge, Docker Bridge, Bridges, bluetooth, Netfilter, D-Bus, capturas remotas) dejando visibles únicamente `enp109s0` (Ethernet) y `wlan0` (WiFi). Wireshark confirma "2 interfaces shown, 18 hidden".

![Lista de interfaces simplificada](images/09_interfaces.png)

## 3.5 Configuración de la captura de paquetes (ring buffer)

### Salida de `ip a`

Se ejecutó `ip a` (equivalente moderno de `ifconfig` en Linux) para listar las interfaces de red:

![Salida de ip a](images/10_ip_a.png)

- **lo**: interfaz de loopback (`127.0.0.1/8`, `::1/128`), usada para tráfico local de la propia máquina, estado `UNKNOWN` (normal en loopback) pero `UP`.
- **enp109s0**: interfaz Ethernet física (nomenclatura *predictable network interface names* de systemd: `en`=Ethernet, `p109`=bus PCI, `s0`=slot). Estado `UP,LOWER_UP` (enlace físico activo), MTU 1500, con IP `192.168.1.39/24` asignada por DHCP (`dynamic`) y varias direcciones IPv6 (global y link-local `fe80::`).
- **wlan0**: interfaz inalámbrica, también `UP`, con IP `192.168.1.34/24` y direcciones IPv6 análogas a la anterior.
- **virbr0, docker0, br-9fdc57030137, br-e9c582f35adc**: bridges virtuales creados por `libvirt` (virtualización KVM) y Docker, en estado `DOWN`/`NO-CARRIER` porque no tienen tráfico ni contenedores/VMs activos en este momento. Cada uno tiene su propia subred privada (`192.168.122.0/24`, `172.17-19.0.0/16`).

Se identifican dos interfaces "reales" con conexión a la red física/inalámbrica (`enp109s0`, `wlan0`) y varias interfaces virtuales de software que no participan en la captura de tráfico externo.

### Configuración del ring buffer

En `Captura -> Opciones -> Salida` se configuró:
- Archivo: `lab1_23016` (formato `pcapng`)
- Crear un nuevo archivo automáticamente después de `5` megabytes
- Usar un buffer cíclico con `10` archivos

![Configuración del ring buffer](images/11_ring_buffer_config.png)

### Captura en progreso

Se inició la captura sobre la interfaz `enp109s0`, generando tráfico de red hasta acumular varios archivos.

![Captura en progreso](images/12_captura_en_progreso.png)

### Archivos generados

Al detener la captura se generaron 10 archivos de ~5 MB cada uno (`lab1_23016_20260709233049_00005` a `..._00014`). La numeración iniciando en `00005` (en vez de `00001`) confirma que el buffer cíclico funcionó correctamente, sobrescribiendo/descartando los archivos más antiguos y conservando únicamente los últimos 10.

![Archivos del ring buffer generados](images/13_archivos_generados.png)

## 3.6 Análisis de paquetes (HTTP)

_Pendiente_

## Discusión

_Pendiente_

## Conclusiones

_Pendiente_

## Referencias

_Pendiente_
