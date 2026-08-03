# Nombres y carnés

- Jorge Luis Felipe Aguilar Portillo — 23195
- Estaban Enrique Carcamo Urizar — 23007

# Título

Comparación de Hamming, CRC-32 y Fletcher en un canal con ruido

# Descripción

Se implementó un cajero emisor en Python y un banco receptor en JavaScript,
comunicados por TCP mediante cinco capas. El sobre conserva la versión 1 y
transporta la configuración en `parametros`. Se evaluaron Hamming con
`m=4,8,16`, Fletcher con palabras de 8, 16 y 32 bits, y CRC-32 IEEE.

# Resultados

El motor ejecuta 58,800 casos reproducibles: siete configuraciones, seis
longitudes, siete probabilidades y 200 repeticiones. El CSV y las siete
gráficas se generan desde código. En ausencia de ruido todos recuperan el
mensaje; Hamming puede corregir un bit por bloque, mientras Fletcher y CRC
detectan corrupción. En el barrido completo, las tasas de recuperación fueron
62.91 % para Hamming, 33.52 % para Fletcher y 33.83 % para CRC-32. Estas tasas
incluyen probabilidades de 0 a 0.1 y no representan una sola condición del
canal. Los datos completos están en `pruebas/resultados/resultados.csv`.

# Discusión

Reducir `m` aumenta el overhead de Hamming, pero reduce la oportunidad de que
dos alteraciones coincidan en un bloque. Fletcher aumenta su checksum de 16 a
64 bits al pasar de palabras de 8 a 32. CRC-32 mantiene 32 bits de overhead y
una probabilidad teórica de colisión cercana a \(2^{-32}\); no es razonable exigir
millones de ejecuciones adicionales para observarla.

La evidencia `data` → `date` muestra la limitación SEC: dos errores en un
bloque pueden producir una corrección equivocada. Por ello, la aplicación
también protege el parseo de JSON.

# Comentario grupal sobre el tema (opcional)

[COMPLETAR POR EL GRUPO]

# Conclusiones

No existe una configuración óptima para todos los canales. Hamming conviene
cuando se desea recuperación local y el ruido es bajo; CRC-32 brinda detección
robusta con costo fijo; Fletcher ofrece una alternativa sencilla y
configurable. Separar capas permitió cambiar algoritmos sin alterar TCP ni la
lógica bancaria.

# Citas y Referencias

- Fletcher, J. G. (1982). *An Arithmetic Checksum for Serial Transmissions*.
  IEEE Transactions on Communications, 30(1), 247-252.
- IEEE. (2022). *IEEE Standard for Ethernet (IEEE 802.3-2022)*.
- Hamming, R. W. (1950). Error Detecting and Error Correcting Codes. *Bell
  System Technical Journal*, 29(2), 147-160.
