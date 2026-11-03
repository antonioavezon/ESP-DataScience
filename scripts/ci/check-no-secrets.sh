#!/usr/bin/env bash
# Controles básicos anti-secretos en el árbol versionado (working tree / checkout CI).
# No sustituye rotación de credenciales ni escáneres históricos profundos.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$RAIZ"

fallos=0
SELF="scripts/ci/check-no-secrets.sh"

echo "::group::Archivos sensibles no deben estar rastreados"
while IFS= read -r f; do
  case "$f" in
    *.env.example|*/.env.example) continue ;;
  esac
  base="$(basename "$f")"
  if [[ "$base" == ".env" || "$base" == "id_rsa" || "$base" == "id_ed25519" ]]; then
    echo "ERROR: archivo sensible rastreado: $f" >&2
    fallos=$((fallos + 1))
  fi
  case "$f" in
    *.pem)
      echo "ERROR: archivo sensible rastreado: $f" >&2
      fallos=$((fallos + 1))
      ;;
  esac
done < <(git ls-files)
echo "::endgroup::"

echo "::group::Patrones de alto riesgo en archivos rastreados"
# Patrones ensamblados para que este propio script no dispare falsos positivos.
p1="BEGIN OPENSSH PRIVATE ""KEY"
p2="BEGIN RSA PRIVATE ""KEY"
p3="AKIA""[0-9A-Z]{16}"
p4="ghp_""[A-Za-z0-9]{36}"
p5="github_pat_""[A-Za-z0-9_]{20,}"
patrones=("$p1" "$p2" "$p3" "$p4" "$p5")

mapfile -t archivos < <(git ls-files '*.py' '*.yml' '*.yaml' '*.json' '*.md' '*.txt' '*.sh' '*.toml' '*.ini' '*.cfg' 2>/dev/null || true)
for f in "${archivos[@]}"; do
  [[ -f "$f" ]] || continue
  [[ "$f" == "$SELF" ]] && continue
  case "$f" in
    archive/*) continue ;;
  esac
  for p in "${patrones[@]}"; do
    if grep -EIq -- "$p" "$f" 2>/dev/null; then
      echo "ERROR: patrón sensible detectado en $f" >&2
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
