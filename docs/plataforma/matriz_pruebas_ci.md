# Matriz de pruebas para CI (línea base 2026-11-03)

Medición local con `/home/antonio/projects/HUC/.venv` (Python 3.14.8). Logs en `/home/antonio/auditorias/HUC/ci-baseline-20261103/`.

| ID | Módulo | Ubicación | Framework | Comando | Deps | Datos | Duración | Resultado | CI | Notas |
|---|---|---|---|---|---|---|---|---|---|---|
| T-WEB | WEB | `web/tests` | Django | `scripts/ci/run-suites.sh web` | requirements-ci | BD test Django; Ollama mock | 63.39 s | Aprobado (123) | A — Sí | |
| T-BES | BES | `datasets/en_uso/BES-jun/tests` | pytest | `… motores` | pandas/numpy/openpyxl/jsonschema/matplotlib | Excel BES en expediente | 21.21 s | Aprobado (182) | A — Sí | No escribe original |
| T-RB1521 | RB | `datasets/en_uso/RB-1521/tests` | pytest | `… motores` | requirements-ci | dataset RB | 1.02 s | Aprobado (6) | A — Sí | |
| T-RBIA | RB-IA | `datasets/en_uso/RB-IA-2191/tests` | pytest | `… motores` | requirements-ci | dataset RB-IA | 1.38 s | Aprobado (6) | A — Sí | |
| T-PROC | PROCESO | `proceso/tests` | pytest/unittest | `… servicios` | stdlib + data | hash Excel BES | 1.13 s | Aprobado (2) | A — Sí | |
| T-DATA | DATA | `data/tests` | pytest | `… servicios` | PYTHONPATH raíz | memoria `valores_en_uso` | 1.04 s | Aprobado (3) | A — Sí | |
| T-IA | MODELOS IA | `modelos_ia/tests` | unittest/pytest | `… servicios` | httpx/mock | sin Ollama real | 1.65 s | Aprobado (5) | A — Sí | |
| T-COMPOSE | Ops | `HUC-1.0.0/compose.yaml` | docker compose | `… compose` | Docker CLI | `.env.example` | 0.92 s | Aprobado | A — Sí | No levanta servicios |
| T-SEC-ENV | Sec | scripts | bash | `check-no-secrets.sh` | git | árbol rastreado | <2 s | Aprobado local | A — Sí | |
| T-SEC-AUDIT | Sec | requirements-ci | pip-audit | `pip-audit -r requirements-ci.txt` | red | — | ~20 s | Sin CVEs conocidas | A — Sí | |
| T-ARCH | Archive | `archive/.../tests` | pytest | — | lab | — | — | No ejecutado en CI | C — No | Laboratorio histórico |
| T-DUP | Espejo | `HUC-1.0.0/codigo/**/tests` | — | — | — | — | — | Excluido | — | Duplicado de raíz |
| T-MQTT-E2E | Integración | stack Compose | manual | compose up + flujo | Mosquitto | simulación | — | No en gate PR | B/C | |
| T-OLLAMA | Lingüístico | holdouts auditorías | manual | — | Ollama+modelo | fuera de Git | — | No en gate PR | C | |

## Distribución de workflows
- `ci.yml` → T-WEB, T-BES, T-RB*, T-PROC, T-DATA, T-IA, T-COMPOSE, compileall
- `security.yml` → T-SEC-*
- `especializadas.yml` → documentación T-MQTT-E2E / T-OLLAMA
