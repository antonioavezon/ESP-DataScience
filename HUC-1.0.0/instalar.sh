#!/bin/sh
# Instala y arranca HUC 1.0.0 con Docker Compose (perfil CPU por defecto).
# Uso: ./instalar.sh        -> CPU
#      ./instalar.sh gpu    -> GPU NVIDIA (requiere NVIDIA Container Toolkit)
set -eu
cd "$(dirname "$0")"
raiz="$(pwd)"

if ! command -v docker >/dev/null 2>&1; then
  echo "Hace falta Docker (https://docs.docker.com/get-docker/)." >&2
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "Hace falta el plugin Docker Compose v2 ('docker compose')." >&2
  exit 1
fi
if [ "$(uname -m)" != "x86_64" ]; then
  echo "Aviso: HUC 1.0.0 solo se ha probado en Linux x86-64; se continúa con $(uname -m)." >&2
fi
if [ -r /proc/meminfo ]; then
  memoria="$(awk '/MemTotal/ {print $2}' /proc/meminfo)"
  if [ "${memoria:-0}" -lt 8000000 ]; then
    echo "Aviso: hay menos de 8 GiB de memoria; el modelo lingüístico puede ir lento o fallar." >&2
  fi
fi

# Modo desarrollo: si el repositorio completo está al lado, se refresca el espejo codigo/.
# En un clon recién descargado el espejo ya viene versionado y sincronizado.
origen="$(cd "$raiz/.." && pwd)"
if [ -d "$origen/web" ] && [ -d "$origen/proceso" ] && [ -d "$origen/datasets" ]; then
  if command -v rsync >/dev/null 2>&1; then
    mkdir -p "$raiz/codigo"
    rsync -a --delete --exclude '__pycache__' --exclude 'tests' --exclude 'db.sqlite3' --exclude 'staticfiles' --exclude '*.sqlite3' "$origen/web/" "$raiz/codigo/web/"
    rsync -a --delete --exclude '__pycache__' --exclude '*.sqlite3' "$origen/data/" "$raiz/codigo/data/"
    rsync -a --delete --exclude '__pycache__' --exclude 'tests' "$origen/proceso/" "$raiz/codigo/proceso/"
    rsync -a --delete --exclude '__pycache__' "$origen/modelos_ia/" "$raiz/codigo/modelos_ia/"
    rsync -a --delete --exclude '__pycache__' --exclude 'docs' --exclude 'logs' --exclude 'tests' --exclude '*.pdf' --exclude '*.ipynb' --exclude '.pytest_cache' --exclude '.ipynb_checkpoints' "$origen/datasets/" "$raiz/codigo/datasets/"
  else
    echo "rsync no está instalado: se usa el espejo codigo/ versionado en el repositorio." >&2
  fi
fi
if [ ! -d "$raiz/codigo/web" ] || [ ! -d "$raiz/codigo/datasets" ]; then
  echo "No está el código de ejecución en codigo/." >&2
  exit 1
fi

aleatorio() {
  # $1 = bytes. openssl si existe; si no, /dev/urandom.
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -base64 "$1" | tr -d '\n'
  else
    head -c "$1" /dev/urandom | base64 | tr -d '\n'
  fi
}

if [ ! -f "$raiz/.env" ]; then
  proyecto="${COMPOSE_PROJECT_NAME:-huc}"
  puerto_web="${HUC_PUERTO_WEB:-8000}"
  puerto_data="${HUC_PUERTO_DATA:-8001}"
  secreto="$(aleatorio 32)"
  clave="$(aleatorio 18 | tr '+/=' 'xyz')"
  hosts="localhost,127.0.0.1"
  origenes="http://localhost:$puerto_web,http://localhost:$puerto_data,http://127.0.0.1:$puerto_web,http://127.0.0.1:$puerto_data"
  for ip in $(hostname -I 2>/dev/null || true); do
    case "$ip" in
      127.*|172.1[6-9].*|172.2[0-9].*|172.3[0-1].*|*:*) continue ;;
    esac
    hosts="$hosts,$ip"
    origenes="$origenes,http://$ip:$puerto_web,http://$ip:$puerto_data"
  done
  umask 077
  cat > "$raiz/.env" <<EOF
COMPOSE_PROJECT_NAME=$proyecto
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
HUC_BIND=${HUC_BIND:-0.0.0.0}
HUC_PUERTO_WEB=$puerto_web
HUC_PUERTO_DATA=$puerto_data
EOF
  echo "Se creó .env con claves aleatorias. Clave del simulador: ver HUC_SIM_CLAVE en $raiz/.env"
fi

archivos="-f $raiz/compose.yaml"
if [ "${1:-}" = "gpu" ]; then
  archivos="$archivos -f $raiz/compose.gpu.yaml"
fi
# shellcheck disable=SC2086
docker compose $archivos build
# shellcheck disable=SC2086
docker compose $archivos up -d

puerto_web="$(sed -n 's/^HUC_PUERTO_WEB=//p' "$raiz/.env" | tail -n 1)"
puerto_data="$(sed -n 's/^HUC_PUERTO_DATA=//p' "$raiz/.env" | tail -n 1)"
echo "HUC 1.0.0 en marcha."
echo "  Visualización y asistente: http://localhost:${puerto_web:-8000}"
echo "  Simulador (DATA):          http://localhost:${puerto_data:-8001}"
echo "La primera vez Ollama descarga el modelo (~2,5 GB). Estado: ./verificar.sh"
