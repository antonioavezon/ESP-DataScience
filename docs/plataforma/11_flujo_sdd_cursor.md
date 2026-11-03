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
5. Ejecutar pruebas de `docs/plataforma/06_estrategia_pruebas.md`.
6. PR a `main`.

## Piloto demostrado
`specs/001-asistente-resolver-referencia/` contiene spec, plan y tasks consistentes. **No** incluye cambio de código productivo (deliberado).

## Nota sobre `.cursor/`
Las `rules/` previas del proyecto se conservaron. Las skills Spec Kit se versionan para que el clon pueda usar SDD; no incluir secretos en `.cursor/`.
