"""Equipos terminales de la red: el ATM y el servidor bancario.

Ninguno de los dos es un router: no corren Link State ni tienen tabla de
enrutamiento. Cada uno se conecta por sockets a su puerta de enlace
predeterminada, que es el nodo router que lo tiene declarado como `host` en
`config/nombres.json`.
"""
