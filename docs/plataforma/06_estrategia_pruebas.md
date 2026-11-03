# 06 — Estrategia de pruebas

## Suites existentes (ejecutadas en consolidación Fase 1)
| Suite | Ubicación | Resultado Fase 1 |
|---|---|---|
| WEB | `web/` `manage.py test` | 123 OK |
| BES-jun | `datasets/en_uso/BES-jun` pytest | 182 OK |
| RB-1521 | pytest | 6 OK |
| RB-IA-2191 | pytest | 6 OK |
| PROCESO | `proceso/` | 2 OK |
| DATA | `data/tests` con PYTHONPATH | 3 OK |
| MODELOS IA | `modelos_ia/tests` | 5 OK |
| Compose config | `docker compose config` | OK |

## Tipos
- Unitarias/determinísticas de motores y contratos.
- Integración Django del asistente (a menudo con Ollama mock).
- Baterías lingüísticas históricas fuera del repo Git (auditorías locales).

## Escenarios críticos de aceptación
1. PIP/THD/caudal BES coinciden con motor.
2. BWPD/BOPD tipificados en RB.
3. Simulación no escribe dataset.
4. Conceptual no llama motor.
5. Adversarial no inventa fórmula.
6. Comparación no imprime `None` como magnitud.

## Brechas
- CI GitHub Actions: no verificado como pipeline activo en consolidación (gh CLI sin login API).
- E2E MQTT de simulación no re-ejecutado en cada commit.
- Holdout lingüístico 40 casos no está en el árbol Git (vive en auditorías locales).

## Criterio de aceptación para cambios SDD
Toda especificación nueva debe nombrar suites a ejecutar y datos de prueba seguros (sin datasets destructivos).
