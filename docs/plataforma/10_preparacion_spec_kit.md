# 10 — Preparación para Spec Kit

## Principios de ingeniería (constitución candidata)
1. Arquitectura modular DATA / PROCESO / VIZ / IA.
2. Responsabilidad única: el motor calcula; el LLM explica.
3. Contratos MQTT/HTTP/JSON verificables.
4. Integridad de datasets: sin escritura desde simulación.
5. Seguridad: no secretos en git; puertos MQTT/Ollama no expuestos a LAN por defecto.
6. Trazabilidad: magnitudes con unidad y origen.
7. Pruebas automatizadas antes de integrar.
8. Revisión humana de cambios de física.
9. Documentar decisiones (ADR).
10. Prohibido introducir cálculos físicos no autorizados vía LLM o código generado sin catálogo.

## Módulos candidatos a especificación (no monolito)
| Módulo | Por qué |
|---|---|
| Asistente — resolución de anáforas | Usabilidad, bajo riesgo físico |
| Presentación de unidades | Contrato de salida |
| Simulador valores_en_uso | Ya acotado |
| Observabilidad chat | Operación |
| **No prioritario:** reescritura de fórmulas BES | Riesgo científico/operacional |

## Metodología de adopción
Constitución → `/speckit.specify` (o equivalente instalado) por módulo → aclarar → plan → tasks → implementación en rama → pruebas listadas en §06 → PR a `main`.

Los nombres exactos de slash-commands se verifican tras `specify init` (Fase 3).
