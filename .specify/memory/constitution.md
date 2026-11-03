# Constitución de HUC

## Core Principles

### I. Separación determinístico / lingüístico
El motor físico calcula. El modelo lingüístico comprende, consulta, interpreta y explica resultados ya calculados. La web presenta. El LLM no inventa fórmulas, no sustituye magnitudes ni autoriza maniobras.

### II. Arquitectura modular
DATA, PROCESO, VISUALIZACIÓN y MODELOS IA mantienen responsabilidades explícitas y contratos verificables (HTTP, MQTT, JSON). Los cambios respetan los límites de módulo documentados en `docs/plataforma/`.

### III. Integridad de datasets
La simulación no escribe datasets originales ni persiste valores simulados como reales. Debe existir camino de retorno a la base del expediente (`valores_en_uso` / restaurar).

### IV. Contratos verificables
Toda integración nueva declara entradas/salidas, unidades e identificadores (dataset, pozo, escenario). Los resultados tipificados conservan `valor`, unidad y nombre semántico.

### V. Pruebas antes de integrar
Los cambios incluyen o actualizan pruebas automatizadas relevantes (WEB, motores, DATA, PROCESO, IA). No se integra a `main` con fallas críticas nuevas sin justificación documentada. Los cambios deben pasar los workflows de GitHub Actions aplicables (`CI HUC`, `Seguridad HUC`) cuando estén disponibles; la evidencia de CI forma parte de la aceptación junto a las pruebas locales.

### VI. Seguridad y secretos
No versionar `.env` reales, claves ni tokens. No exponer MQTT/Ollama a la LAN salvo decisión explícita. No publicar datos operacionales sensibles.

### VII. Simplicidad y revisión humana
Preferir el cambio mínimo que cumpla la especificación. Cambios de fórmulas físicas o reglas determinísticas requieren revisión humana explícita y no se delegan al LLM.

## Restricciones de dominio
- No afirmar validación científica u operacional no demostrada (p. ej. RC-BES siguen pendientes).
- Identidades hoja↔código provisionales en BES deben declararse en specs que las toquen.
- Specs deben ser por módulo/capacidad, no monolitos de todo HUC.

## Flujo de desarrollo (SDD)
1. Constitución (este documento).
2. Especificación (`/speckit-specify`).
3. Aclaración (`/speckit-clarify`) si hay ambigüedad.
4. Plan (`/speckit-plan`).
5. Tareas (`/speckit-tasks`).
6. Análisis opcional (`/speckit-analyze`).
7. Implementación controlada (`/speckit-implement`) en rama.
8. Pruebas listadas en la spec/plan (local + `scripts/ci/run-suites.sh`).
9. Pull Request → GitHub Actions → revisión humana → merge a `main`.

## Governance
Esta constitución prima sobre hábitos ad hoc del agente. Enmiendas requieren ADR en `docs/plataforma/adr/` y actualización de este archivo. Los PRs deben poder trazarse a una spec cuando el cambio sea funcional. La infraestructura de CI se documenta en `docs/plataforma/12_integracion_continua.md`.

**Version**: 1.1.0 | **Ratified**: 2026-11-03 | **Last Amended**: 2026-11-03 (CI/SDD)
