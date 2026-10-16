# Plan de las etapas siguientes

La actividad 2.11 queda cerrada. El diccionario está en `docs/diccionario_variables.md`. Usa el artículo de 2019, el artículo de 2018b y la tesis de Zhu (2017). No hay modelos entrenados ni tablas en `data/processed`.

## 2.12 — Tabla larga, todavía en dos archivos

Construir, sin modificar los Excel de `data/raw`:

- Una tabla de mapping, con hoja, velocidad, condición, caudal en bpd y `DP2-3` en psi. En `100psig` y `150psig` la velocidad se anota como asignación del diseño experimental, no como celda leída.
- Otra tabla de surging, con hoja, velocidad, fracción de QBEP, `GVF0` en porcentaje y `DP2-3` en psi.

No se apilan las dos tablas. No se divide `GVF0` por 100 salvo que esa conversión quede escrita como tal. No se calcula QG a 1800 rpm mientras Qmax solo esté dado a 3500 rpm.

## 2.13 — Recién entonces, un modelo

El primer ajuste, si se autoriza, sería el más simple de `docs/matriz_modelos_candidatos.md`, sobre una sola tabla y con validación por curvas completas. El objetivo sería `DP2-3` en psi. El modelo híbrido espera a que exista una predicción física calculable. No forma parte de 2.12.
