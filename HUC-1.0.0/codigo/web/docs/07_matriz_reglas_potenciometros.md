# Matriz de reglas y potenciometros

Fecha de la lectura: 2026-10-21. No se modificaron fórmulas ni datasets.

## Qué es cada archivo

| Archivo | Qué contiene |
|---|---|
| `datasets/en_uso/BES-jun/integracion/reglas.json` | Copia de integración del catálogo. No es código ejecutable. |
| `datasets/en_uso/BES-jun/src/reglas/catalogo.py` | Catálogo declarativo. `REGLAS` y `disposicion`. Versión 1.1.0. |
| `datasets/en_uso/BES-jun/src/reglas/candidatas_bes_jun.py` | La única comparación numérica: `comparar_caudal_con_limites` y `limites_a_frecuencia`. |
| `datasets/en_uso/BES-jun/src/reglas/trazabilidad.py` | Consultas CT-06 y CT-08 ligadas a cada identificador. |
| `datasets/en_uso/BES-jun/src/evaluacion/motor.py` | Llama a esa comparación y arma el contrato de salida. `aprobada_para_uso_operacional` queda en falso. |
| `datasets/en_uso/BES-jun/integracion/variables.json` | Catálogo descriptivo. No define mandos. |
| `datasets/en_uso/BES-jun/integracion/pozos.json` | Medición registrada de cada pozo: frecuencia, caudal, límites a 60 Hz y curva de seis puntos. `fecha_medicion` es null. |
| `datasets/en_uso/BES-jun/integracion/contrato_entrada.schema.json` y `contrato_salida.schema.json` | Contratos. El caudal y la frecuencia son variables operacionales. Los límites, la curva y las TVD son parámetros protegidos. |
| `docs/reglas_candidatas.md`, `matriz_ecuaciones_BES-jun.md`, `consultas_tecnicas_pendientes.md`, `discrepancias_cientificas.md` | El catálogo genera el markdown de reglas. CT-08 (afinidad) y CT-06 (curva de fabricante) siguen abiertas. CT-03 es el signo del PIP y no alimenta estas reglas. |

`reglas.json` no se ejecuta. El motor usa `catalogo.py` y `comparar_caudal_con_limites`.

## Reglas encontradas

Hay cuatro identificadores. Tres tienen función Python. Ninguna está aprobada para uso operacional.

| Id | Función | Estado | Qué hace | Pozos |
|---|---|---|---|---|
| RC-BES-01 | `comparar_caudal_con_limites` | `pendiente_validacion`, disposición preliminar | Caudal estrictamente mayor que el máximo escrito, escalado con Q(f) = Q(60) · f / f_base | Las cinco hojas de BES-jun |
| RC-BES-02 | la misma función | igual | Caudal estrictamente menor que el mínimo escrito, escalado | Las mismas. En las cinco hojas, con la medición registrada, no se activa |
| RC-BES-03 | la misma función | igual | Mínimo ≤ caudal ≤ máximo, inclusive, en la misma frecuencia | Las mismas |
| RC-BES-04 | ninguna (`funcion_registrada` es null) | `no_evaluable` | Reservada. Falta curva de fabricante y BEP | Ninguno |

La función devuelve una sola de las tres primeras. No hay una segunda zona crítica. `limite_critico_validado` no existe en el catálogo.

## Matriz

| Regla | Variable | Unidad | Entrada modificable | Límite | Validación | Potenciometro |
|---|---|---|---|---|---|---|
| RC-BES-01, 02, 03 | `frecuencia_hz` | Hz | Sí. Variable operacional. Escala los límites | No hay límite de variador. El recorrido del mando es el mínimo y el máximo escritos en las cinco hojas: 56 Hz a 67 Hz | `pendiente_validacion` | Sí |
| RC-BES-01, 02, 03 | `caudal_operacion_bfpd` | BFPD | Sí. Es el valor que la regla compara | Mínimo y máximo escritos de la hoja, escalados a la frecuencia. Inclusive. El recorrido del mando es la curva tabulada a 60 Hz, escalada con la misma razón | `pendiente_validacion` | Sí |
| RC-BES-01, 03 | `limite_maximo_bfpd` | BFPD | No. Parámetro protegido. Es el umbral | Celda «Limite maximo» a 60 Hz | Texto de la hoja, no de fabricante | No |
| RC-BES-02, 03 | `limite_minimo_bfpd` | BFPD | No. Parámetro protegido. Es el umbral | Celda «Limite minimo» a 60 Hz | Igual | No |
| RC-BES-01, 02, 03 | `frecuencia_curva_hz` | Hz | No. Base del escalamiento. En el código es 60 Hz | Constante `FRECUENCIA_BASE_LIMITES_HZ` | La hoja escribe la curva en el bloque de 60 Hz | No |
| RC-BES-04 | `cono_eficiencia_bfpd` | BFPD | No | No hay umbral evaluable | `no_evaluable` | No |

## Por qué entra o no entra cada magnitud pedida

| Magnitud | Decisión | Motivo |
|---|---|---|
| Frecuencia | Potenciometro | Está en `variables_requeridas` de las tres reglas ejecutables y el contrato la acepta como variable operacional. |
| Caudal | Potenciometro | Es el término que la comparación mira. La medición inicial sale de `condiciones_registradas`. |
| Profundidad de la bomba | Eliminada | No está en ninguna regla ejecutable. Cambiar la TVD no cambia RC-BES-01, 02 ni 03. |
| Potencia | Eliminada | `brake_hp` es un punto de la curva. No es entrada ni resultado de la regla. |
| Head | Sin mando. Lectura del THD | El head de la curva no es consigna. El THD es salida del balance y no clasifica la regla de caudal. |
| PIP | Lectura | Salida de la celda. CT-03 sigue abierta. No entra en las reglas de caudal. |
| Presiones, API, BS&W, temperatura | Sin mando | Son variables operacionales del contrato, pero ninguna regla ejecutable las usa. |
| Cono de eficiencia | Sin mando | Solo lo nombra RC-BES-04, que no se evalúa. |

En QF-084 la curva a 60 Hz va de 0 a 12 500 BFPD y los límites escritos son 2 500 y 10 000. A 63 Hz la razón es 63/60, así que el recorrido del caudal pasa el máximo escrito: se puede cruzar RC-BES-01 sin salir de la curva tabulada. En QF-005 y QF-306 la curva llega a 10 000 BFPD y el máximo escrito a 60 Hz es 8 000: también se puede cruzar dentro de la curva.

No se usa el 50 % ni el 150 % del valor como recorrido. Ese margen no está en el expediente.
