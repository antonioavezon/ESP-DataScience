#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ "${1:-}" = "gpu" ]; then
  docker compose -f compose.yaml -f compose.gpu.yaml up -d
else
  docker compose -f compose.yaml up -d
fi
