# 11 — Flujo Spec-Driven Development en Cursor

## Instalación verificada
- Spec Kit CLI **1.2.5** (`specify version`)
- Integración: `cursor-agent` → skills en `.cursor/skills/speckit-*`
- Infraestructura compartida: `.specify/`
- Constitución: `.specify/memory/constitution.md`

## Comandos / skills
| Skill | Uso |
|---|---|
| `/speckit-constitution` | Principios del proyecto |
| `/speckit-specify` | Especificación |
| `/speckit-clarify` | Ambigüedades |
| `/speckit-plan` | Plan técnico |
| `/speckit-tasks` | Desglose |
| `/speckit-analyze` | Consistencia |
| `/speckit-implement` | Implementación |
| `/speckit-checklist` | Listas de calidad |

## Procedimiento para funcionalidades nuevas
1. Partir de `main` actualizado.
2. Crear feature con `.specify/scripts/bash/create-new-feature.sh` o `/speckit-specify`.
3. Completar spec → clarify → plan → tasks.
4. Implementar solo lo listado; no alterar física sin ADR.
5. Ejecutar pruebas locales: `./scripts/ci/run-suites.sh` (o el subconjunto nombrado en la spec).
6. Abrir PR a `main` con convención de rama `NNN-nombre-corto` o `infra/...` / `docs/...`.
7. Esperar GitHub Actions (`CI HUC`, `Seguridad HUC`) — ver `12_integracion_continua.md`.
8. Revisión humana y merge sin force-push.

### Quién hace qué
| Paso | Cursor / agente | GitHub Actions | Humano |
|---|---|---|---|
| Spec/plan/tasks | Sí | No | Aprueba alcance |
| Implementación | Sí | No | Supervisa física/contratos |
| Pruebas locales | Sí | No | — |
| CI remota | No | Sí | Interpreta fallos |
| Merge a main | No | Checks | Autoriza merge |

### Convención de trazabilidad
- Rama / PR: mencionar `specs/NNN-...` en descripción.
- Commits funcionales: referencia al ID de requisito (p. ej. `FR-001`) cuando exista.

## Piloto demostrado
`specs/001-asistente-resolver-referencia/` contiene spec, plan y tasks consistentes. **No** incluye cambio de código productivo (deliberado).

## Nota sobre `.cursor/`
Las `rules/` previas del proyecto se conservaron. Las skills Spec Kit se versionan para que el clon pueda usar SDD; no incluir secretos en `.cursor/`.
