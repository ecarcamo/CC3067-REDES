#!/usr/bin/env bash
# Revisa que nodos de la topologia estan escuchando ahora mismo.
#
#   bash scripts/sondear_red.sh
#
# Lee las direcciones de config/nombres.json, asi que sirve igual en local
# (127.0.0.1) que sobre Tailscale. Un nodo "caido" es un proceso que no esta
# corriendo o un firewall que no deja pasar; conviene descartar eso antes de
# buscar el problema en el plano de control.

set -uo pipefail
cd "$(dirname "$0")/.."

NOMBRES="${1:-config/nombres.json}"
ESPERA=3

python3 -c "
import json, sys
datos = json.load(open('$NOMBRES', encoding='utf-8'))
for nodo in sorted(datos):
    entrada = datos[nodo]
    print(nodo, entrada['ip'], entrada['puerto'])
    host = entrada.get('host')
    if host:
        print(host['tipo'].upper(), host['ip'], host['puerto'])
" | while read -r nombre ip puerto; do
  if timeout "$ESPERA" bash -c "echo > /dev/tcp/$ip/$puerto" 2>/dev/null; then
    printf '  %-4s arriba  %s:%s\n' "$nombre" "$ip" "$puerto"
  else
    printf '  %-4s caido   %s:%s\n' "$nombre" "$ip" "$puerto"
  fi
done
