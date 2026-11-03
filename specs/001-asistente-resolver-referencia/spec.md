# Feature Specification: Resolver referencias numéricas de pozo en el asistente

**Feature Branch**: `001-asistente-resolver-referencia`

**Created**: 2026-11-03

**Status**: Draft (piloto Spec Kit — sin implementación de código en esta adopción)

**Input**: Permitir que frases como «compara caudales 084 y 301» resuelvan `QF-084` y `QF-301` cuando el dataset activo sea BES-jun, sin inventar pozos ni alterar el motor físico.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Comparar dos pozos por sufijo numérico (Priority: P1)

El operador, con dataset BES-jun (o alcance Todos que incluya BES), escribe «compara solo caudales 084 y 301». El sistema interpreta `QF-084` y `QF-301`, obtiene magnitudes del motor y responde sin pedir «de qué pozo se trata» si la resolución es unívoca.

**Why this priority**: Cierra el residual de holdout H004/H014 sin tocar física.

**Independent Test**: Consulta unitaria a `interpretar` + `responder` con mock Ollama; asertar intención `comparar` y pozos `QF-084`,`QF-301`.

**Acceptance Scenarios**:

1. **Given** dataset BES-jun y pozos conocidos QF-084/QF-301, **When** consulta «compara caudales 084 y 301», **Then** decisión incluye ambos pozos y no responde solo con pedido de pozo.
2. **Given** texto «084» ambiguo (varios candidatos), **When** no hay desambiguación posible, **Then** se aclara sin inventar magnitudes.

### User Story 2 - No resolver fuera de inventario (Priority: P2)

**Why this priority**: Seguridad de identidad.

**Independent Test**: «compara 999 y 998» → pozo desconocido / aclarar.

**Acceptance Scenarios**:

1. **Given** sufijos sin pozo HUC, **When** se interpreta, **Then** no se inventan IDs ni se llama motor con códigos falsos.

### User Story 3 - No aplicar a RB por defecto (Priority: P3)

**Why this priority**: Evitar cruce de datasets.

**Independent Test**: Con alcance solo RB-1521, «084» no debe mapear a QF-084 silenciosamente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Resolver sufijos numéricos de 3 dígitos a `QF-XXX` solo contra inventario conocido y alcance activo.
- **FR-002**: No modificar motores ni fórmulas.
- **FR-003**: Conservar comportamiento actual cuando ya hay códigos `QF-`/`RB-` explícitos.
- **FR-004**: Si la resolución es ambigua o vacía, pedir aclaración (falla segura).

### Key Entities

- Pozo HUC (`pozo_id`), dataset activo, decisión de intención.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Casos holdout tipo H004 pasan en batería de regresión dedicada (≥3 variantes).
- **SC-002**: 0 llamadas a motor con `pozo_id` no inventariado en esos casos.
- **SC-003**: Suites WEB existentes siguen en verde.

## Out of Scope

- Implementación en esta rama de adopción SDD (solo demuestra el flujo Spec Kit).
- Cambios de UI visual.
- Resolución semántica libre tipo «el de la bomba S8000» (futuro).
