# Inicio rápido de HUC

Todos los comandos se ejecutan desde la carpeta `HUC-1.0.0/` del repositorio.
La guía completa está en el [README](README.md).

## Instalación y primer arranque

```bash
cd HUC-1.0.0
./instalar.sh          # CPU
./instalar.sh gpu      # GPU NVIDIA (opcional)
./verificar.sh
```

## Inicio / detención / estado

```bash
./iniciar.sh           # CPU
./iniciar.sh gpu       # GPU NVIDIA
./detener.sh
./estado.sh
```

## Logs

```bash
docker compose logs --tail 100
docker compose logs -f huc-ollama
```

## Fórmulas del motor

```bash
docker compose exec huc-proceso python /app/proceso/formulas.py list
```

## Interfaces

- Visualización y asistente: <http://localhost:8000>
- Simulador (DATA): <http://localhost:8001> — usuario `operador`, clave en `HUC-1.0.0/.env` (`HUC_SIM_CLAVE`).

Desde otro equipo de la red: `http://IP_DEL_PC:8000` (la IP debe figurar en `DJANGO_ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`).
