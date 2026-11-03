# Progreso de la investigación

Bitácora del laboratorio ESP-DataScience. Los hallazgos de las actividades 2.1 a 2.10 salen de la ejecución de `notebooks/01_exploracion_inicial.ipynb` sobre las copias locales de los Excel. Los pares numéricos completos no se interpretan como mediciones físicamente validadas ni como experimentos independientes.

## 2.1 — Localización de archivos

La raíz del laboratorio se obtiene con `pathlib`, subiendo desde el directorio de trabajo hasta la carpeta que contiene a la vez:

- `data/raw/mapping.xlsx`
- `data/raw/surging.xlsx`

Ambos archivos están presentes. No se usan rutas del computador donde se hizo el análisis anterior.

## 2.2 — Identificación de hojas

`pd.ExcelFile()` muestra las mismas tres hojas en los dos libros:

- `50psig`
- `100psig`
- `150psig`

Dimensiones al leer con `header=None`:

| Archivo | Hoja | Filas | Columnas |
|---|---|---:|---:|
| mapping | 50psig | 50 | 18 |
| mapping | 100psig | 52 | 18 |
| mapping | 150psig | 55 | 18 |
| surging | 50psig | 50 | 9 |
| surging | 100psig | 61 | 9 |
| surging | 150psig | 56 | 9 |

El nombre de las hojas coincide. El tamaño no. El inventario de columnas de las actividades siguientes se limita a Mapping/`50psig`.

## 2.3 — Inspección inicial

La hoja `50psig` de `mapping.xlsx`, leída con `header=None`, tiene **50 filas y 18 columnas**. Las primeras filas mezclan rótulos de condición, nombres de variable y valores numéricos. Las primeras 15 filas quedan impresas en el notebook ejecutado.

## 2.4 — Inventario de columnas

Los encabezados de las filas 0 y 1, columna por columna:

| Índice | Condición en la fila 0 | Variable en la fila 1 |
|---:|---|---|
| 0 | sin rótulo | rotary speed |
| 1 | Single Phase | Flow rate |
| 2 | sin rótulo | DP2-3 |
| 3 | sin rótulo | sin rótulo |
| 4 | Qgd=0.005 | Flow rate |
| 5 | sin rótulo | DP2-3 |
| 6 | sin rótulo | sin rótulo |
| 7 | Qgd=0.01 | Flow rate |
| 8 | sin rótulo | DP2-3 |
| 9 | sin rótulo | sin rótulo |
| 10 | Qgd=0.015 | Flow rate |
| 11 | sin rótulo | DP2-3 |
| 12 | sin rótulo | sin rótulo |
| 13 | sin rótulo | sin rótulo |
| 14 | sin rótulo | sin rótulo |
| 15 | sin rótulo | sin rótulo |
| 16 | sin rótulo | sin rótulo |
| 17 | sin rótulo | sin rótulo |

Una celda de encabezado vacía no implica que el resto de la columna esté vacío. Las columnas 13, 14, 16 y 17 no tienen rótulo en las filas 0 y 1, y aun así contienen información más abajo.

## 2.5 — Perfilamiento de columnas

Celdas con información (no vacías) en Mapping/`50psig`:

| Índice | Celdas con información |
|---:|---:|
| 0 | 4 |
| 1 | 35 |
| 2 | 33 |
| 3 | 0 |
| 4 | 49 |
| 5 | 47 |
| 6 | 0 |
| 7 | 43 |
| 8 | 41 |
| 9 | 0 |
| 10 | 40 |
| 11 | 38 |
| 12 | 0 |
| 13 | 22 |
| 14 | 21 |
| 15 | 0 |
| 16 | 17 |
| 17 | 16 |

Columnas completamente vacías: **[3, 6, 9, 12, 15]**. Esas columnas se registran y se conservan.

## 2.6 — Investigación de bloques

Inspección de las columnas **[0, 13, 14, 16, 17]**:

- La columna 0 alterna el rótulo `rotary speed` con dos valores numéricos: **1800** y **3500**.
- La columna 13 contiene el rótulo intermedio `Qgd=0.04`, el nombre `Flow rate` y después valores numéricos.
- La columna 14 contiene el nombre `DP2-3` y después valores numéricos.
- La columna 16 contiene el rótulo intermedio `Qgd=0.05`, el nombre `Flow rate` y después valores numéricos.
- La columna 17 contiene el nombre `DP2-3` y después valores numéricos.

Esta actividad no asigna la unidad. La actividad 2.11, ya cerrada, la fija en rpm.

## 2.7 — Estructura vertical

Hay dos filas de condiciones experimentales en Mapping/`50psig`:

| Fila | Condiciones presentes |
|---:|---|
| 0 | Single Phase; Qgd=0.005; Qgd=0.01; Qgd=0.015 |
| 22 | Single Phase; Qgd=0.01; Qgd=0.02; Qgd=0.03; Qgd=0.04; Qgd=0.05 |

La fila 1 nombra las variables del primer bloque. La fila 23 nombra las del segundo. `Qgd=0.04` y `Qgd=0.05` aparecen solo en el segundo bloque.

## 2.8 — Inventario estructurado

`df_inventario` describe únicamente Mapping/`50psig`. Cada condición ocupa la columna de `Flow rate`; `DP2-3` está en la columna siguiente.

| Hoja | Velocidad | Condición | Columna de caudal | Columna de DP |
|---|---:|---|---:|---:|
| 50psig | 1800 | Single Phase | 1 | 2 |
| 50psig | 1800 | Qgd=0.005 | 4 | 5 |
| 50psig | 1800 | Qgd=0.01 | 7 | 8 |
| 50psig | 1800 | Qgd=0.015 | 10 | 11 |
| 50psig | 3500 | Single Phase | 1 | 2 |
| 50psig | 3500 | Qgd=0.01 | 4 | 5 |
| 50psig | 3500 | Qgd=0.02 | 7 | 8 |
| 50psig | 3500 | Qgd=0.03 | 10 | 11 |
| 50psig | 3500 | Qgd=0.04 | 13 | 14 |
| 50psig | 3500 | Qgd=0.05 | 16 | 17 |

La velocidad 1800 está en la fila 2 de la columna 0. La velocidad 3500 está en la fila 24 de la columna 0. Estas posiciones no se trasladan a otras hojas.

## 2.9 — Conteo de observaciones

Para cada condición se convierten caudal y `DP2-3` con `pd.to_numeric(errors="coerce")` y se cuentan las filas en las que ambos valores son numéricos.

- Velocidad 1800: filas desde la 2 hasta antes de la 22.
- Velocidad 3500: filas desde la 24 hasta el final de la hoja.

| Velocidad | Condición | Pares completos |
|---|---|---:|
| 1800 | Single Phase | 10 |
| 1800 | Qgd=0.005 | 19 |
| 1800 | Qgd=0.01 | 18 |
| 1800 | Qgd=0.015 | 15 |
| 3500 | Single Phase | 21 |
| 3500 | Qgd=0.01 | 26 |
| 3500 | Qgd=0.02 | 21 |
| 3500 | Qgd=0.03 | 21 |
| 3500 | Qgd=0.04 | 20 |
| 3500 | Qgd=0.05 | 15 |

## 2.10 — Verificaciones

Comprobación programática sobre Mapping/`50psig`:

| Verificación | Resultado |
|---|---:|
| Pares completos | 186 |
| Condiciones inventariadas | 10 |
| Pares a velocidad 1800 | 62 |
| Pares a velocidad 3500 | 124 |

Las cuatro comprobaciones coinciden con el análisis anterior. 62 + 124 = 186.

## 2.11 — Diccionario científico de variables

Quedó cerrado con tres fuentes locales: el artículo de 2019 (`docs/esp_gassy_flow_paper.pdf`), Zhu et al. (2018b) en `ProjectESP/Papers/Zhu 2018b.pdf` y la tesis de Zhu (2017) en `ProjectESP/Papers/Thesis/Two-phase/Zhu 2017 (PhD thesis).pdf`. El diccionario, la auditoría, la matriz de modelos, la propuesta y el plan están en `docs/`. El cuaderno `notebooks/01_exploracion_inicial.ipynb` continúa después de la actividad 2.10. No se modificaron los Excel ni se entrenaron modelos. Las cifras de la actividad 2.10 no cambiaron.

Lectura de trabajo:

- Qgd = QG / Qmax, adimensional. Qmax de la TE-2700 a 3500 rpm es 4900 bpd.
- QBEP a 3500 rpm es 2700 bpd, el mismo punto que 0,005 m³/s. Surging usa 0,75 QBEP, QBEP y 1,25 QBEP.
- `Flow rate` se lee como QL en bpd.
- `DP2-3` se lee como el incremento de presión de la etapa 3, en psi. El rótulo no está en la tesis. La certeza es media.
- `GVF0` se lee como la fracción de gas de admisión en porcentaje. El sufijo 0 no está definido.
- Psep de las hojas: 50, 100 y 150 psig.
- A 1800 rpm el mapping usa Qgd = 0,005, 0,01 y 0,015. A 3500 rpm usa Qgd = 0,01, 0,02, 0,03, 0,04 y 0,05. Esa regla asigna la velocidad de Mapping/`100psig` y Mapping/`150psig`, cuyas celdas están vacías.

## 2.12 — Normalización de los datos experimentales

Quedó cerrada en `notebooks/02_normalizacion.ipynb`. Se escribieron `data/processed/mapping_long.csv` (570 filas) y `data/processed/surging_long.csv` (387 filas). Los Excel de `data/raw` conservan su SHA-256. No se entrenaron modelos y no se apilaron los dos protocolos.

Mapping/`50psig` repite 186 pares, 10 condiciones, 62 a 1800 rpm y 124 a 3500 rpm. Las otras hojas repiten los totales de la auditoría: 192, 192, 119, 129 y 139. No hubo discrepancia.

La velocidad de Mapping/`100psig` y Mapping/`150psig` no estaba en la celda. En la tabla queda con origen `diseño_experimental`. `GVF0` sigue en porcentaje y `DP2-3` en psi. El detalle está en `docs/normalizacion_datos.md`.

## Reorganización del código

Después de publicar la actividad 2.12 se copiaron sus funciones a `src/esp_datascience/`. Los cuadernos `01_exploracion_inicial.ipynb` y `02_normalizacion.ipynb` conservan su texto, su código y sus resultados. Esta reorganización no es una actividad científica nueva y no inicia la 2.13.

`tests/test_normalizacion.py` ejecutó 4 pruebas con `unittest`. Todas pasaron. La copia en `src/` reproduce el texto de los dos CSV. Sus huellas siguen siendo `ff68e36703d3d3901b8bd964008c49b062afa9d89a817b9d66e7849f9b400648` para mapping y `f58e8e2cac74acdf2081479ec8769422f39c4e4665f5b3ff472df4a70b15bd96` para surging. Los Excel de `data/raw` tampoco cambiaron.

## 2.13 — Estudio científico y selección de modelos

Quedó cerrada como selección metodológica, sin entrenar modelos y sin resultados de predicción. La síntesis es `docs/estudio_modelos_2_13.md`. El registro reproducible es `notebooks/03_seleccion_modelos.ipynb`, ejecutado de principio a fin en este entorno. Se usaron el diccionario, la normalización, la matriz previa, los textos locales de Zhu y un complemento bibliográfico de fichas verificadas.

Hay 30 curvas en mapping y 18 en surging. No se apilan. Las curvas de agua bajan al subir el caudal. En 422 de 434 pares cercanos, la presión con gas queda por debajo del agua. En surging, las 18 curvas terminan más bajas de lo que empiezan. Esos hechos no identifican un régimen ni eligen un ganador.

Pasan a la actividad 2.14, si se autoriza: regresión lineal, polinomio de grado 2 con cresta, recta por la condición de gas y un bosque aleatorio poco profundo. En mapping se añade el cociente respecto de la curva de agua. No hay candidato principal único: la nota de la recta por condición y la del polinomio difieren en 0,15, y el primer puesto cambia si se da más peso a la validación. El mecanicista, el híbrido, las redes y la simulación de fluidos quedan pospuestos. Los Excel y los CSV no se modificaron.

## Actividad 2.14, en curso

### 2.14 — Desarrollo y evaluación experimental de modelos

Fase A cerrada y congelada en `2.14-A`. Fase B cerrada para la recta y el polinomio de grado 2 con cresta: 26 pruebas automatizadas terminaron correctamente y el cuaderno se ejecutó completo con nbconvert. Una ejecución reprodujo el MAE por curva: 3,999 psi y 1,364 psi en mapping, 2,312 psi y 1,114 psi en surging. Ese cierre no cierra la actividad.

Fase C cerrada en su desarrollo, sin reabrirla. M3 cubre las 30 y las 18 curvas, con MAE por curva de 3,783 psi y 2,041 psi. M4 queda en 1,044 psi y 0,754 psi. M5 entra solo en cinco curvas de 50 psig, con 2,078 psi.

Antes de la fase D se cerraron los libros Excel de `tests/test_normalizacion.py` con un administrador de contexto. La normalización y las huellas no cambiaron. Las fases A, B y C no se reabren con ese mantenimiento.

Fases A, B, C y D cerradas, sin reajustar M1–M5. El intervalo del 95 % por curvas, con 10.000 réplicas y semilla 214, deja a M4 por debajo de M2 y deja a M3 frente a M1 cruzando el cero. Ese intervalo no se lee como generalización. La regla de superioridad de 2.13 no se cumple. No hay ganador único.

Fase E desarrollada. Sintetiza la precisión de M4, la referencia interpretable M1, la referencia no lineal M2 y la referencia parcial M5, sin pesos nuevos y sin un modelo híbrido. El informe autónomo es `docs/informe_final_actividad_2_14.md`. La actividad 2.14 está formalmente cerrada, con las fases A, B, C, D y E completadas y verificadas, el 16 de octubre de 2026.

La actividad 2.15 está desarrollada y en revisión científica. Todavía no está cerrada. Compara, sin reentrenar, el conocimiento publicado por Zhu con los resultados de la 2.14. El cuaderno es `notebooks/05_comparacion_cientifica_zhu.ipynb`. El informe es `docs/estudio_comparativo_zhu_2_15.md`. La matriz es `docs/matriz_evidencias_2_15.csv`. El proyecto es de iniciativa personal: no es un entregable de una pasantía ni una posición institucional. Las mediciones siguen siendo de Zhu, bajo CC BY 4.0 en el conjunto Mendeley. Los PDF de artículos y la tesis no se redistribuyen.


## Procedencia de los archivos usados en 2.1 a 2.10

Los Excel de trabajo son copia, con otro nombre, del conjunto de Jianjun Zhu en Mendeley Data, DOI 10.17632/fk2b4r69bs.1, licencia CC BY 4.0. El SHA-256 de `data/raw/mapping.xlsx` y de `data/raw/surging.xlsx` coincide con el de los archivos originales. El contenido no se modificó para obtener las cifras de esta bitácora.

El PDF de 2019 no forma parte del repositorio Git. La actividad 2.11 lo usó junto con la tesis de 2017 y el artículo de 2018b, que están en `ProjectESP` y tampoco se publican desde este laboratorio.
