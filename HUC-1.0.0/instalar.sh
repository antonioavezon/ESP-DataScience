#!/bin/sh
set -eu
cd "$(dirname "$0")"
raiz="$(pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "Hace falta Docker." >&2
  exit 1
fi
docker compose version >/dev/null
if [ "$(uname -m)" != "x86_64" ]; then
  echo "HUC 1.0.0 está preparado para Linux x86-64." >&2
  exit 1
fi
memoria="$(awk '/MemTotal/ {print $2}' /proc/meminfo)"
if [ "${memoria:-0}" -lt 4000000 ]; then
  echo "La memoria total es baja para el modelo lingüístico." >&2
fi

origen="$(cd "$raiz/.." && pwd)"
if [ -d "$origen/web" ] && [ -d "$origen/proceso" ] && [ -d "$origen/datasets" ]; then
  mkdir -p "$raiz/codigo"
  rsync -a --delete --exclude '__pycache__' --exclude 'tests' --exclude 'db.sqlite3' --exclude 'staticfiles' --exclude '*.sqlite3' "$origen/web/" "$raiz/codigo/web/"
  rsync -a --delete --exclude '__pycache__' --exclude '*.sqlite3' "$origen/data/" "$raiz/codigo/data/"
  rsync -a --delete --exclude '__pycache__' --exclude 'tests' "$origen/proceso/" "$raiz/codigo/proceso/"
  rsync -a --delete --exclude '__pycache__' "$origen/modelos_ia/" "$raiz/codigo/modelos_ia/"
  rsync -a --delete --exclude '__pycache__' --exclude 'docs' --exclude 'logs' --exclude 'tests' --exclude '*.pdf' --exclude '*.ipynb' "$origen/datasets/" "$raiz/codigo/datasets/"
  find "$raiz/codigo" -name '*.md' ! -name 'dataset.md' -delete
fi
if [ ! -d "$raiz/codigo/web" ] || [ ! -d "$raiz/codigo/datasets" ]; then
  echo "No está el código de ejecución en codigo/." >&2
  exit 1
fi

if [ ! -f "$raiz/.env" ]; then
  secreto="$(openssl rand -base64 32 | tr -d '\n')"
  clave="$(openssl rand -base64 18 | tr -d '\n')"
  hosts="localhost,127.0.0.1"
  origenes="http://localhost:8000,http://localhost:8001,http://127.0.0.1:8000,http://127.0.0.1:8001"
  for ip in $(hostname -I); do
    case "$ip" in
      127.*|172.1[6-9].*|172.2[0-9].*|172.3[0-1].*) continue ;;
    esac
    hosts="$hosts,$ip"
    origenes="$origenes,http://$ip:8000,http://$ip:8001"
  done
  cat > "$raiz/.env" <<EOF
COMPOSE_PROJECT_NAME=huc
HUC_VERSION=1.0.0
DJANGO_SECRET_KEY=$secreto
DJANGO_ALLOWED_HOSTS=$hosts
CSRF_TRUSTED_ORIGINS=$origenes
HUC_SIM_USUARIO=operador
HUC_SIM_CLAVE=$clave
OLLAMA_MODEL=qwen3:4b-instruct-2507-q4_K_M
HUC_MQTT_HOST=huc-mqtt
HUC_MQTT_PORT=1883
HUC_IA_URL=http://huc-ia:8002
OLLAMA_BASE_URL=http://huc-ollama:11434
EOF
  echo "Clave del simulador escrita en .env."
fi

docker compose -f "$raiz/compose.yaml" build
docker compose -f "$raiz/compose.yaml" up -d
echo "HUC 1.0.0 en marcha."
hostname -I | tr ' ' '\n' | while read -r ip; do
  case "$ip" in
    ""|127.*|172.1[6-9].*|172.2[0-9].*|172.3[0-1].*) continue ;;
  esac
  echo "http://$ip:8000"
  echo "http://$ip:8001"
done
