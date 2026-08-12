#!/usr/bin/env bash
# Levanta varios nodos en la misma maquina, cada uno con su bitacora.
#
#   bash scripts/levantar_topologia.sh           # los nueve nodos
#   bash scripts/levantar_topologia.sh A I D     # solo algunos
#
# Se detiene todo con Ctrl+C.

set -uo pipefail
cd "$(dirname "$0")/.."

NODOS=("$@")
if [ ${#NODOS[@]} -eq 0 ]; then
  NODOS=(A B C D E F G H I)
fi

mkdir -p bitacoras
PIDS=()

detener() {
  echo
  echo "deteniendo los nodos..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null
  done
  wait 2>/dev/null
  exit 0
}
trap detener INT TERM

for id in "${NODOS[@]}"; do
  python3 nodo.py --id "$id" > "bitacoras/$id.log" 2>&1 &
  PIDS+=("$!")
  echo "nodo $id levantado (pid $!) -> bitacoras/$id.log"
done

echo
echo "Ctrl+C para detener. Para seguir un nodo: tail -f bitacoras/A.log"
wait
