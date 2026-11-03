# Auditoría de preparación de datos

Lectura de las seis hojas con `header=None`, sin modificar los Excel. Los pares numéricos de esta nota usan la misma regla que la actividad 2.9: dos celdas de la fila son numéricas a la vez. Ese conteo no es una medición validada ni un experimento independiente.

La actividad 2.10 sigue vigente solo para Mapping/`50psig`: 186 pares, 10 condiciones, 62 a 1800 y 124 a 3500. El mismo detector, aplicado otra vez a esa hoja, reproduce esas diez cifras. Los conteos de las otras hojas son exploratorios y no sustituyen esa validación.

## Qué hay en cada archivo

### mapping.xlsx

Tres hojas: `50psig`, `100psig`, `150psig`. Ancho de 18 columnas. Columnas completamente vacías en las tres: 3, 6, 9, 12 y 15. Esas columnas se conservan.

Cada hoja tiene dos franjas de condiciones. La primera empieza en la fila 0. La segunda empieza en la fila 22 (`50psig`), 20 (`100psig`) o 30 (`150psig`).

Condiciones escritas en la primera franja: `Single Phase`, `Qgd=0.005`, `Qgd=0.01`, `Qgd=0.015`.

Condiciones escritas en la segunda: `Single Phase`, `Qgd=0.01`, `Qgd=0.02`, `Qgd=0.03`, `Qgd=0.04`, `Qgd=0.05`.

Variables de cada bloque: `Flow rate` y `DP2-3`. El rótulo `rotary speed` está en la columna 0.

| Hoja | Velocidad en las celdas | Velocidad según el diseño del ensayo | Pares numéricos exploratorios |
|---|---|---|---:|
| 50psig | 1800 y 3500 | 1800 en la primera franja y 3500 en la segunda | 186 |
| 100psig | la celda está vacía | la misma asignación, por los Qgd de cada franja | 192 |
| 150psig | la celda está vacía | la misma asignación, por los Qgd de cada franja | 192 |

La tesis de Zhu (2017), sección 2.3.3, y Zhu et al. (2018b), sección 3.3, fijan la primera franja (Qgd = 0,005, 0,01 y 0,015) en 1800 rpm y la segunda (Qgd = 0,01 a 0,05) en 3500 rpm. Eso vale para las tres presiones. Las celdas de 100 y 150 psig siguen vacías; la velocidad no se inventa desde el orden de las filas, se toma de ese diseño.

### surging.xlsx

Tres hojas con los mismos nombres y 9 columnas. No hay columnas completamente vacías. El esquema no es el de mapping.

Cada hoja tiene dos franjas. La velocidad está escrita y el encabezado dice `Rotary Speed (rpm)`.

Condiciones de caudal líquido: `0.75Qbep`, `Qbep`, `1.25Qbep`.

Variables: `GVF0` y `DP2-3`.

| Hoja | Velocidades escritas | Pares numéricos exploratorios |
|---|---|---:|
| 50psig | 1800 y 3500 | 119 |
| 100psig | 1800 y 3500 | 129 |
| 150psig | 1800 y 3500 | 139 |

## Variables disponibles, derivables y ausentes

Disponibles, con la lectura del diccionario:

- Mapping: Qgd o `Single Phase`, `Flow rate` en bpd, `DP2-3` como incremento de la etapa 3 en psi, y la velocidad a 1800 o 3500 rpm. En 100 y 150 psig la velocidad viene del diseño experimental, no de la celda.
- Surging: velocidad en rpm, líquido en 0,75 QBEP, QBEP o 1,25 QBEP, `GVF0` como fracción de gas de admisión en porcentaje, y `DP2-3` en psi.
- Psep, por el nombre de la hoja: 50, 100 y 150 psig.
- Qmax de la TE-2700 a 3500 rpm: 4900 bpd. QBEP a 3500 rpm: 2700 bpd.

No se derivan en la actividad 2.11 ni en la 2.12:

- QG = Qgd × Qmax. Qmax está dado a 3500 rpm. A 1800 rpm la tesis no escribe otro número.
- La fracción entre 0 y 1 a partir de `GVF0`. Si la columna está en porcentaje, habría que dividir por 100. El sufijo 0 no está definido y no se hace esa división aquí.

Siguen fuera de un dataset único:

- Mapping y surging no se apilan. Uno fija Qgd y varía el líquido. El otro fija el líquido respecto de QBEP y registra `GVF0`.
- QG no es una columna.
- La temperatura de cada fila y la geometría de la etapa no están en los Excel.

## Compatibilidad entre registros

No se combinan filas de mapping con filas de surging. El primero fija el gas, en forma de Qgd, y varía el caudal líquido. El segundo fija un caudal líquido relativo a Qbep y registra `GVF0`. Las columnas no tienen el mismo significado confirmado.

Las tres hojas de mapping pueden reunirse si la velocidad ausente en la celda queda marcada como asignación del diseño experimental. Guardar ese número como si la celda lo trajera seguiría siendo incorrecto.

Dentro de una misma hoja, los bloques comparten el nombre de las columnas `Flow rate` y `DP2-3`, o `GVF0` y `DP2-3`. La actividad 2.12 construye una tabla larga por archivo. Cada fila conserva la hoja, la velocidad y la condición. Donde la celda de velocidad estaba vacía, el origen queda en `diseño_experimental`.

## Inconsistencias y datos faltantes

- Mapping a 100 y 150 psig: la celda de velocidad está vacía. La velocidad se lee del diseño del ensayo, no de esa celda.
- La segunda franja de mapping no repite `Qgd=0.005` y sí agrega `Qgd=0.02` hasta `Qgd=0.05`. Es el diseño de 3500 rpm frente al de 1800 rpm, no un error de copia.
- `GVF0` supera 1. Se lee como porcentaje, que es la escala de las figuras, y no como fracción de 0 a 1.
- El artículo de 2019 lista ΔP en Pa y Q en m³/s. La tesis de los mismos ensayos usa psi y bpd. Los Excel siguen a la tesis.
- Hay celdas vacías dentro de las columnas con datos. En las seis hojas, esas posiciones tienen las dos mediciones vacías a la vez. No apareció un par con una sola celda numérica. La actividad 2.12 no convierte esos huecos en filas.

## Riesgo de fuga entre entrenamiento y validación

Todavía no hay modelo. Estos riesgos quedan registrados para cuando exista una tabla:

- Los puntos de una misma curva de desempeño no son ensayos independientes. Un reparto aleatorio de filas deja que un punto intermedio de la curva sirva para predecir a sus vecinos.
- La hoja y la velocidad son condiciones del ensayo. Si el reparto mezcla filas de la misma curva en entrenamiento y validación, el modelo ve el mismo régimen dos veces.
- Mapping y surging son protocolos distintos. Unirlos sin una variable de protocolo confunde dos diseños experimentales.
- Rellenar la celda vacía de velocidad es una asignación del diseño experimental. Hay que guardarla como tal, distinta de un número que estuviera en el Excel.
- Pasar `GVF0` de porcentaje a fracción es una conversión. No se hace en esta actividad.
- Calcular QG desde Qgd y desde el mismo caudal que luego se usa como entrada repetiría información.

La validación futura tiene que separar curvas o condiciones completas, no filas sueltas de una misma curva. Esta actividad no elige todavía el esquema concreto.

## Cierre en la actividad 2.12

Los conteos de pares completos de esta auditoría se reprodujeron sin discrepancia al escribir `data/processed/mapping_long.csv` y `data/processed/surging_long.csv`. El procedimiento está en `docs/normalizacion_datos.md`.
