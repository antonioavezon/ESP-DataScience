# Plan de las etapas siguientes

La actividad 2.11 queda cerrada. El diccionario está en `docs/diccionario_variables.md`. La actividad 2.12 también queda cerrada: las tablas están en `data/processed/` y el procedimiento en `docs/normalizacion_datos.md`. No hay modelos entrenados.

## 2.12 — Tabla larga, en dos archivos

Hecho. `mapping_long.csv` tiene 570 filas y `surging_long.csv` tiene 387. Mapping/`50psig` conserva los 186 pares. La velocidad que no estaba en la celda quedó marcada como `diseño_experimental`. No se apilaron los protocolos, no se imputaron mediciones y no se calcularon QG ni el caudal de surging en bpd.

## 2.13 — Recién entonces, un modelo

El primer ajuste, si se autoriza, sería el más simple de `docs/matriz_modelos_candidatos.md`, sobre una sola tabla y con validación por curvas completas. El objetivo sería `dp2_3_psi`. El modelo híbrido espera a que exista una predicción física calculable. No forma parte de lo ya hecho.
