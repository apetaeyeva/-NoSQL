#!/usr/bin/env bash
# Запуск (или перезапуск) узла(ов) учебного Replica Set. Только 127.0.0.1.
# Использование: ./01_start_nodes.sh          -> запустить все три
#                ./01_start_nodes.sh 1        -> запустить только rs1 (возврат узла)
set -euo pipefail
BASE="$(pwd)/data"
start() {
  local n=$1 port=$((27100 + $1))
  mkdir -p "$BASE/rs$n"
  mongod --replSet rsLab10 --port "$port" --dbpath "$BASE/rs$n" --bind_ip 127.0.0.1 \
         --fork --logpath "$BASE/rs$n/mongod.log" --pidfilepath "$BASE/rs$n/mongod.pid"
  echo "rs$n started on $port"
}
if [ $# -eq 1 ]; then start "$1"; else for n in 1 2 3; do start "$n"; done; fi
