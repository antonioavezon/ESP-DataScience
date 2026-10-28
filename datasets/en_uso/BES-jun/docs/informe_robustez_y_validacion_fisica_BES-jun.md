# Informe de robustez y comprobación físico-matemática · BES-jun

Pasada registrada del motor 0.4.0 y de 123 pruebas. La pasada posterior está en `docs/informe_validacion_integral_BES-jun.md`.

Fecha: 2026-10-20. Software **0.4.0**. Motor **0.4.0**. Contrato **1.3.0**. Catálogo de reglas **1.1.0**. El expediente sigue en `datasets/en_uso/BES-jun`. Ninguna regla quedó aprobada.

## A. Diagnóstico

La línea base, antes de esta pasada, fue **85 passed** en 11.85 s (`logs/respaldo_previo_a_robustez/pytest_linea_base.txt`).

Se reprodujeron dos fallos. Un `nombre` enviado como lista llegaba a `nombre in PARAMETROS_PROTEGIDOS` y lanzaba `TypeError: unhashable type: 'list'`. `fecha_observacion: 23` y `escenario_id: 1234` se rechazaban, pero el esqueleto de la respuesta copiaba el número a campos que el esquema solo admite como texto o null.

## B. Evaluación de try/except

No se envolvió el motor en un `except Exception` que devuelva un resultado vacío. Los tipos, las unidades, los duplicados, el tamaño y la ficha se rechazan en la validación, antes de los modelos. La captura de `Exception` queda en `evaluar`, `evaluar_solicitud` y `evaluar_json`, y alrededor de `calcular_hoja`. La traza va a `logs/incidentes.jsonl`. La respuesta pública solo lleva `incidente_id` y un texto fijo, sin ruta ni traceback. Si el registro falla, la respuesta estructurada se entrega igual.

## C. Reparaciones

- `src/evaluacion/contratos.py`. Un identificador se usa como clave solo si es texto. Hay límites de 100000 caracteres, 2000 nodos, profundidad 8 y 64 elementos. El contrato pasa a 1.3.0 porque la respuesta exige `incidente_id` y el error puede traer `mensaje`, `tipo_esperado` y `unidad_esperada`. Una solicitud 1.2.0 se rechaza.
- `src/evaluacion/motor.py`, versión 0.4.0. Los campos públicos se normalizan: un número no se copia a `fecha_referencia` ni a `escenario_id`.
- `src/modelo_deterministico/hipotesis_ct03.py`. Comparación hidrostática aislada. El motor no la llama y no reemplaza la celda.
- No se cambió ningún coeficiente ni ningún signo de la transcripción.

## D. Pruebas adversariales

Están en `tests/test_adversarial.py`. Cubren nombre como lista, objeto, booleano y null; fecha y escenario numéricos; JSON vacío, raíz lista y texto demasiado largo; cuarenta combinaciones con semilla `20261020`; y una excepción inyectada en `calcular_hoja`.

## E. Contratos

Todas las respuestas de esas pruebas cumplen el esquema 1.3.0, incluidas las inválidas. `dataset_evaluado` sigue en null cuando la solicitud no se procesa.

## F. Mensajes y plantillas

Diez plantillas en `integracion/ejemplos/plantillas/`, generadas ejecutando el motor. Los caudales de QF-084 son los de la hoja. El escenario de 11000 y 20000 está marcado como prueba y no autoriza operación. El catálogo de códigos está en `integracion/README.md`. Ningún mensaje propone completar un dato con un promedio.

## G. Modelos

La matriz está en `docs/matriz_ecuaciones_BES-jun.md`. M-BES-FLUIDO, M-BES-BALANCE y M-BES-INTERSECCION siguen en `transcripcion-1` y siguen reproduciendo la caché.

## H. Pruebas matemáticas

`tests/test_propiedades_fisicas.py`. API 10 da gravedad específica 1 por la definición escrita en el test. El gradiente es `0.052` por la densidad. La fricción crece con el caudal y la longitud y baja con el diámetro, con los exponentes 1.85 y 4.8566. La afinidad de la hoja cumple `Q ∝ f` y `H ∝ f²`. Fuera de la tabla no hay caudal inventado. La THD sube con la descarga, la fricción y el THP, y baja con el PIP.

## I. Discrepancias

Con el sensor 100 ft más profundo que el intake, la celda de PIP y la hipótesis hidrostática simple difieren en 200 ft. CT-03 queda abierta. CT-02, CT-05, CT-06, CT-08 y CT-09 también. El exponente 4.8566 no se unificó con el 4.8655 del PDF.

## J. AutoTest

| | |
|---|---|
| Inicial | 85 passed en 11.85 s |
| Final | 123/123, 0 fallos, 0 omitidas, 12.847 s |
| Fecha | 2026-10-20T19:54:50+00:00 |
| Reporte | `logs/autotest_reporte.md` |

## K. Integración

El paquete es 0.4.0. El ejemplo de QF-084 se volvió a ejecutar y da RC-BES-03. Las plantillas se vuelven a ejecutar en la suite.

## L. Pendientes

CT-01 a CT-10 y P-14. La identidad Cluster/Pozo, el signo del PIP, Hazen-Williams, la unidad de BS&W, la curva de fabricante, la afinidad y la tolerancia entre Q* y el caudal medido.

## M. Cierre

El software 0.4.0 rechaza las entradas mal tipadas que se reprodujeron y controla una excepción imprevista sin devolver una recomendación. Eso no valida físicamente las fórmulas. Las reglas siguen pendientes o no evaluables. BES-jun no se movió. El Excel conserva el SHA-256 `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`. El informe consolidado, regenerado, tiene SHA-256 `25cbc343c28df4705fd5dc36796f1f5fc0972c6e0240582de3484a557a2fabbb`.

Para repetir la suite, sin Jupyter:

```text
cd /home/antonio/projects/HUC/datasets/en_uso/BES-jun
PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m evaluacion.autotest
```
