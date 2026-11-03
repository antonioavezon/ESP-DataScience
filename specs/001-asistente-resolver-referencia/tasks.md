# Tasks: Resolver referencias numéricas de pozo

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Phase 0 — Piloto SDD (esta adopción)
- [x] Constitución HUC en `.specify/memory/constitution.md`
- [x] Spec Kit init (`cursor-agent`)
- [x] Spec/plan/tasks creados bajo `specs/001-...`
- [ ] Implementación de código (aplazada — fuera del piloto)

## Phase 1 — Implementación futura (no ejecutar aquí)
- [ ] T001 Escribir tests `test_pozo_referencia_numerica.py` (H004-like, ambiguo, RB no mapea)
- [ ] T002 Extender `_pozos_nombrados` / resolver sufijos en `chat_intencion.py`
- [ ] T003 Asegurar que `comparar` recibe ≥2 pozos tras resolución
- [ ] T004 Ejecutar suite WEB completa
- [ ] T005 Actualizar matriz de trazabilidad y cerrar PR

## Consistency notes
- Spec FR-001 ↔ Plan phase 1 ↔ T002
- Spec SC-001 ↔ T001/T004
- Out of scope de implementación confirmado para esta rama documental/SDD
