# Decisiones

## DEC-001 · Primer dataset de esta iteración

- **Fecha:** 2026-10-17
- **Estado:** registrada para esta iteración. La puerta G1 del plan `trabajo2.md` sigue sin aprobarse.
- **Decisión:** el archivo leído en esta iteración es `Copia de FINAL BES-jun.xlsx`. Esa lectura no lo incorpora al tablero de asesor-esp ni lo pone delante de D1.
- **Copia de trabajo:** `datasets/en_uso/BES-jun/entrada/BES_jun.xlsx`
- **SHA-256:** `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`
- **MD5:** `ba89f317f505f321c496e44ab5046104`
- **Qué no es:** no es `RB-1521-PY-121120.xls` (MD5 `a2dcc88b6b1ee8a82db9fdad29b5affa`) ni `RB-IA-2191-Data.xlsx` (MD5 `8c82a502b1e10d8db9e69b7f6f6918b4`). Esos archivos se conservan para etapas posteriores. Sus filas no entran en este análisis.
- **Relación con el plan:** `trabajo2.md` y `asesor-esp/trabajo.md` son el mismo texto. Allí D1 sigue siendo RB-1521. P-14 pide al responsable del alcance si eso cambia. La respuesta, la fecha, el responsable y el efecto están pendientes en `docs/decisiones_pendientes.md`. Hasta entonces el orden del tablero no se toca.

## DEC-002 · Qué cálculo se transcribe ahora

- **Estado:** borrador. No sustituye la aprobación de `docs/decision_modelo_base.md`.
- **Decisión de trabajo:** implementar solo la cadena que las celdas de BES-jun escriben de forma explícita (fluido, PIP en ft desde la presión de sensor, Hazen-Williams de la hoja, THD TOTAL) y contrastarla con los valores cacheados del libro.
- **Qué no se implementa como si fuera válido:** el observador EKF de E1, el Método B de inversión de caudal desde la potencia, ni las correcciones propuestas en el Anexo B de `trabajo2.md`.

## DEC-004 · El paquete de BES-jun no entra todavía en asesor-esp

- **Fecha:** 2026-10-20
- **Estado:** registrada. No sustituye a P-14 ni aprueba la puerta G1.
- **Decisión:** el evaluador, los contratos y el catálogo de reglas candidatas viven en `datasets/en_uso/BES-jun/`. `asesor-esp/` sigue siendo el esqueleto de la aplicación futura y no recibe estas fórmulas, porque allí una fórmula solo se programa cuando está revisada y el motor interno usa unidades SI. BES-jun trabaja en las unidades de la hoja y con fórmulas todavía en reserva.
- **Consecuencia:** la aplicación consumirá `integracion/` cuando se autorice. Hoy no hay reglas aprobadas para uso operacional.

## DEC-003 · Privacidad

- **Estado:** registrada.
- **Decisión:** el trabajo de esta iteración se hizo en la máquina local. No se enviaron libros, identificadores de pozo ni documentos a un servicio externo. El GLM no se instaló.
