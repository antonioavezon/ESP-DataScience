# Arquitectura funcional

Estado a 2026-10-20. Distingue lo que ya corre de lo que solo está previsto.

## Componentes

| Componente | Dónde está | Qué hace hoy |
|---|---|---|
| Repositorio de datasets | `datasets/en_espera`, `en_uso`, `procesadas` | BES-jun está en `en_uso`. RB-1521 y RB-IA-2191 están en `en_espera` y no se procesan. `procesadas` sigue vacío. |
| Ingesta y calidad | `datasets/en_uso/BES-jun/src/ingesta` y los cuadernos 00 y 01 | Lee BES-jun por rótulo, sin guardar el Excel. |
| Catálogo de pozos | `integracion/pozos.json` | Cinco pozos de este archivo, identidad provisional. No hay catálogo central de todos los datasets. |
| Modelos físicos | `src/modelo_deterministico` | Tres modelos de transcripción de la hoja (`transcripcion-1`). No son el motor SI de `asesor-esp`. |
| Motor de evaluación | `src/evaluacion/motor.py` | `evaluar(dataset_id, pozo_id, entradas, fecha_referencia)` sobre BES-jun. Sin red y sin modelo de lenguaje. |
| Reglas | `src/reglas` y `integracion/reglas.json` | RC-BES-01 a 04. Ninguna aprobada. RC-BES-04 no evaluable. |
| Aplicación gráfica | `asesor-esp/` | Esqueleto (config, docs, reglas de agentes). No consume todavía el paquete. |
| Modelo de lenguaje | `integracion/capa_linguistica.md` | Contrato escrito. No hay cliente ni llamada simulada. |
| Trazabilidad | cuadernos, `docs/`, pruebas, huellas | La ficha, el informe y el paquete se regeneran desde código. |

## Dependencias

La aplicación futura lee `integracion/` y llama al motor. El motor lee el libro a través de `ingesta` y calcula con `modelo_deterministico`. Las reglas no duplican esas ecuaciones: llaman a `comparar_caudal_con_limites`. El modelo de lenguaje, cuando exista, solo recibe el JSON de salida.

## Decisión de frontera

DEC-004: las fórmulas de BES-jun no se copian a `asesor-esp` mientras sigan en reserva y en unidades de la hoja. El paquete de integración es la frontera.
