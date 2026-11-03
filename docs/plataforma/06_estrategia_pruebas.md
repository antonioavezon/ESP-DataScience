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

## CI (GitHub Actions)
Ver `12_integracion_continua.md` y `matriz_pruebas_ci.md`.
- Categoría A: workflows `ci.yml` + `security.yml`.
- Categoría C (Ollama real, E2E MQTT, holdouts locales): `especializadas.yml` / ejecución local.
- Orquestación: `scripts/ci/run-suites.sh`.

## Brechas
- Obligatoriedad de status checks en merge: depende de branch protection (configuración administrativa).
- E2E MQTT de simulación no forma parte del gate de cada PR.
- Holdout lingüístico 40 casos no está en el árbol Git (vive en auditorías locales).

## Criterio de aceptación para cambios SDD
Toda especificación nueva debe nombrar suites a ejecutar y datos de prueba seguros (sin datasets destructivos). El PR debe mostrar los workflows aplicables en verde antes del merge.
