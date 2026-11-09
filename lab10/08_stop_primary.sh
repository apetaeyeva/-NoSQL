#!/usr/bin/env bash
# Штатная остановка ТОЛЬКО текущего primary учебного стенда. Печатает t0.
set -euo pipefail
URI="mongodb://127.0.0.1:27101,127.0.0.1:27102,127.0.0.1:27103/?replicaSet=rsLab10"
P=$(mongosh "$URI" --quiet --eval 'print(db.hello().primary.split(":")[1])')
case "$P" in 27101|27102|27103) ;; *) echo "не узел стенда: $P"; exit 1;; esac
echo "primary: $P"; date -u +"t0(stop command) = %Y-%m-%dT%H:%M:%S.%3NZ"
mongosh --port "$P" admin --quiet --eval 'try{db.shutdownServer()}catch(e){}'
