# Informe de cierre técnico · BES-jun

**Documento histórico.** Registra el software 0.3.0, el contrato 1.2.0 y la suite de 85 pruebas. La pasada posterior está en `docs/informe_robustez_y_validacion_fisica_BES-jun.md`.

Fecha: 2026-10-20. Software **0.3.0**. Contrato **1.2.0**. Motor **0.3.0**. Catálogo de reglas **1.1.0**. El expediente sigue en `datasets/en_uso/BES-jun`.

## 1. Resumen

Se cerró el desarrollo computacional del primer dataset. Cuatro defectos de la revisión externa quedaron corregidos en el motor y en los generadores, con pruebas que los reproducen. La aprobación física y operacional de las reglas no forma parte de este cierre.

Línea base, antes de tocar el código de esta pasada: **76 passed** en 11.59 s. Registro: `logs/respaldo_previo_a_cierre/pytest_linea_base.txt`. Entorno: Fedora 43, Python 3.14.8, pandas 3.0.6, numpy 2.5.4, jsonschema 4.26.0, pytest 9.1.1.

## 2. Anomalías y causa

1. **Variable duplicada.** `evaluar_solicitud` volcaba la lista `variables` en un diccionario. La última aparición reemplazaba a las anteriores, con el mismo valor o con otro, y la regla se evaluaba sin aviso.
2. **Ficha reescribible.** Límites, etapas y curva viajaban por el mismo canal que el caudal. Sustituir el máximo de 10000 BFPD por 20000 cambiaba la clasificación de un caudal de 11000 BFPD a 63 Hz. El Excel no convierte ese número en un límite validado, pero el operador tampoco puede cambiarlo en la evaluación ordinaria.
3. **Salida fuera de esquema.** El esquema exigía `dataset_id` constante `BES-jun` también cuando la solicitud era de otro dataset. La respuesta decía `entrada_invalida` y, a la vez, incumplía el contrato que un consumidor externo habría validado. `errores_de_salida` no usaba el mismo validador JSON.
4. **Documentación de una corrida anterior.** `docs/reporte_cierre_computacional.md` seguía presentando 53 pruebas y el hash viejo del informe como si fueran el estado actual.

## 3. Correcciones

- `src/evaluacion/contratos.py`, contrato 1.2.0. Lista de mediciones operacionales y de parámetros protegidos. `VARIABLE_DUPLICADA`, `PARAMETRO_PROTEGIDO`, `CLAVE_JSON_DUPLICADA`, `CONFIGURACION_AJENA`. `interpretar_json` no se queda con la última clave repetida. `errores_de_salida` usa `Draft202012Validator` sobre el esquema publicado y, además, rechaza una recomendación operacional sin regla aprobada.
- `src/evaluacion/motor.py`, motor 0.3.0. La salida separa `dataset_solicitado` y `dataset_evaluado`, `pozo_solicitado` y `pozo_resuelto`. Un dataset ajeno deja `dataset_evaluado` en nulo. El modo `simulacion` exige `escenario_id`, marca `hipotetico` y no escribe la ficha. Un fallo de `calcular_hoja` después de validar la solicitud sale como `error_interno`, no como resultado operacional.
- No se modificó ninguna ecuación ni ningún coeficiente. RC-BES-04 sigue en CT-06 y `no_evaluable`. RC-BES-01, 02 y 03 siguen en `pendiente_validacion`.
- La guía de integración, la guía de datasets y el informe consolidado salen de sus generadores.

## 4. AutoTest

Comando, desde la raíz del expediente:

```text
PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m evaluacion.autotest
```

Resultado del 2026-10-20T19:23:09+00:00, en `logs/autotest_reporte.json` y `logs/autotest_reporte.md`:

| | |
|---|---|
| Total | 85 |
| Aprobadas | 85 |
| Fallidas | 0 |
| Omitidas | 0 |
| Duración | 11.805 s |
| Estado | aprobado |

Incluye los cuatro defectos: duplicados con valores iguales, distintos y tres apariciones; JSON con clave repetida; intento de reescribir máximo, mínimo, etapas y curva; escenario hipotético que no guarda la ficha; dataset ajeno que cumple el esquema; documentación histórica marcada y vigentes sin el conteo de 53; los cinco pozos en RC-BES-03; QF-084 con máximo escalado 10500.

## 5. Modelos

`M-BES-FLUIDO`, `M-BES-BALANCE` y `M-BES-INTERSECCION`, versión `transcripcion-1`. Las pruebas de reproducción contra la caché siguen aprobadas. Esa coincidencia es equivalencia con el Excel, no validez física independiente. El informe lo dice en la sección de la aplicación.

## 6. Reglas

| Regla | Estado | Consultas |
|---|---|---|
| RC-BES-01 | pendiente_validacion | CT-06, CT-08 |
| RC-BES-02 | pendiente_validacion | CT-06, CT-08 |
| RC-BES-03 | pendiente_validacion | CT-06, CT-08 |
| RC-BES-04 | no_evaluable | CT-06 |

Ninguna tiene `aprobada_para_uso_operacional`. En las cinco hojas registradas la clasificación preliminar es RC-BES-03. No es una autorización de operación.

## 7. Integración

El ejemplo `integracion/ejemplos/solicitud_qf084.json` se valida con el esquema, se ejecuta y da RC-BES-03. `resultado_qf084.json` cumple el esquema de salida 1.2.0. Una versión de contrato distinta de 1.2.0 se rechaza.

## 8. Documentación

Doce cuadernos sin reconstruir: no citaban el contrato 1.1.0 y ya separaban CT-06 de CT-09. El pipeline `python -m informes.pipeline_cuadernos` promovió 12 HTML y 12 PDF, 0 errores. Informe consolidado: 9 páginas, SHA-256 `159353755253caae48f1e1784c6689115c71ed6671d45f399f36d341ce812266`. La página de sensibilidad y la página 5 del PDF del cuaderno 04 muestran tabla, código y ecuación dentro de la hoja. Ficha y guía de integración regeneradas.

## 9. Depuración

Detalle en `docs/depuracion_documental_BES-jun.md`. Se marcaron como históricos el reporte de 53 pruebas, el informe de la pasada de 76 y el análisis preliminar del 17 de octubre. No se eliminó ningún archivo: las dos figuras antiguas siguen citadas. Los respaldos de `logs/` se conservan.

## 10. Integridad

SHA-256 del Excel de trabajo y de `fuentes/originales/Copia de FINAL BES-jun.xlsx`: `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`. El manifiesto de versión está en `integracion/manifiesto_version.json`. No contiene su propio hash ni el de este informe.

## 11. Limitaciones

CT-01 a CT-10 y P-14. Identidad Cluster/Pozo, signo del PIP, Hazen-Williams, unidad de BS&W, procedencia de la curva, significado de EFF, afinidad y tolerancia entre Q* y el caudal medido. El rango 56–67 Hz no es un límite operacional.

## 12. Estado final

Cierre técnico del software: sí, con la suite en 85/85, contratos coherentes, ejemplos ejecutados y documentos vigentes regenerados. La versión de software es 0.3.0 y no 1.0.0 porque las reglas no están aprobadas.

Cierre científico y operacional: no. Ninguna regla queda aprobada. BES-jun no se movió a `procesadas`. La promoción sigue bloqueada hasta una autorización expresa y el cierre de las consultas que correspondan.

## 13. Continuidad

Otro dataset no hereda las ecuaciones ni los nombres protegidos de BES-jun. Hereda el método: integridad del archivo, separación entre medición y ficha, rechazo de variables duplicadas, contrato versionado, reglas con estado, AutoTest sin Jupyter y exportación del documento completo. El procedimiento está en `docs/guia_procesamiento_datasets.md`. RB-1521 y RB-IA-2191 no se abrieron.
