#!/usr/bin/env bash
# Backup и восстановление в ОТДЕЛЬНУЮ базу university_restore10 (без --drop).
set -euo pipefail
URI="mongodb://127.0.0.1:27101,127.0.0.1:27102,127.0.0.1:27103/?replicaSet=rsLab10"
rm -rf ./backup_lab10
mongodump --uri="$URI" --db=university_lab10 --out=./backup_lab10
mongorestore --uri="$URI" --nsFrom="university_lab10.*" --nsTo="university_restore10.*" ./backup_lab10/university_lab10
mongosh "$URI" --quiet --eval 'var DBNAME="university_restore10"' --file 06_check_after.js
