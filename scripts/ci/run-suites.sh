#!/usr/bin/env bash
# Ejecuta suites de categoría A de HUC de forma reproducible (local o CI).
# Uso: scripts/ci/run-suites.sh [all|web|motores|servicios|compose|syntax]
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$RAIZ"
PY="${PYTHON:-python}"

suite="${1:-all}"

run_web() {
  echo "::group::WEB (Django)"
  (cd "$RAIZ/web" && "$PY" manage.py test --verbosity=1)
  echo "::endgroup::"
}

run_motores() {
  echo "::group::BES-jun"
  (cd "$RAIZ/datasets/en_uso/BES-jun" && "$PY" -m pytest -q --tb=short)
  echo "::endgroup::"
  echo "::group::RB-1521"
  (cd "$RAIZ/datasets/en_uso/RB-1521" && "$PY" -m pytest -q --tb=short)
  echo "::endgroup::"
  echo "::group::RB-IA-2191"
  (cd "$RAIZ/datasets/en_uso/RB-IA-2191" && "$PY" -m pytest -q --tb=short)
  echo "::endgroup::"
}

run_servicios() {
  echo "::group::PROCESO"
  "$PY" -m pytest "$RAIZ/proceso/tests" -q --tb=short
  echo "::endgroup::"
  echo "::group::DATA"
  PYTHONPATH="$RAIZ" "$PY" -m pytest "$RAIZ/data/tests" -q --tb=short
  echo "::endgroup::"
  echo "::group::MODELOS_IA"
  "$PY" -m pytest "$RAIZ/modelos_ia/tests" -q --tb=short
  echo "::endgroup::"
}

run_compose() {
  echo "::group::Compose config"
  if ! command -v docker >/dev/null 2>&1; then
    echo "docker no disponible; omitiendo validación compose" >&2
    return 0
  fi
  (cd "$RAIZ/HUC-1.0.0" && docker compose --env-file .env.example -f compose.yaml config -q)
  echo "::endgroup::"
}

run_syntax() {
  echo "::group::compileall módulos núcleo"
  "$PY" -m compileall -q \
    "$RAIZ/web" \
    "$RAIZ/proceso" \
    "$RAIZ/data" \
    "$RAIZ/modelos_ia" \
    "$RAIZ/datasets/en_uso/BES-jun/src" \
    "$RAIZ/datasets/en_uso/RB-1521" \
    "$RAIZ/datasets/en_uso/RB-IA-2191"
  echo "::endgroup::"
}

case "$suite" in
  all)
    run_syntax
    run_web
    run_servicios
    run_motores
    run_compose
    ;;
  web) run_web ;;
  motores) run_motores ;;
  servicios) run_servicios ;;
  compose) run_compose ;;
  syntax) run_syntax ;;
  *)
    echo "Suite desconocida: $suite" >&2
    echo "Uso: $0 [all|web|motores|servicios|compose|syntax]" >&2
    exit 2
    ;;
esac

echo "OK suite=$suite"
