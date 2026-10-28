# Cierre de validación de curvas y catastro · BES-jun

Fecha: 2026-10-20. Expediente en `datasets/en_uso/BES-jun`. No se movió. No se abrieron otros datasets. Ninguna regla quedó aprobada.

## A. Resumen de la intervención

Había dos tareas. La primera era dejar de aceptar una curva de simulación cuyo caudal retrocede aunque el head baje. La segunda era contar, desde el código, cuántas fórmulas hay, cuáles se usan y cuáles siguen sin validación externa.

La línea base, antes de editar, fue 151 pruebas en 13.54 s. Motor 0.4.1. Contrato 1.3.0. Respaldo en `logs/respaldo_previo_a_cierre_curvas/`. El motor pasó a 0.4.2 porque cambia el rechazo de una entrada que antes llegaba al cálculo. El contrato sigue en 1.3.0: no cambió la forma de la respuesta.

## B. Validación de curvas

Solicitud reproducida, con motor 0.4.1, guardada en `logs/respaldo_previo_a_cierre_curvas/reproduccion_retroceso_caudal.json`:

| Punto | Caudal BFPD | Head ft |
|---|---:|---:|
| 1 | 0 | 100 |
| 2 | 200 | 50 |
| 3 | 100 | 0 |

Resultado de esa ejecución: `no_evaluable`. Llegó a M-BES-FLUIDO, M-BES-BALANCE y M-BES-INTERSECCION. `reglas_ejecutadas` = 0. Sin errores de contrato. Contrato 1.3.0.

Causa: `_validar_curva` exigía head estrictamente descendente y caudales no repetidos como conjunto. No exigía `Q[i+1] > Q[i]`. El conjunto {0, 200, 100} pasa esa prueba. Con una THD de 25 ft entre los heads 50 y 0, la interpolación devolvía 150 BFPD, recorriendo el caudal hacia atrás.

El contrato de esta representación queda así: en el orden enviado, el caudal es estrictamente creciente y el head estrictamente descendente. La comparación es exacta, sin tolerancia ni redondeo. No se reordena, no se borra un punto y no se adapta la curva al algoritmo. No es una ley de todas las bombas centrífugas.

El rechazo señala el campo. En el caso reproducido es `parametros_escenario.curva[2].caudal_bfpd`, código `ESTRUCTURA_INVALIDA`, estado `entrada_invalida`. El modelo no se ejecuta.

Una curva con la misma forma y head dentro de rango, pero sin corte con la THD del pozo, sigue siendo `no_evaluable` y sí entra al modelo. El mensaje no es el de una curva mal formada.

Las cinco curvas de la hoja ya cumplen el orden. Enviadas de nuevo con solo `caudal_bfpd` y `head_ft`, QF-084 sigue en RC-BES-03 y el máximo a 63 Hz sigue en 10500 BFPD.

## C. Pruebas de regresión

`tests/test_curvas_orden.py` cubre el retroceso, el caudal decreciente, el duplicado, el head incompatible, los dos errores juntos, valores separados por un `nextafter`, sesenta puntos, la curva de la hoja, la falta de intersección, el vértice analítico y la interpolación entre puntos. Una fecha inválida y el retroceso se rechazan en la misma respuesta.

La suite anterior sigue aprobada. No se cambió una fórmula para conseguirlo.

## D. Protección del ciclo de datos

| Archivo | SHA-256 antes | SHA-256 después |
|---|---|---|
| `entrada/BES_jun.xlsx` | `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85` | el mismo |
| `fluidos_bes_jun.py` | `db856bb28e7b84123bde0dae62df091e73016afb3c747c301768b11ebbed43c8` | el mismo |
| `balance_bes_jun.py` | `3a7fdb6fd279aa6f2cf27a35c0bff9f72f49a058ca7569f3c869af8642ed7532` | el mismo |
| `interseccion_bes_jun.py` | `09a989177ab574c748ad151c9f355b4e83aa544680e68ac51c8cf71c5c5005b6` | el mismo |
| `hipotesis_ct03.py` | `5742ff43016673f11d1e95777941207ed21c597b3af6b34b650292818445f08a` | el mismo |

El original `fuentes/originales/Copia de FINAL BES-jun.xlsx` y la copia de la raíz del repositorio tienen la misma huella. Las curvas en memoria de las cinco hojas no se reordenan. Una simulación no escribe la ficha ni el Excel.

## E. Catastro matemático

Fuente: `src/catalogo/catastro_formulas_bes_jun.py`. El resumen se calcula desde esa lista. Los grupos principal, auxiliar, hipótesis y documentada no se solapan y suman el total. Los otros indicadores sí se solapan.

| Indicador | Cantidad |
|---|---:|
| Total de fórmulas únicas inventariadas | 20 |
| Fórmulas principales E-01 a E-10 | 10 |
| Fórmulas auxiliares adicionales | 4 |
| Fórmulas realmente utilizadas | 14 |
| Fórmulas implementadas, pero no utilizadas en resultados | 1 |
| Fórmulas solamente documentadas | 4 |
| Fórmulas matemáticamente verificadas | 15 |
| Fórmulas con consistencia física condicionada | 5 |
| Fórmulas con validación física externa suficiente | 0 |
| Fórmulas pendientes de validación experimental | 12 |
| Fórmulas con discrepancia identificada | 2 |
| Hipótesis alternativas no activas | 2 |

14 utilizadas + 1 implementada sin entrar en resultados + 5 no implementadas = 20. Las 15 verificadas matemáticamente son las 14 utilizadas más HYP-CT03. Eso no las valida físicamente.

## F. Fórmulas utilizadas

E-01 a E-10 producen el gradiente, el PIP, la THD y Q*, o escalan los límites de las reglas. AUX-ELAST, AUX-DERIV, AUX-MC y AUX-TVD producen números del informe o del control de survey. No son leyes de la bomba.

## G. Fórmulas verificadas

Las 15 con consistencia matemática tienen un oráculo escrito fuera de la función bajo prueba, citado en cada ficha. Consistencia física condicionada, no externa: E-01, E-03, E-04, E-06 y AUX-MC. Validación externa suficiente: ninguna.

## H. Fórmulas no validadas

Pendientes de experimento en estos pozos: las diez principales y las dos hipótesis. E-02 sigue sin origen de sus coeficientes. E-03 sigue con el rótulo de BS&W sin confirmar. E-09 no tiene curva de banco. E-10 no tiene curva de fabricante ni tolerancia entre Q* y el caudal medido.

Solo documentadas, sin función de cálculo: DOC-F02, DOC-POTENCIA, DOC-F36 y DOC-F41. El bloque eléctrico es un ítem, no un desglose de ecuaciones que el código no transcribe. HYP-PUNTO-FIJO está en el cuaderno 04b y no es importable desde el motor.

## I. Discrepancias físicas

E-05 permanece. La diferencia celda menos hidrostática es `2·(TVD_sensor − TVD_intake)`: 51.291 ft en QF-084, 38.627 ft en QF-301, 51.060 ft en QF-147, 41.247 ft en QF-005 y 41.078 ft en QF-306. La caché coincide con la celda. CT-03 sigue abierta. El signo no se cambió.

E-07 permanece. El exponente de la celda es 4.8566 y el PDF escribe 4.8655. La longitud es la TVD de descarga. CT-05 sigue abierta.

E-04 no entra en ese conteo. El factor 0.052 de la celda y el factor SI 0.051948 difieren en menos de 0.0001 y la función sigue usando 0.052.

## J. Reglas

RC-BES-01, RC-BES-02 y RC-BES-03 siguen en `pendiente_validacion`. Dependen de E-09 para escalar los límites y no heredan una validación física de esa álgebra. En las cinco hojas, con los datos registrados, la clasificación sigue siendo RC-BES-03. RC-BES-04 sigue `no_evaluable` por CT-06 y no apunta a una ecuación activa. Aprobadas: ninguna.

## K. Integración

El paquete se reconstruyó con el motor 0.4.2. La guía dice que el caudal de la curva de escenario tiene que crecer en el orden enviado y que no se reordena. Las plantillas se vuelven a ejecutar en la suite. Una simulación no autoriza operación.

## L. AutoTest

Inicial: 151 aprobadas, 13.54 s, motor 0.4.1.

Final: 172/172, 0 fallos, 0 omitidas, 17.977 s, 2026-10-20T20:59:29+00:00. Estado del reporte: aprobado.

```bash
cd /home/antonio/projects/HUC/datasets/en_uso/BES-jun
PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m evaluacion.autotest
```

Para volver a escribir el catastro:

```bash
PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -c "from catalogo.catastro_formulas_bes_jun import emitir; emitir()"
```

## M. Documentación

Regenerados: catastro Markdown, JSON, HTML y PDF; informe consolidado Markdown, HTML y PDF; guía HTML y PDF; esquemas y manifiesto.

Conservados: los doce cuadernos y sus HTML y PDF. Sus fuentes no cambiaron y ya tratan CT-03 como ambigüedad abierta.

PDF del catastro: `pdf/informes/catastro_maestro_formulas_BES-jun.pdf`, 18 páginas, carta, SHA-256 `7bf10d0f0d613e02cf10c69d7b914197f11c652db2a5657d99c10d0279f787ed`.

Informe PDF: `pdf/informes/informe_analisis_BES-jun.pdf`, SHA-256 `949cec67120050ac1594ab4c5941ad03f8ec8cf193e338d1772876ed9604e8dd`.

Guía PDF: `pdf/informes/guia_integracion_BES-jun.pdf`, SHA-256 `7bc0c2b15304cee491ca5d52a0c09ce8de912c2d8f0072405f9f1b8435b152e0`.

## N. Estado del dataset

**Cierre informático de esta pasada:** aprobado. La curva con caudal en retroceso no calcula, las curvas de las cinco hojas siguen produciendo RC-BES-03, el Excel y las ecuaciones conservan su huella y la suite no tiene fallos.

**Cierre científico:** no. Cero fórmulas con validación externa suficiente. E-05 y E-07 siguen con discrepancia identificada. Doce ítems siguen pendientes de experimento o de decisión externa.

**Cierre operacional:** no. Ninguna regla está aprobada. BES-jun sigue en `en_uso`.
