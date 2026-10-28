# Decisiones pendientes

Este registro no adelanta la respuesta del responsable del alcance. Una fila se cierra solo cuando esa respuesta queda escrita aquí, con fecha, responsable y efecto en el orden de procesamiento.

## P-14 · Lugar de BES-jun frente a D1

| Campo | Registro |
|---|---|
| Pregunta | ¿El tablero de `asesor-esp` adopta `Copia de FINAL BES-jun.xlsx` como dataset del plan, o `RB-1521-PY-121120.xls` (D1) sigue siendo el primer dataset? |
| Respuesta | Pendiente. No hay respuesta del responsable del alcance. |
| Fecha de la pregunta | 2026-10-17 |
| Fecha de la respuesta | — |
| Responsable | Responsable del alcance. En `asesor-esp/trabajo.md` §10 la columna «Para» de P-14 dice Remitente. No se ha identificado otra persona ni se ha recibido contestación. |
| Efecto en el orden de procesamiento | Hasta que la respuesta esté escrita en esta tabla, el orden del tablero no cambia: primero D1 (`RB-1521-PY-121120.xls`), después D2 (`RB-IA-2191-Data.xlsx`). BES-jun no forma parte de ese tablero y no sustituye a D1. El archivo puede seguir en inventario, lectura y perfil de esta iteración. Sus filas no se mezclan con D1 ni con D2. |

Mientras la respuesta esté vacía, no se añade BES-jun a `asesor-esp/trabajo.md` §4.1 ni se reordena §5.2.

## Puerta de fórmulas

Segunda condición del motor determinístico general. Estado: **no satisfecha**.

| Requisito | Estado | Dónde está la evidencia |
|---|---|---|
| Ecuaciones de los documentos y fórmulas del XLSM trazadas | Borrador. No están reconciliadas. | `docs/trazabilidad_ecuaciones.md`, `logs/notas_agente_dominio.md` |
| Formulación base definida, con unidades, supuestos, dominio de uso y parámetros requeridos | No definida. `docs/decision_modelo_base.md` sigue en borrador. La puerta G1 no está aprobada. | `docs/decision_modelo_base.md` |
| Diferencias y faltantes documentados | Documentados y todavía abiertos. Entre ellos: exponente de Hazen-Williams 4.8566 en BES-jun frente a 4.8655 en el PDF; signo de `J64` en el XLSM frente al dibujo de la misma hoja; BS&W rotulado «%» y usado como fracción; constantes de celda sin definición fuera de la celda; Método B y el observador EKF sin parámetros para calcularlos. | `docs/bloqueos.md`, `docs/trazabilidad_ecuaciones.md` |

## Motor determinístico general

**Estado: BLOQUEADO.** Hacen falta las dos condiciones:

1. P-14 con respuesta, fecha, responsable y efecto escritos en la tabla de arriba.
2. Puerta de fórmulas satisfecha: trazabilidad reconciliada, formulación base definida y diferencias documentadas.

P-14 no impide el análisis aislado del expediente `datasets/en_uso/BES-jun`. Ese análisis no incorpora el archivo al tablero ni cambia el orden oficial.

El motor común para todos los Excel no se construye en esta etapa. El código de `datasets/en_uso/BES-jun/src/` solo transcribe celdas de ese libro y las compara con su caché. No se entrena un modelo, no se genera un pronóstico y ninguna regla queda aprobada.

Cuando P-14 y la puerta de fórmulas estén satisfechas, el estado se actualiza en `trabajo.md`. Hasta entonces no hay motor general.
