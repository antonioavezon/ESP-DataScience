# Plan de las etapas siguientes

La actividad 2.11 queda cerrada. El diccionario está en `docs/diccionario_variables.md`. La actividad 2.12 también queda cerrada: las tablas están en `data/processed/` y el procedimiento en `docs/normalizacion_datos.md`. La actividad 2.13 queda cerrada como estudio de selección, en `docs/estudio_modelos_2_13.md`. No hay modelos entrenados.

## 2.12 — Tabla larga, en dos archivos

Hecho. `mapping_long.csv` tiene 570 filas y `surging_long.csv` tiene 387. Mapping/`50psig` conserva los 186 pares. La velocidad que no estaba en la celda quedó marcada como `diseño_experimental`. No se apilaron los protocolos, no se imputaron mediciones y no se calcularon QG ni el caudal de surging en bpd.

Las mismas funciones quedaron copiadas en `src/esp_datascience/`. El cuaderno no se reemplazó por llamadas a ese paquete. Las tablas no se volvieron a escribir.

## 2.13 — Estudio científico y selección de modelos

Hecho, sin entrenamiento. El documento es `docs/estudio_modelos_2_13.md`. Mapping y surging siguen separados. La lista que pasaría a una fase experimental, en orden, es la regresión lineal, el polinomio con cresta, la recta por condición de gas, el cociente respecto de la curva de agua en mapping y el bosque aleatorio. No se declaró un modelo superior. El híbrido física–aprendizaje automático queda pospuesto.

## 2.14 — Desarrollo y evaluación experimental

No está iniciada. Solo empieza con autorización expresa. Comprende implementar, ajustar y comparar los modelos ya elegidos, con validación por curvas completas, y recién entonces decir si alguno es más adecuado. No forma parte de lo ya hecho.
