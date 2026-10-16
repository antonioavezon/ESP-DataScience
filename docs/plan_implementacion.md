# Plan de las etapas siguientes

La actividad 2.11 queda cerrada. El diccionario está en `docs/diccionario_variables.md`. La actividad 2.12 también queda cerrada: las tablas están en `data/processed/` y el procedimiento en `docs/normalizacion_datos.md`. La actividad 2.13 queda cerrada como selección metodológica. La síntesis es `docs/estudio_modelos_2_13.md` y la exploración reproducible es `notebooks/03_seleccion_modelos.ipynb`. No hay modelos entrenados.

## 2.12 — Tabla larga, en dos archivos

Hecho. `mapping_long.csv` tiene 570 filas y `surging_long.csv` tiene 387. Mapping/`50psig` conserva los 186 pares. La velocidad que no estaba en la celda quedó marcada como `diseño_experimental`. No se apilaron los protocolos, no se imputaron mediciones y no se calcularon QG ni el caudal de surging en bpd.

Las mismas funciones quedaron copiadas en `src/esp_datascience/`. El cuaderno no se reemplazó por llamadas a ese paquete. Las tablas no se volvieron a escribir.

## 2.13 — Estudio científico y selección de modelos

Hecho, sin entrenamiento. El cuaderno 03 comprobó las huellas, las 30 y 18 curvas, la forma de las curvas y una matriz de idoneidad con pesos y sensibilidad. No hay candidato predictivo principal único.

Pasan a una fase experimental, si se autoriza: regresión lineal, polinomio de grado 2 con cresta, recta por la condición de gas y bosque aleatorio poco profundo. En mapping se añade el cociente respecto de la curva de agua, sin llamarlo con el símbolo normalizado de 2018. Quedan pospuestos el boosting, los vectores de soporte, el modelo aditivo, el proceso gaussiano, las redes, el mecanicista como predictor de psi, el híbrido y la simulación de fluidos.

## 2.14 — Desarrollo y evaluación experimental

Autorizada. La fase A está preparada y espera revisión. No hay modelos entrenados.

El cuaderno `notebooks/04_entrenamiento_evaluacion_modelos.ipynb` fija tres pliegues por curvas completas, con anillo interno. Mapping reserva 10 curvas por pliegue y surging reserva 6. Cada pliegue conserva las dos velocidades, las tres presiones y las condiciones del protocolo en entrenamiento y en prueba. `GroupKFold` directo no se usa como reparto principal: en mapping deja un pliegue sin 100 psig y en surging deja un pliegue sin la fracción 1,25.

La fase B, si se aprueba, estimará la recta y el polinomio de grado 2 con cresta sobre esos cortes. El MAE en psi sigue siendo la métrica principal prevista. Si ningún modelo supera a la recta con la regla del cuaderno 03, la recta sigue siendo el informe.
