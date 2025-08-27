#!/usr/bin/env bash
set -euo pipefail

#this script rund automatically on first db initialisation if present in /docker-entrypoint-initdb.d
if [ -f /docker-entrypoint-initdb.d/dvdrental.tar ]; then
  echo "-> restoring dvdrental from tar ..."
  pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" /docker-entrypoint-initdb.d/dvdrental.tar
  echo "-> restore complete!"
else
  echo "dvdrental.tar not found; starting with empty dvdrental database!"
fi