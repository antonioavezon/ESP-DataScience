#!/bin/sh
# Comprueba que HUC está operativo: contenedores, modelo Ollama, HTTP y un resultado determinístico.
# Uso: ./verificar.sh      (código de salida 0 si todo está bien)
set -u
cd "$(dirname "$0")"
dc() { docker compose -f compose.yaml "$@"; }
fallos=0

echo "== Contenedores"
dc ps --format 'table {{.Service}}\t{{.Status}}'
for servicio in huc-mqtt huc-ollama huc-proceso huc-ia huc-visualizacion huc-data; do
  estado="$(dc ps --format '{{.Service}} {{.Health}}' 2>/dev/null | awk -v s="$servicio" '$1==s {print $2}')"
  if [ "$estado" != "healthy" ]; then
    echo "  [PENDIENTE] $servicio: ${estado:-no iniciado}"
    fallos=$((fallos + 1))
  fi
done

echo "== Modelo lingüístico"
if dc exec -T huc-ollama sh -c 'ollama list | grep -q "$OLLAMA_MODEL"' 2>/dev/null; then
  dc exec -T huc-ollama sh -c 'echo "  [OK] $OLLAMA_MODEL descargado"'
else
  echo "  [PENDIENTE] el modelo aún no está descargado. Ver: docker compose logs -f huc-ollama"
  fallos=$((fallos + 1))
fi

echo "== HTTP y motor determinístico"
if dc exec -T huc-visualizacion python - <<'EOF'
import json, sys, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={"Host": "localhost"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, r.read()

ok = True
for url in ("http://127.0.0.1:8000/", "http://127.0.0.1:8000/asistente/", "http://huc-data:8001/"):
    try:
        estado, _ = get(url)
        print(f"  [OK] {url} -> {estado}")
    except Exception as e:
        print(f"  [FALLA] {url} -> {e}")
        ok = False
try:
    _, cuerpo = get("http://127.0.0.1:8000/api/consola/pozos/QF-084/resultado/")
    d = json.loads(cuerpo)
    pip = d["resultados"]["pip_ft"]
    print(f"  [OK] QF-084 ({d['dataset_id']}): estado {d['estado']['codigo']}, PIP {pip['valor_visible']} {pip['unidad']}")
except Exception as e:
    print(f"  [FALLA] resultado determinístico QF-084 -> {e}")
    ok = False
sys.exit(0 if ok else 1)
EOF
then :; else fallos=$((fallos + 1)); fi

if [ "$fallos" -eq 0 ]; then
  echo "HUC operativo."
else
  echo "Hay $fallos comprobación(es) pendiente(s). En el primer arranque espere a que termine la descarga del modelo."
  exit 1
fi
