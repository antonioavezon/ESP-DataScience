# Informe de correcciones y AutoTest · BES-jun

**Documento histórico.** Registra la corrección del contrato 1.1.0 y la suite de 76 pruebas. No describe la versión vigente. El cierre técnico actual está en `docs/informe_cierre_tecnico_BES-jun.md`.

Fecha de cierre de esta intervención: 2026-10-20. El expediente sigue en `datasets/en_uso/BES-jun`. Estado: validación pendiente. Ninguna regla quedó aprobada para uso operacional.

## A. Estado anterior

La revisión externa señaló tres anomalías sobre un expediente que ya calculaba, clasificaba y exportaba.

1. El motor aceptaba solicitudes incompletas. Sin versión de contrato seguía. Un caudal sin unidad se trataba como BFPD. Un campo desconocido se ignoraba. La frecuencia `"alto"` llegaba al cálculo y terminaba en `TypeError: '<' not supported between instances of 'str' and 'float'`.
2. RC-BES-04, la regla de proximidad al punto de máxima eficiencia, citaba CT-09. CT-09 pregunta por la tolerancia entre el caudal calculado y el medido. La curva de bomba y el significado de EFF están en CT-06.
3. El cuaderno `04_modelo_deterministico` calculaba la elasticidad local de diez entradas. El informe consolidado no las presentaba.

La suite existente, ejecutada antes de tocar el motor, dio **53 passed** en 10.11 s. El registro está en `logs/respaldo_previo_a_autotest/pytest_linea_base.txt`. El respaldo de `motor.py`, `contratos.py` y `catalogo.py` está en esa misma carpeta.

## B. Causa raíz

La validación de esquema y la validación de dominio no se ejecutaban antes de los modelos. `evaluar` aplicaba sustituciones y comparaba magnitudes. Un texto llegaba al operador `<`. La ausencia de unidad no era un error: el código asumía la unidad canónica. La versión del contrato no era obligatoria en la práctica.

La referencia CT-09 de RC-BES-04 estaba escrita en `src/reglas/catalogo.py`. `integracion/reglas.json` y `docs/reglas_candidatas.md` se generan desde ese catálogo, así que corregir solo el JSON no habría durado.

El informe se arma en `src/informes/escribir_informe.py`. Esa función resumía la sensibilidad y no llamaba a las diez elasticidades que ya calculaba `analisis.sensibilidad_local`.

## C. Correcciones

Contrato de entrada y de salida: **1.1.0**. Motor: **0.2.0**. Catálogo de reglas: **1.1.0**.

- `src/evaluacion/contratos.py`. `validar_solicitud` aplica el esquema JSON con `jsonschema` (`Draft202012Validator`) y, si el esquema pasa, comprueba la unidad canónica y el dominio físico. `validar_sustitucion` hace lo mismo para el diccionario de `evaluar`. No hay conversión de unidades. Un booleano no es una magnitud. Un texto no se convierte a número. `inf` y `NaN` son `VALOR_NO_FINITO`. Frecuencia, etapas, diámetro o frecuencia de curva menores o iguales a cero, y caudal o TVD negativos, son `FISICAMENTE_INADMISIBLE`. Esos límites son los de la fórmula ya escrita, no umbrales nuevos. `jsonschema==4.26.0` quedó en `requirements.txt`.
- `src/evaluacion/motor.py`. `evaluar` y `evaluar_solicitud` validan antes de leer modelos. Una solicitud inválida sale como `entrada_invalida`, con `errores`, `reglas_ejecutadas` en 0 y `recomendacion_operacional_autorizada` en falso. No se captura `Exception` para disfrazar un fallo de programación.
- `src/reglas/candidatas_bes_jun.py`. Si el mínimo escrito supera al máximo, la comparación devuelve `no_evaluable` y no clasifica.
- `src/reglas/catalogo.py`. RC-BES-04 cita CT-06. RC-BES-01, 02 y 03 siguen citando CT-06 y CT-08. CT-09 permanece en la intersección Q* y en el contraste con el caudal medido.
- `src/reglas/trazabilidad.py`. Matriz revisada regla → variables → ecuaciones → consultas, con el motivo de cada enlace. La existencia del identificador no basta: el test compara el catálogo con esa matriz.
- `src/evaluacion/autotest.py`. Ejecutor de pytest. Escribe `logs/autotest_reporte.json` y `logs/autotest_reporte.md`.
- `src/informes/escribir_informe.py` y `src/analisis/graficos.py`. El informe incorpora los cinco puntos, la elasticidad de las diez entradas, las derivadas de las tres TVD y la figura `reports/figuras/elasticidad_q_estrella.png`.
- `src/integracion/construir_paquete.py`. La guía deja de llamar `error_validacion` al rechazo de una solicitud. El estado vigente es `entrada_invalida`.

No se modificaron constantes, exponentes ni umbrales físicos. RC-BES-04 sigue `no_evaluable`. No se inventó un BEP ni una curva de fabricante.

## D. Pruebas iniciales

```text
53 passed in 10.11s
```

Esa corrida es anterior a la validación estricta y al AutoTest nuevo. Después de la validación, y antes de añadir `tests/test_autotest_reglas.py`, la misma suite de 53 volvió a pasar. Las aserciones que esperaban asumir la unidad o el estado viejo se actualizaron al contrato 1.1.0. No se borró ninguna prueba.

## E. Pruebas nuevas

Están en `tests/test_autotest_reglas.py`. Los cinco pozos, sus caudales y sus límites a 60 Hz están escritos en el test. El máximo escalado que se compara es `qmax_60 * Hz / 60`, no el valor devuelto por `limites_a_frecuencia`.

| Prueba | Qué cubre |
|---|---|
| Los cinco pozos | La hoja leída coincide con la tabla y `evaluar` devuelve RC-BES-03, pendiente, sin recomendación |
| QF-084 | 63 Hz, 10301 BFPD, máximo a 60 Hz 10000, máximo escalado 10500; la comparación sin escalar queda como RC-BES-01 no vigente |
| RC-BES-01 | Por encima del máximo escalado; en el máximo y por debajo no |
| RC-BES-02 | Por debajo del mínimo escalado; en el mínimo no |
| Límites contradictorios y mínimo ausente | `no_evaluable`, cero reglas activadas |
| RC-BES-04 | No evaluable, consulta CT-06, sin CT-09 |
| Entradas inválidas | Texto, `inf`, `NaN`, cero, negativos, booleano, unidad ausente, campo desconocido |
| Solicitud | Versión ausente, versión distinta, dataset ajeno, JSON que no es objeto, pozo ausente |
| Contrato | La solicitud y la salida válidas cumplen el esquema; la salida se serializa |
| Trazabilidad | Catálogo = matriz revisada; cada consulta, variable y ecuación existe |
| Documentos | El informe vigente no recupera la clasificación vieja de QF-084; la discrepancia de EFF cita CT-06 |

Los mensajes de las cinco hojas no contienen órdenes de bajar o subir la frecuencia ni una afirmación de operación segura.

## F. Ciclos de corrección

1. Línea base: 53 passed.
2. Validación estricta. La suite anterior se actualizó donde el contrato cambió de verdad (unidad ausente y versión incompatible pasan a `entrada_invalida`). Volvió a dar 53 passed. No se relajó un umbral físico.
3. AutoTest nuevo. `pytest -q` dio **76 passed** en 11.86 s.
4. El ejecutor `python -m evaluacion.autotest` falló antes de correr las pruebas: el gancho `pytest_runtest_logreport` exige el argumento `report`. El método se llamaba `reporte`. Se renombró el argumento. No se tocó ninguna regla ni ninguna ecuación.
5. Segunda ejecución del ejecutor: **76/76**, estado `aprobado`, 11.835 s. Fecha del reporte: 2026-10-20T18:55:00+00:00.

## G. Resultados finales

| Métrica | Valor |
|---|---|
| Pruebas | 76 |
| Aprobadas | 76 |
| Fallidas | 0 |
| Omitidas | 0 |
| Reglas cubiertas | RC-BES-01, RC-BES-02, RC-BES-03, RC-BES-04 |
| Casos de regresión | Los cinco pozos, clasificados RC-BES-03 |
| Contrato verificado | 1.1.0 |
| Motor | 0.2.0 |
| Catálogo | 1.1.0 |
| Errores pendientes de la suite | ninguno |
| Duración | 11.835 s |

El reporte reproducible es `logs/autotest_reporte.json` y `logs/autotest_reporte.md`.

## H. Evaluación científica

Sigue sin validación externa:

- Identidad Cluster / Pozo.
- Signo del PIP frente a F-12 (CT-03).
- Exponente y constantes de Hazen-Williams (CT-05).
- Unidad de BS&W y el valor único de °API (CT-10).
- Si la tabla de seis puntos y los límites son de fabricante (CT-06).
- Si Q ∝ f puede aplicarse a esos límites (CT-08).
- Qué diferencia entre Q* y el caudal medido sería aceptable (CT-09). El caudal medido entra en la fricción: el contraste no es una predicción independiente.
- RC-BES-04. No hay curva de eficiencia confirmada. No se infiere el BEP.
- P-14, que no cambia este expediente.

El rango observado, 56–67 Hz, no es un límite operacional. A 80 Hz el modelo transcrito calcula y no avisa; el evaluador marca la salida del dominio observado y no cambia la ecuación.

## I. Integración

La aplicación futura puede, sin Jupyter y sin un modelo de lenguaje:

- enviar una solicitud del contrato 1.1.0;
- recibir `entrada_invalida` con errores estructurados, o `no_evaluable`, o `completada_preliminar`;
- leer PIP, THD, Q* y la regla preliminar RC-BES-01, 02 o 03, con evidencia y versión;
- comprobar que `recomendacion_operacional_autorizada` es falso.

No puede tratar RC-BES-04 como ejecutable, ni aprobar reglas, ni ordenar un cambio de frecuencia. Un modelo de lenguaje, cuando exista, solo redactará ese JSON.

## J. Estado del dataset

BES-jun permanece en `datasets/en_uso/`. No se trasladó a `procesadas`. No se abrieron RB-1521 ni RB-IA-2191. El Excel de trabajo conserva el SHA-256 `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85` y 329308 bytes, igual que la copia original.

## Cómo volver a ejecutar el AutoTest

Desde la raíz del expediente, en Fedora 43, con el entorno del proyecto. El comando no abre Jupyter ni llama a un modelo de lenguaje. Escribe el reporte JSON y el Markdown en `logs/`.

```text
cd /home/antonio/projects/HUC/datasets/en_uso/BES-jun
PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m evaluacion.autotest
```

Salida distinta de cero si hay fallos. Para una sola familia:

```text
PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m pytest -q tests/test_autotest_reglas.py
```

## Documentos regenerados en esta pasada

- Informe: `reports/informe_analisis_BES-jun.md`, HTML junto a él, y `pdf/informes/informe_analisis_BES-jun.pdf` (9 páginas, SHA-256 `9e46c9cfe8e91ec6fca20486ba09f5dd0e8142152bc4452cba9a7bcedcc5b836`).
- Ficha, guía de integración y catálogos generados por `python -m integracion.construir_paquete`.
- Doce cuadernos: `python -m informes.pipeline_cuadernos` promovió 12 de 12, 0 errores. Las fuentes de los cuadernos ya citaban CT-06 para la curva EFF y CT-09 para la tolerancia de Q*; no hubo que reconstruirlos. No se usó `exportar_pdf`.
