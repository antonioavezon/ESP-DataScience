#!/usr/bin/env bash
# Controles básicos anti-secretos en el árbol versionado (working tree / checkout CI).
# No sustituye rotación de credenciales ni escáneres históricos profundos.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$RAIZ"

fallos=0

echo "::group::Archivos sensibles no deben estar rastreados"
prohibidos=(
  '.env'
  'HUC-1.0.0/.env'
  'id_rsa'
  'id_ed25519'
  '*.pem'
)
while IFS= read -r f; do
  case "$f" in
    *.env.example|*/.env.example) continue ;;
  esac
  base="$(basename "$f")"
  if [[ "$base" == ".env" || "$base" == "id_rsa" || "$base" == "id_ed25519" || "$f" == *.pem ]]; then
    echo "ERROR: archivo sensible rastreado: $f" >&2
    fallos=$((fallos + 1))
  fi
done < <(git ls-files)
echo "::endgroup::"

echo "::group::Patrones de alto riesgo en archivos rastreados"
# Escaneo acotado: evita falsos positivos en PDFs/binarios.
mapfile -t archivos < <(git ls-files '*.py' '*.yml' '*.yaml' '*.json' '*.md' '*.txt' '*.sh' '*.env*' '*.toml' '*.ini' '*.cfg' 2>/dev/null || true)
patrones=(
  'BEGIN OPENSSH PRIVATE KEY'
  'BEGIN RSA PRIVATE KEY'
  'AKIA[0-9A-Z]{16}'
  'ghp_[A-Za-z0-9]{36}'
  'github_pat_[A-Za-z0-9_]{20,}'
)
for f in "${archivos[@]}"; do
  [[ -f "$f" ]] || continue
  # Excluir documentación de ejemplo / archive lab si solo menciona patrones
  case "$f" in
    archive/*) continue ;;
  esac
  for p in "${patrones[@]}"; do
    if grep -EIq -- "$p" "$f" 2>/dev/null; then
      echo "ERROR: patrón sensible '$p' en $f" >&2
      fallos=$((fallos + 1))
    fi
  done
done
echo "::endgroup::"

if [[ "$fallos" -gt 0 ]]; then
  echo "Hallazgos de secretos: $fallos" >&2
  exit 1
fi
echo "OK check-no-secrets"
