# Plan de las etapas siguientes

La actividad 2.11 queda cerrada. El diccionario está en `docs/diccionario_variables.md`. La actividad 2.12 también queda cerrada: las tablas están en `data/processed/` y el procedimiento en `docs/normalizacion_datos.md`. La actividad 2.13 queda cerrada como selección metodológica, sin entrenamiento propio. La síntesis es `docs/estudio_modelos_2_13.md` y la exploración reproducible es `notebooks/03_seleccion_modelos.ipynb`. Los modelos de la actividad 2.14 se describen más abajo.

## 2.12 — Tabla larga, en dos archivos

Hecho. `mapping_long.csv` tiene 570 filas y `surging_long.csv` tiene 387. Mapping/`50psig` conserva los 186 pares. La velocidad que no estaba en la celda quedó marcada como `diseño_experimental`. No se apilaron los protocolos, no se imputaron mediciones y no se calcularon QG ni el caudal de surging en bpd.

Las mismas funciones quedaron copiadas en `src/esp_datascience/`. El cuaderno no se reemplazó por llamadas a ese paquete. Las tablas no se volvieron a escribir.

## 2.13 — Estudio científico y selección de modelos

Hecho, sin entrenamiento. El cuaderno 03 comprobó las huellas, las 30 y 18 curvas, la forma de las curvas y una matriz de idoneidad con pesos y sensibilidad. No hay candidato predictivo principal único.

Pasan a una fase experimental, si se autoriza: regresión lineal, polinomio de grado 2 con cresta, recta por la condición de gas y bosque aleatorio poco profundo. En mapping se añade el cociente respecto de la curva de agua, sin llamarlo con el símbolo normalizado de 2018. Quedan pospuestos el boosting, los vectores de soporte, el modelo aditivo, el proceso gaussiano, las redes, el mecanicista como predictor de psi, el híbrido y la simulación de fluidos.

## 2.14 — Desarrollo y evaluación experimental

Autorizada y no cerrada. La fase A está congelada en `2.14-A`. La fase B está cerrada: las 26 pruebas de esa fase terminaron correctamente y el cuaderno se ejecutó completo con nbconvert. No se cambiaron los pliegues ni la métrica. En esas particiones, el polinomio tiene menor MAE por curva que la recta: 1,364 psi frente a 3,999 psi en mapping, y 1,114 psi frente a 2,312 psi en surging.

La fase C está desarrollada. Estimó la recta por condición (M3), el bosque con profundidad y hoja mínima elegidas por el MAE interno (M4) y el cociente respecto del agua de entrenamiento (M5). M5 solo cubre 5 de las 30 curvas de mapping.

Las fases A a D están cerradas. La fase D comparó M1–M4 en todas las curvas y M5 solo en su subconjunto. El intervalo bootstrap, con 10.000 réplicas y la semilla 214, describe el remuestreo de estas curvas. M4 tiene menor MAE. M1 y M3 conservan la caída del agua. La regla de 2.13 no nombra un superior.

La fase E está desarrollada y queda para revisión de cierre de la actividad. No reentrena. El informe autónomo es `docs/informe_final_actividad_2_14.md`. No hay ganador único ni modelo híbrido. La actividad 2.14 no se declara cerrada.

El cuaderno fuente es `notebooks/04_entrenamiento_evaluacion_modelos.ipynb`. La ejecución de la fase C está en `resultados/04_ejecucion_fase_c.ipynb` y la de la fase D, de la A a la D, en `resultados/04_ejecucion_fase_d.ipynb`. El informe acumulado es `docs/resultados_modelos_2_14.md`.
