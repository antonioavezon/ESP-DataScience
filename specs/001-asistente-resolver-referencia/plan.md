# Implementation Plan: Resolver referencias numéricas de pozo

**Branch**: `001-asistente-resolver-referencia` | **Date**: 2026-11-03 | **Spec**: [spec.md](./spec.md)

**Note**: En la adopción Spec Kit este plan es el artefacto de demostración. La implementación de código queda para una rama futura tras PR de SDD.

## Summary
Extender `chat_intencion` (y, si hace falta, el orquestador) para mapear sufijos `NNN` → `QF-NNN` dentro del inventario y alcance activos, sin tocar motores.

## Technical Context
- **Language/Version**: Python 3.14 / Django 6
- **Primary files**: `web/services/chat_intencion.py`, tests en `web/tests/`
- **Testing**: `manage.py test` + casos holdout sintéticos
- **Constraints**: Constitución HUC INV-1/INV-2; no cambiar fórmulas

## Constitution Check
| Principio | Cumple |
|---|---|
| LLM no calcula | Sí — solo resuelve identidad |
| Datasets intactos | Sí |
| Pruebas | Obligatorio antes de merge de implementación |

## Project Structure (touched later)
```
web/services/chat_intencion.py
web/tests/test_pozo_referencia_numerica.py  # nuevo (futuro)
```

## Phases
1. Diseño de reglas de resolución y ambigüedad.
2. Tests que fallen (rojo) para H004-like.
3. Implementación mínima.
4. Regresión WEB completa.
5. PR a `main`.
