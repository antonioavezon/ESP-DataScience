# Documentación de plataforma HUC

Índice de la documentación técnica alineada con el código en `main` (actualizar SHA tras cada consolidación).

| Doc | Contenido |
|---|---|
| [01 Contexto y alcance](01_contexto_alcance.md) | Objetivos, actores, límites |
| [02 Arquitectura técnica](02_arquitectura_tecnica.md) | Componentes y despliegue |
| [03 Flujos operacionales](03_flujos_operacionales.md) | Datos, MQTT, asistente |
| [04 Contratos e interfaces](04_contratos_interfaces.md) | HTTP, MQTT, JSON |
| [05 Reglas funcionales](05_reglas_funcionales.md) | Invariantes y responsabilidades |
| [06 Estrategia de pruebas](06_estrategia_pruebas.md) | Suites y brechas |
| [07 Despliegue y operación](07_despliegue_operacion.md) | Compose, arranque, recuperación |
| [08 ADR](adr/) | Decisiones arquitectónicas |
| [09 Glosario](09_glosario.md) | Términos |
| [10 Spec Kit](10_preparacion_spec_kit.md) | Adopción SDD |
| [11 Flujo SDD Cursor](11_flujo_sdd_cursor.md) | Skills instaladas y procedimiento |
| [12 Integración continua](12_integracion_continua.md) | GitHub Actions, gates, límites |
| [Matriz de trazabilidad](matriz_trazabilidad.md) | Requisito→evidencia→prueba |
| [Matriz de pruebas CI](matriz_pruebas_ci.md) | Suites A/B/C y línea base |

Documentación histórica de estudio (ecuaciones, bloqueos, hoja de ruta antigua) permanece en `docs/*.md` de la raíz de `docs/` y no se sustituye aquí.

**Hecho vs pendiente:** donde el código y un requisito divergen, se marca explícitamente.
