# 07 — Despliegue y operación

## Arranque (fuente: `inicio.md`)
```bash
cd HUC-1.0.0
./iniciar.sh          # CPU
./iniciar.sh gpu      # GPU
./estado.sh
./detener.sh
```

## Servicios Compose
`huc-mqtt`, `huc-ollama`, `huc-proceso`, `huc-ia`, `huc-data` (:8001), `huc-visualizacion` (:8000).  
Override GPU: `compose.gpu.yaml`.

## Configuración
Copiar/ajustar `HUC-1.0.0/.env` desde `.env.example` (no commitear secretos).  
Tras cambios de código fuente: `instalar.sh` sincroniza `codigo/` y reconstruye imágenes.

## Recuperación
- `docker compose ps` / logs.
- Restaurar pozo en simulador para volver a hoja.
- Ollama: comprobar `OLLAMA_MODEL` y `/api/tags`.

## Observabilidad
Logs JSON de contenedores; bitácora chat (`huc.chat`); incidentes BES locales **ignorados por git** (`**/logs/incidentes.jsonl`).
