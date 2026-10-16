# Resultados de la actividad 2.14

Los capítulos 1 a 16 conservan el informe de la fase B, con sus cifras originales. Esa fase quedó cerrada después de 26 pruebas automatizadas correctas y de la ejecución completa del cuaderno con nbconvert. El capítulo 17 es la fase C. El capítulo 18 es la fase D. No hay un modelo definitivo y la actividad 2.14 sigue abierta. La fase E no está iniciada.

La fase A permanece en la versión `2.14-A`. Una segunda ejecución de `evaluar_protocolo`, sobre los CSV originales, reprodujo la tabla ya publicada. No se cambió la métrica, la rejilla de alpha, el grado ni un pliegue. El registro ejecutable es `notebooks/04_entrenamiento_evaluacion_modelos.ipynb`. Las funciones están en `src/esp_datascience/entrenamiento.py`.

## 1. Introducción

Se predice `dp2_3_psi`, leído como el incremento de presión de la etapa 3, en psi, con la certeza media del diccionario. No es la presión absoluta. Mapping y surging son ensayos distintos y no se ajustan juntos.

M1 es la regresión lineal múltiple. M2 es el polinomio de grado 2 con cresta. La comparación pregunta si esa curvatura, regularizada, reduce el error absoluto medio sobre curvas que el ajuste no vio.

## 2. Hipótesis

- H0: M2 no mejora el error absoluto medio de M1.
- H1: M2 reduce ese error sobre curvas independientes.

Orientan la lectura. El protocolo no fijó una prueba de significación, así que un MAE menor no rechaza H0 en sentido formal. La métrica principal es el MAE en psi con igual peso por curva. ΔMAE = MAE(M2) − MAE(M1). Un valor negativo indica menor error de M2 en esa curva.

## 3. Materiales y métodos

Los datos son los CSV de la actividad 2.12. Mapping tiene 570 filas y 30 curvas. Surging tiene 387 filas y 18 curvas. El objetivo y los predictores salen del diccionario y de la fase A.

En mapping entran el caudal de líquido en bpd, el indicador de agua, el Qgd técnico, la velocidad en rpm y la presión del separador en psig. El Qgd medido sigue vacío en las 87 filas de agua. El cero existe solo en la copia que ve el estimador y no es una medición. En surging entran GVF0 en porcentaje, la fracción de QBEP como número ordenado, la velocidad y la presión del separador. Qgd y GVF0 no son la misma variable.

No entran el identificador de curva, la fila, el archivo ni `origen_velocidad`.

## 4. Protocolo de validación

Huella de mapping: `f35be865a01a6255cc08afdccb96863184ad394a550d9a5249d42b4041a8d948`.

Huella de surging: `71c4818c4b3a5bce0d363c5df658e04141ce1c1301e72f754d5805a52c9dc742`.

Tres pliegues externos. Cada curva es prueba una sola vez y no se parte. El anillo interno tiene cuatro cortes en mapping y tres en surging, solo sobre las curvas de entrenamiento. Alpha se elige en ese anillo, entre 0,01, 0,1, 1, 10 y 100, por el MAE interno con igual peso por curva. El grado queda en 2. La prueba externa no entra en la escala, en el polinomio ni en la elección de alpha.

El alcance es predecir una curva nueva cuyas velocidad, presión y condición ya aparecen en otras curvas del entrenamiento. No es una prueba de extrapolación.

## 5. Descripción matemática

M1, con predictores x1…xp:

ŷ = β0 + β1 x1 + … + βp xp.

ŷ es el incremento predicho, en psi. β0 es el intercepto cuando todos los predictores valen cero, un punto que el ensayo no visita. βj es el cambio de ŷ asociado a una unidad de xj con los demás predictores fijos. El residuo es predicción menos medición.

M2 añade cuadrados y productos, los centra y los escala con la media y la desviación del entrenamiento de ese ajuste, y penaliza la suma de coeficientes al cuadrado con alpha. El intercepto no se penaliza. Esos coeficientes no son una ley de la etapa: viven en el espacio escalado, y el cuadrado del indicador de agua repite al indicador. Ese término repetido se conserva. No se quitó para mejorar el error.

## 6. Implementación y entrenamiento

El orden de M2 es fijo: preparar, polinomio de grado 2 sin columna de unos, quitar columnas idénticamente nulas, escalar, cresta con solucionador SVD. En mapping la única columna nula es el producto `es_monofasica qgd_tecnico`, que vale cero por la codificación del agua. La máscara se aprende en el entrenamiento y se aplica igual a la prueba. En surging no se quita ninguna columna.

En mapping los tres pliegues eligen alpha = 0,1. En surging eligen 0,01, 1 y 0,01. No se refinó la rejilla después de ver el error externo.

El error de entrenamiento no es generalización. En mapping, el MAE de entrenamiento de M2 ronda 1,27 psi y el externo es 1,364 psi. En el pliegue 0 de surging, M2 separa 0,702 psi de entrenamiento y 1,335 psi externos. Ese externo sigue por debajo de los 2,468 psi de M1 en el mismo pliegue.

## 7. Métricas externas

MAE, RMSE y sesgo dan el mismo peso a cada curva. El RMSE de la tabla es la media de los RMSE de cada curva. No es el RMSE de todas las filas juntas. R² sí usa las observaciones externas juntas, así que las curvas largas pesan más. El MAE por fila es secundario.

| Protocolo | Modelo | MAE por curva (psi) | RMSE por curva (psi) | Sesgo (psi) | R² |
|---|---|---:|---:|---:|---:|
| Mapping | M1 | 3,999 | 4,865 | 0,043 | 0,543 |
| Mapping | M2 | 1,364 | 1,707 | 0,025 | 0,940 |
| Surging | M1 | 2,312 | 2,734 | 0,136 | 0,894 |
| Surging | M2 | 1,114 | 1,353 | 0,146 | 0,962 |

Una cuenta independiente, fila por curva y luego promedio, reproduce esas cifras. El RMSE global, que no es la métrica del protocolo, es otro número: 5,930 psi y 2,154 psi en mapping, y 2,709 psi y 1,633 psi en surging, para M1 y M2. En mapping la diferencia con el RMSE por curva pasa de 1 psi. Confundirlos cambiaría la lectura.

El MAE por fila, secundario, es 4,382 psi y 1,462 psi en mapping, y 2,132 psi y 1,225 psi en surging.

## 8. Comparación estadística descriptiva

La media de ΔMAE, sin redondear los MAE antes de restar, es −2,634 psi en mapping y −1,199 psi en surging. La mediana es −2,883 psi y −0,902 psi. El mínimo es −5,139 psi y −3,378 psi. El máximo es +0,451 psi y +0,265 psi. M2 tiene menor MAE en 29 de 30 curvas de mapping y en 17 de 18 de surging.

La resta de los MAE ya redondeados a tres decimales no cae en la misma milésima. La media que se cita es la de las diferencias por curva.

Las dos curvas en que M2 no mejora son `150psig|1800|Single Phase` (0,892 psi frente a 1,343 psi) y `150psig|3500|0.75Qbep` (1,024 psi frente a 1,290 psi).

Esto describe estas particiones. No es un intervalo de confianza ni un rechazo formal de H0.

## 9. Análisis físico de las predicciones

Las predicciones se evaluaron en los caudales y GVF0 medidos. No se alargó la abscisa. La media por curva acompaña el salto de velocidad: en mapping, cerca de 4,3 psi a 1800 rpm y de 15,4 psi a 3500 rpm, en la medición y en los dos modelos. El coeficiente lineal de la velocidad, unos 0,010 psi/rpm en los tres pliegues de mapping, no es una ley de afinidad. El de Qgd técnico ronda −190 psi por unidad de ese código, cerca de −1,9 psi por cada 0,01. El cero técnico no es un Qgd medido, y el coeficiente no aísla un efecto.

Un MAE menor no vuelve coherente toda la curva. R² alto no identifica un mecanismo. Los coeficientes de M2 no se leen como efectos físicos.

## 10. Diagnóstico de valores negativos

Ninguna medición de estos CSV es negativa. El mínimo medido es 0,080 psi en mapping y 0,383 psi en surging. Una predicción negativa es un resultado matemático del modelo en una fila medida. No se declara imposible en toda condición de una bomba, y tampoco se observa en este experimento. No se reemplazó por cero.

| Protocolo | M1 | M2 | Mínimo de M2 (psi) |
|---|---:|---:|---:|
| Mapping | 1 | 22 | −7,292 |
| Surging | 34 | 12 | −6,230 |

El detalle de cada fila está en `docs/derivados/predicciones_negativas_fase_b.csv`. Ese archivo es un derivado. `es_medicion` es falso. No sustituye a los CSV.

En mapping, la única predicción negativa de M1 está en `150psig|1800|Qgd=0.015`, en el caudal más alto de esa curva, 2247 bpd. La medición es 0,353 psi y la predicción es −0,207 psi. Las 22 de M2 caen en un extremo de la abscisa de su curva, con fracción 0 o 1. Las mediciones de esas filas van de 0,147 psi a 1,862 psi. El mínimo, −7,292 psi, no aparece donde la etapa todavía entrega decenas de psi. Aparece donde el incremento medido ya es pequeño y el polinomio se curva en el borde del tramo observado.

En surging las 34 predicciones negativas de M1 están a 1800 rpm. El mínimo es −8,184 psi. Solo 14 de esas 34 están en el 10 % final de la abscisa de su curva: el resto está en la parte alta de GVF0, no únicamente en el último punto. Las mediciones van de 0,383 psi a 2,290 psi. La recta en GVF0, con pendiente cercana a −1,2 psi por punto porcentual, cruza cero cuando el gas es alto y la ordenada de ese bloque no alcanza. M2 reduce el conteo a 12 y el mínimo queda en −6,230 psi. Ocho de esas doce están en el extremo de la curva. Diez son a 1800 rpm y dos son a 3500 rpm, en el bloque QBEP. La curvatura no elimina el cruce.

## 11. Comportamiento de las curvas monofásicas

Hay seis curvas de agua. Ordenadas por caudal, la medición no sube en ningún paso sucesivo. M1 tampoco: dentro de una curva de agua solo cambia el caudal, y su coeficiente es negativo. M2 sí sube en tramos locales de las seis.

Spearman compara el orden de los caudales con el orden de las presiones. Un valor de −1 dice que el orden es estrictamente inverso. Un valor negativo menor en magnitud, como −0,655, dice que la tendencia de los rangos sigue siendo a la baja, aunque algunos pasos suban. No equivale a mirar cada diferencia de un punto al siguiente.

| Curva | Spearman de M2 | Subidas de la medición | Subidas de M1 | Subidas de M2 |
|---|---:|---:|---:|---:|
| `100psig\|1800\|Single Phase` | −0,950 | 0 | 0 | 1 |
| `100psig\|3500\|Single Phase` | −0,913 | 0 | 0 | 3 |
| `150psig\|1800\|Single Phase` | −0,915 | 0 | 0 | 2 |
| `150psig\|3500\|Single Phase` | −0,849 | 0 | 0 | 5 |
| `50psig\|1800\|Single Phase` | −0,842 | 0 | 0 | 2 |
| `50psig\|3500\|Single Phase` | −0,655 | 0 | 0 | 7 |

El caso `50psig|3500|Single Phase` es el más marcado. M2 tiene siete subidas. La mayor es de 5,248 psi, entre 289 bpd y 717 bpd: la predicción pasa de 19,661 psi a 24,909 psi, mientras la medición pasa de 31,210 psi a 31,146 psi. El polinomio dobla el arranque de la curva de agua. No se impuso una pendiente negativa para corregirlo.

## 12. Análisis del gas

Comparar la presión media de dos curvas con distinto Qgd mezcla caudales que no coinciden. Para no hacer eso, se interpoló la medición y las predicciones ya hechas en el punto medio del caudal común a cada hoja y velocidad. Esa interpolación es descriptiva. No es una predicción nueva y no entra al ajuste. No se evaluó fuera del tramo en que todas las curvas de ese grupo tienen datos.

En los seis grupos, en ese caudal común, la medición baja al subir el Qgd. M1 y M2 también bajan en esos seis puntos. M1 queda por debajo de la medición. M2 se acerca más al nivel medido y, a 3500 rpm y Qgd = 0,01, puede quedar por encima. Eso es una coincidencia de dirección en un caudal interior al soporte común. No identifica un régimen ni demuestra una causa.

El resumen anterior, que contaba subidas de la presión media de la curva, no fija el caudal. A 3500 rpm esa media sube en uno de cuatro pasos del Qgd. No contradice la lectura en el caudal común: son preguntas distintas.

En surging, dentro de cada curva, GVF0 es la abscisa. La medición y las dos predicciones tienen asociación de Spearman negativa. En las predicciones llega a −1 en las 18 curvas: a lo largo del gas medido, la predicción no se da la vuelta. El sesgo sí cambia con el bloque de líquido. En M1 es +1,207 psi en 0,75 de QBEP, −0,103 psi en 1,25 y −0,697 psi en QBEP. En M2 es +0,423 psi, +0,361 psi y −0,348 psi. El error absoluto bajó. El signo del sesgo entre bloques no desapareció.

## 13. Análisis de sesgo

El sesgo medio por curva puede ser pequeño porque unas curvas quedan altas y otras bajas.

| Protocolo | Modelo | Sesgo medio (psi) | Curvas altas | Curvas bajas | Media de las altas (psi) | Media de las bajas (psi) |
|---|---|---:|---:|---:|---:|---:|
| Mapping | M1 | 0,043 | 17 | 13 | 0,766 | −0,902 |
| Mapping | M2 | 0,025 | 15 | 15 | 0,440 | −0,390 |
| Surging | M1 | 0,136 | 6 | 12 | 2,370 | −0,981 |
| Surging | M2 | 0,146 | 11 | 7 | 0,778 | −0,849 |

En mapping, M1 y M2 quedan por encima a 1800 rpm (0,154 psi y 0,151 psi) y por debajo a 3500 rpm (−0,031 psi y −0,059 psi). Entre presiones, M1 pasa de 0,001 psi a 50 psig a 0,318 psi a 100 psig y a −0,191 psi a 150 psig. M2 pasa de 0,121 psi a 0,013 psi y a −0,058 psi.

En las filas de mapping cuyo incremento medido está en el cuartil más bajo, hasta 4,374 psi, el MAE por fila de M1 es 4,961 psi y el sesgo es +4,450 psi: la recta se queda alta donde la medición es pequeña. M2 tiene ahí un MAE por fila de 1,122 psi y un sesgo de +0,105 psi. Ese cuartil no es la métrica del protocolo. Muestra que el sesgo global no resume el error en los incrementos chicos.

En surging, en el cuartil bajo hasta 4,398 psi, M1 tiene sesgo −0,911 psi, coherente con las predicciones que cruzan a negativo. M2 tiene sesgo −0,110 psi.

## 14. Limitaciones

- Mapping y surging no comparten la variable de gas ni el recorrido experimental.
- El ensayo es la bomba TE-2700, con agua y aire, sin isopropanol, a 1800 y 3500 rpm y a 50, 100 y 150 psig.
- Los CSV no cubren otros regímenes, otras velocidades ni otras bombas.
- En mapping, 384 filas tienen la velocidad asignada por el diseño, no leída en la celda. No se repitió el ajuste sin esas filas: el dominio pasaría a una sola presión.
- Qgd y GVF0 no son intercambiables.
- La prueba es una curva nueva dentro de condiciones que el entrenamiento ya vio. No demuestra extrapolación.
- Un MAE menor no garantiza que la curva predicha respete la forma medida. El caso de agua a 50 psig y 3500 rpm lo muestra.
- Un R² alto no valida un mecanismo.
- La regla de superioridad de la actividad 2.13 pide, además, un sesgo que no cambie de signo y la repetición sin la velocidad de diseño. Esas condiciones no se cumplen aquí.
- La comparación con la recta por condición, el bosque y el cociente de agua no está hecha.

## 15. Conclusiones provisionales

Sobre las curvas dejadas fuera, M2 tiene menor MAE y menor RMSE por curva que M1 en los dos protocolos. La diferencia pareada es negativa en casi todas las curvas. H0 no describe ese resultado. No se rechaza con una prueba que el protocolo no definió, y no se nombra a M2 ganador.

El sesgo medio es pequeño porque se cancela entre curvas. El polinomio cruza a incrementos negativos en el borde del caudal o en GVF0 alto, donde la medición ya es baja, y dobla curvas de agua que en el archivo solo bajan. Esas limitaciones quedan escritas. No se corrigieron con una restricción nueva.

## 16. Estado de cierre de la fase B

La fase B está desarrollada, vuelta a ejecutar y documentada. Los datos originales y las huellas no cambiaron. Las predicciones negativas están identificadas. Las curvas de agua y el sesgo están desglosados.

La fase B queda cerrada con ese registro: 26 pruebas automatizadas, las de `tests/test_normalizacion.py`, `tests/test_particiones.py` y `tests/test_entrenamiento.py`, terminaron correctamente, y el cuaderno se ejecutó completo con nbconvert. Ese cierre no cierra la actividad 2.14. La fase C está en el capítulo 17.

## 17. Fase C — M3, M4 y M5

### 17.1 Objetivo e hipótesis

La fase C estima los candidatos que la actividad 2.13 dejó después de la recta y el polinomio. El protocolo sigue siendo `2.14-A`. No se movió un pliegue, no se cambió la métrica principal y no se reajustaron M1 ni M2 con otra regla. Una ejecución nueva de `evaluar_protocolo` reprodujo el MAE por curva de la fase B: 3,999 psi y 1,364 psi en mapping; 2,312 psi y 1,114 psi en surging.

Las hipótesis se escribieron antes de leer el error externo:

- H3. Una recta propia de cada condición experimental puede reducir el error que viene de mezclar curvas distintas, y puede perder generalización cuando esa condición tiene pocos experimentos.
- H4. Un bosque de árboles de profundidad limitada puede representar curvaturas e interacciones que la recta y el polinomio de grado 2 no escriben de forma explícita.
- H5. En mapping, el cociente entre el incremento de presión con gas y el de la curva de agua, a caudal, velocidad y presión de separador comparables, puede describir el efecto del gas si esa agua está disponible sin mezclar entrenamiento y prueba.

Estas frases no son el resultado. El resultado está en las tablas de este capítulo.

### 17.2 Modelos

M3 ajusta una regresión lineal distinta para cada condición, solo con las curvas de entrenamiento de esa condición. En mapping la condición es `Single Phase` o el valor de Qgd. Dentro de la condición, los predictores posibles son el caudal de líquido, la velocidad y la presión del separador. Entra en la recta solo el que toma al menos dos valores distintos en ese entrenamiento, y el caudal tiene que ser uno de ellos. Qgd y el indicador de agua son constantes dentro de la condición, así que no tienen pendiente. En surging la condición es la fracción de QBEP: 0,75, 1 y 1,25. GVF0 sigue siendo el gas continuo y entra como predictor, junto con la velocidad y la presión del separador cuando varían. El identificador de curva no entra. Si una condición de prueba no fuera estimable, sus filas quedarían sin predicción. No hay un modelo global de respaldo. En estas particiones todas las condiciones externas fueron estimables.

La ecuación de una condición c, con el conjunto J_c de predictores identificables, es

ŷ = β0,c + Σ βj,c xj, para j en J_c.

M4 es un `RandomForestRegressor` de scikit-learn. Usa las mismas entradas que M1, incluida la copia técnica de Qgd en el agua. La semilla es 214, `n_jobs` es 1 y `max_features` es 1,0: entran todos los predictores autorizados y no se buscó un subconjunto. Antes de ver el error externo se fijó `n_estimators` en 100. La rejilla buscada, solo con el MAE interno por curva, es `max_depth` en {3, 5, 7} y `min_samples_leaf` en {3, 5, 10}. Si dos combinaciones empatan a menos de 10⁻⁹ psi, se queda la de menor profundidad y, dentro de ella, la de hoja mínima más grande. No se añadió otro hiperparámetro después de ver la prueba.

`n_estimators` es el número de árboles cuyo promedio es la predicción. `max_depth` limita cuántos cortes sucesivos puede hacer un árbol. `min_samples_leaf` exige un mínimo de observaciones en cada hoja y así frena una hoja que coincida con un solo punto. `random_state` fija el muestreo bootstrap para que la misma tabla dé el mismo bosque.

M5 es solo de mapping. En cada punto de gas cuyo caudal cae dentro de la curva de agua de la misma hoja y la misma velocidad, y solo si esa agua está en el entrenamiento, se calcula

R = ΔP_gas / ΔP_agua.

ΔP_agua se interpola en el caudal de líquido. Fuera del mínimo y el máximo medidos de esa agua no hay valor. La relación ajustada, solo con puntos de gas autorizados, es R̂ = β0 + β1 Qgd. La predicción en psi es R̂ por la presión de agua interpolada. No es la presión normalizada de Zhu y Zhang (2018): aquella usa la densidad de la mezcla, que estos archivos no traen. Una curva entra en el MAE de M5 solo si todos sus puntos tienen interpolación. No se rellenan los huecos. Las curvas de agua de prueba no se predicen y no se usan como referencia.

### 17.3 Factibilidad de M3

En el entrenamiento externo, las condiciones raras de mapping tienen dos curvas, una sola velocidad y dos presiones. La velocidad no recibe coeficiente. La presión de la curva de prueba de esa condición no está entre las dos presiones de entrenamiento: la predicción usa la pendiente de presión fuera de los valores vistos en esa condición. Eso ocurre en 18 de las 30 curvas de mapping. Qgd = 0,01 y `Single Phase` sí tienen las dos velocidades y las tres presiones en el entrenamiento de cada pliegue.

En surging, cada fracción tiene cuatro curvas de entrenamiento, las dos velocidades y dos de las tres presiones. La presión de las dos curvas de prueba no está en el entrenamiento de esa fracción. Las 18 curvas quedan marcadas con esa extrapolación. Aun así la condición es estimable: hay pendiente de GVF0, de velocidad y de presión.

En el anillo interno de mapping, 36 de 54 bloques de condición tienen una sola curva de entrenamiento. Siguen siendo estimables porque el caudal varía, pero entonces la velocidad y la presión no tienen coeficiente. M3 no elige hiperparámetros con ese anillo. El dato queda como límite de lo delgada que es una condición cuando se aparta una curva más. Ningún bloque interno quedó sin estimación. No se cambiaron los pliegues para evitarlo.

### 17.4 Hiperparámetros de M4

El MAE interno eligió, en mapping, profundidad 7 y hoja mínima 3 en los tres pliegues. En surging eligió profundidad 5 y hoja mínima 3 en el pliegue 0, y profundidad 7 y hoja mínima 3 en los pliegues 1 y 2. En mapping, esa esquina de la rejilla tenía un MAE interno de cerca de 1,39 psi, 1,26 psi y 1,37 psi, frente a cerca de 2,8 psi a 3,0 psi en la esquina más rígida. No se amplió la profundidad después de ver el error externo. El tope de la rejilla puede estar activo en mapping. En surging el pliegue 0 muestra que el procedimiento no elige siempre la combinación más flexible.

### 17.5 Cobertura y métricas externas

El MAE, el RMSE y el sesgo son medias sin ponderar de las curvas. R² usa las observaciones externas reunidas. La cobertura es completa en M1, M2, M3 y M4.

| Protocolo | Modelo | MAE por curva (psi) | RMSE por curva (psi) | Sesgo (psi) | R² | Cobertura |
|---|---|---:|---:|---:|---:|---|
| Mapping | M1 | 3,999 | 4,865 | 0,043 | 0,543 | 30/30 |
| Mapping | M2 | 1,364 | 1,707 | 0,025 | 0,940 | 30/30 |
| Mapping | M3 | 3,783 | 4,488 | −0,153 | 0,591 | 30/30 |
| Mapping | M4 | 1,044 | 1,546 | −0,007 | 0,937 | 30/30 |
| Surging | M1 | 2,312 | 2,734 | 0,136 | 0,894 | 18/18 |
| Surging | M2 | 1,114 | 1,353 | 0,146 | 0,962 | 18/18 |
| Surging | M3 | 2,041 | 2,486 | 0,350 | 0,895 | 18/18 |
| Surging | M4 | 0,754 | 0,963 | 0,041 | 0,972 | 18/18 |

Las cifras de M1 y M2 son las de la fase B, reproducidas en esta ejecución. El RMSE de la tabla es la media por curva, no el RMSE global.

La diferencia pareada es el MAE del candidato menos el MAE de la referencia, en las mismas curvas.

En mapping, M3 queda por debajo de M1 en 12 de 30 curvas. La media de esas diferencias es −0,215 psi y la mediana es +0,054 psi: la media mejora por unas pocas curvas, no por el conjunto. M3 queda por debajo de M2 en 4 de 30 curvas. M4 queda por debajo de M1 en las 30 curvas, con media −2,955 psi, y por debajo de M2 en 21 de 30, con media −0,321 psi.

En surging, M3 queda por debajo de M1 en 9 de 18 curvas, con media −0,271 psi y mediana −0,042 psi. Queda por debajo de M2 en 5 de 18. M4 queda por debajo de M1 en 17 de 18 curvas. La excepción es `150psig|3500|0.75Qbep`, donde el MAE de M4 supera al de M1 en 0,341 psi. M4 queda por debajo de M2 en 15 de 18 curvas, con media −0,360 psi.

### 17.6 M5 y su cobertura

En cada pliegue, las 8 curvas de gas de prueba tienen su agua en el entrenamiento. De las 16 curvas de gas de entrenamiento, solo 8 tienen el agua también en el entrenamiento. Las otras 8 tienen el agua reservada en la prueba y no entran al ajuste. Hay 2 curvas de agua en cada prueba. M5 no las predice.

El ajuste fue posible en los tres pliegues, con 139, 148 y 140 puntos y 8 curvas de gas autorizadas. Los interceptos de R fueron 0,916, 0,922 y 0,886. Las pendientes respecto de Qgd fueron −8,186, −7,437 y −6,837. El signo es el de una relación que baja cuando el código de gas sube. Eso describe el ajuste. No demuestra que la fórmula sea el mecanismo de la bomba.

Solo 5 de 30 curvas tienen todos sus caudales dentro del agua autorizada, y las cinco son de 50 psig: `50psig|1800|Qgd=0.01`, `50psig|1800|Qgd=0.015`, `50psig|3500|Qgd=0.02`, `50psig|3500|Qgd=0.04` y `50psig|3500|Qgd=0.05`. Son 89 filas. Hay predicción puntual en 427 de 570 filas, pero esas filas de curvas incompletas no entran al MAE ni se completan con un valor inventado.

En esas 5 curvas, y solo en ellas, el MAE por curva es:

| Modelo | MAE por curva (psi) | RMSE por curva (psi) | Sesgo (psi) | R² |
|---|---:|---:|---:|---:|
| M1 | 3,080 | 3,734 | −0,423 | 0,677 |
| M2 | 1,048 | 1,290 | −0,101 | 0,961 |
| M3 | 3,381 | 4,043 | 0,235 | 0,652 |
| M4 | 1,206 | 1,500 | 0,607 | 0,950 |
| M5 | 2,078 | 2,885 | 0,204 | 0,828 |

Esas cifras no se comparan con el MAE de las 30 curvas. En el subconjunto que M5 alcanza, su error queda entre el de M1 y el de M2. No cubre 100 psig, 150 psig ni las curvas de agua.

### 17.7 Error de entrenamiento y error externo

En M3 el MAE de entrenamiento y el externo quedan cerca. En mapping, por pliegue, el de entrenamiento es 3,693 psi, 3,571 psi y 3,497 psi, y el externo es 3,627 psi, 3,826 psi y 3,897 psi. En surging son 1,847 psi, 1,731 psi y 1,834 psi frente a 1,916 psi, 2,153 psi y 2,055 psi. La recta por condición no memoriza el entrenamiento. Su límite está en la forma lineal y en la presión que no vio dentro de la condición.

En M4 el error sobre las mismas curvas de entrenamiento es más bajo que el externo, y el MAE interno que eligió el hiperparámetro es más alto que el externo. En mapping, las medias de los tres pliegues son, en ese orden, cerca de 0,75 psi, 1,04 psi y 1,34 psi. En surging, cerca de 0,39 psi, 0,75 psi y 1,44 psi. El bosque ajusta las curvas de entrenamiento con más holgura de la que luego muestra fuera. El error externo de esta partición no superó la cifra con la que se eligió la rejilla. Esa diferencia no autoriza a profundizar los árboles después de haber visto la prueba.

### 17.8 Diagnóstico físico

No se sustituyó ninguna predicción negativa por cero y no se obligó a ninguna curva a ser decreciente.

M3 tiene 4 predicciones negativas en mapping, todas en agua a 1800 rpm y en la zona alta del caudal. La más baja es −1,897 psi en `100psig|1800|Single Phase`, a 2349 bpd, donde la medición es 0,543 psi. Tres de esas cuatro filas están en el extremo de su curva; la cuarta está cerca, con fracción de abscisa 0,89. En surging hay 27 predicciones negativas, todas a 1800 rpm. La más baja es −13,993 psi en `150psig|1800|0.75Qbep`, con GVF0 de 19,141 % y medición de 0,383 psi. Varias no están en el extremo de la curva. La lista está en `docs/derivados/predicciones_negativas_fase_c.csv`. No son mediciones.

M4 no produjo predicciones negativas. En mapping el mínimo es 0,451 psi y el máximo 28,706 psi. En surging el mínimo es 1,227 psi y el máximo 27,474 psi. Un bosque promedia valores de entrenamiento. Con mediciones positivas, la predicción se queda dentro del rango que las hojas vieron. Por eso no llega al mínimo medido de surging, 0,383 psi, ni al máximo medido de mapping, 31,210 psi. Esa contención no es una comprensión de la bomba. Es una restricción del promedio de las hojas.

En las seis curvas de agua, la medición no tiene pasos ascendentes. M3 tampoco: la pendiente de caudal del agua es negativa en los tres pliegues y, dentro de una curva, la velocidad y la presión no cambian. En Qgd = 0,015 y en Qgd = 0,04 la pendiente de caudal cambia de signo entre pliegues, así que M3 no garantiza una curva de gas decreciente. M4 tiene pasos ascendentes en las seis curvas de agua. El caso mayor es `50psig|3500|Single Phase`: Spearman −0,549 y cuatro subidas. Entre 288,8 bpd y 717,1 bpd la predicción pasa de 2,121 psi a 13,412 psi, una subida de 11,291 psi, mientras la medición pasa de 31,210 psi a 31,146 psi. En ese primer punto, M3 predice 39,769 psi. Los dos modelos fallan el extremo de la misma curva, en sentidos distintos.

La media de las medias por curva distingue 1800 rpm de 3500 rpm. En mapping la medición da 4,338 psi y 15,403 psi. M3 da 4,240 psi y 15,213 psi. M4 da 4,292 psi y 15,422 psi. En surging la medición da 3,681 psi y 15,893 psi. M3 da 4,068 psi y 16,207 psi. M4 da 3,706 psi y 15,951 psi. Los dos modelos reproducen el orden de magnitud de esa diferencia. No son una ley de afinidad.

En el punto medio del caudal común de cada hoja y velocidad, la medición baja al subir Qgd en los seis grupos. M3 sube en cinco de esos seis. M4 sube en uno, el de 150 psig y 3500 rpm. La interpolación es descriptiva, no entra al ajuste y no identifica un régimen. Dentro de cada curva de surging, el coeficiente de GVF0 de M3 es negativo y el Spearman de la predicción con GVF0 es −1. M4 queda cerca de −1, pero no en todas las curvas: en `150psig|1800|1.25Qbep` es −0,977. La monotonía de M3 dentro de la curva sale de una recta con pendiente negativa, no de un mecanismo identificado.

El sesgo medio sigue cancelándose. En mapping, M3 tiene 15 curvas por encima y 15 por debajo, con medias de sesgo +0,633 psi y −0,939 psi. M4 tiene 13 y 17, con +0,752 psi y −0,587 psi. En surging, M3 tiene 12 y 6, con +1,005 psi y −0,960 psi. M4 tiene 7 y 11, con +0,565 psi y −0,293 psi. En mapping, el sesgo por curva de M4 en agua es −1,179 psi y en Qgd = 0,05 es +1,245 psi. El MAE de M3 en mapping es 1,527 psi a 1800 rpm y 5,288 psi a 3500 rpm.

### 17.9 Comparación provisional

H3 no queda respaldada como ventaja general. El MAE medio de M3 es algo menor que el de M1, pero la mediana pareada está cerca de cero y M2 tiene menor error en la mayoría de las curvas. La especialización, además, predice presiones de separador que esa condición no vio en el entrenamiento.

H4 queda como una reducción del MAE externo frente a M1 en casi todas las curvas y frente a M2 en la mayoría. Al mismo tiempo, el bosque dobla todas las curvas de agua, se aparta en más de 11 psi en un tramo de agua a 3500 rpm y ajusta el entrenamiento mejor de lo que predice fuera. Reproducir el orden de las velocidades no significa que el bosque entienda la hidráulica.

H5 es viable solo como referencia parcial. Se pudo calcular sin usar el agua de prueba, y solo en 5 curvas de 50 psig. En ese subconjunto no mejora a M2 ni a M4. No es un competidor de las 30 curvas.

No se nombra un ganador. La fase D es la que tiene la comparación con incertidumbre. No está iniciada.

### 17.10 Entorno

La ejecución usó el entorno `.venv` del laboratorio: Python 3.14.8, NumPy 2.5.4, pandas 3.0.6 y scikit-learn 1.9.1. La semilla es 214. El código de esta fase está en `src/esp_datascience/fase_c.py`. Las pruebas nuevas están en `tests/test_fase_c.py`. El cuaderno ejecutado de toda la actividad, de la fase A a la C, queda en `resultados/04_ejecucion_fase_c.ipynb`, separado del cuaderno fuente para no reescribir las salidas ya guardadas de la fase B.

### 17.11 Conclusión de la fase

M3, M4 y M5 quedaron estimados con el protocolo congelado. M3 y M4 cubren todas las curvas externas. M5 cubre cinco. Las predicciones negativas de M3 están listadas. Las curvas de agua y el sesgo están desglosados. M1 y M2 conservan sus cifras. No hay un modelo definitivo.

## 18. Fase D — Comparación científica e incertidumbre

### 18.1 Mantenimiento previo

Antes de esta comparación se cerró un `pd.ExcelFile` que las pruebas de normalización dejaban abierto. El cambio está solo en `tests/test_normalizacion.py`: los dos libros entran en un `with`, con las mismas hojas, `header=None` y las mismas funciones de normalización. `src/` no abre esos libros. Los cuadernos históricos no se reescribieron. Con las advertencias de recurso convertidas en error, las cuatro pruebas de normalización pasan. La batería completa deja de mostrar el archivo sin cerrar. Las huellas de los Excel y de los CSV no cambian. Este mantenimiento no reabre las fases A, B ni C.

### 18.2 Método

La fase D no reajusta M1–M5 ni mueve el protocolo `2.14-A`. La unidad es la curva. La diferencia pareada es el MAE del candidato menos el de la referencia.

El intervalo principal es un percentil del 95 % de la media de esas diferencias, con 10.000 réplicas y semilla 214, fijadas antes de leer el intervalo. Cada réplica extrae curvas con reemplazo y conserva el emparejamiento. Mapping y surging no se mezclan.

Ese intervalo describe la incertidumbre de remuestrear las curvas disponibles. No demuestra independencia completa entre curvas, generalización a otras bombas o condiciones, un mecanismo físico, ni que la selección interna de hiperparámetros haya sido inocua.

Hay tres variabilidades distintas. Dentro de una curva, los puntos comparten el mismo ensayo. Entre curvas cambia la condición, aunque pueden compartir hoja, velocidad y banco. Entre condiciones, la hoja y la velocidad agrupan varias curvas. El bootstrap principal mira la segunda. El de conglomerados mira la tercera y, con seis grupos, es una base limitada.

La regla de superioridad de la actividad 2.13 sigue siendo la que se escribió antes de ver el error. Los pesos de idoneidad de esa actividad, 25 % compatibilidad, 25 % fundamento físico, 20 % forma observada, 15 % validación, 10 % interpretabilidad y 5 % simplicidad, no se recalculan con el MAE. La matriz de notas de esta fase es otra cosa: se construyó después de ver los errores.

### 18.3 Precisión

| Protocolo | Modelo | MAE por curva (psi) | RMSE por curva (psi) | Cobertura |
|---|---|---:|---:|---|
| Mapping | M1 | 3,999 | 4,865 | 30/30 |
| Mapping | M2 | 1,364 | 1,707 | 30/30 |
| Mapping | M3 | 3,783 | 4,488 | 30/30 |
| Mapping | M4 | 1,044 | 1,546 | 30/30 |
| Surging | M1 | 2,312 | 2,734 | 18/18 |
| Surging | M2 | 1,114 | 1,353 | 18/18 |
| Surging | M3 | 2,041 | 2,486 | 18/18 |
| Surging | M4 | 0,754 | 0,963 | 18/18 |

Quitar la peor curva no cambia el orden de esas medias. En mapping la peor de M4 y de M2 es la misma agua, `50psig|3500|Single Phase`, con 4,023 psi y 3,221 psi.

### 18.4 Intervalos

Media de ΔMAE e intervalo del 95 % por curvas.

| Protocolo | Comparación | Media (psi) | Intervalo (psi) | Curvas que mejoran | Wilcoxon, p |
|---|---|---:|---|---:|---:|
| Mapping | M2 menos M1 | −2,634 | [−3,254, −2,015] | 29/30 | muy pequeño |
| Mapping | M3 menos M1 | −0,215 | [−0,676, 0,168] | 12/30 | 0,72 |
| Mapping | M4 menos M1 | −2,955 | [−3,694, −2,234] | 30/30 | muy pequeño |
| Mapping | M4 menos M2 | −0,321 | [−0,562, −0,081] | 21/30 | 0,013 |
| Mapping | M4 menos M3 | −2,740 | [−3,513, −1,977] | 29/30 | muy pequeño |
| Surging | M2 menos M1 | −1,199 | [−1,683, −0,768] | 17/18 | muy pequeño |
| Surging | M3 menos M1 | −0,271 | [−0,712, 0,103] | 9/18 | 0,42 |
| Surging | M4 menos M1 | −1,559 | [−2,120, −1,035] | 17/18 | muy pequeño |
| Surging | M4 menos M2 | −0,360 | [−0,588, −0,124] | 15/18 | 0,012 |
| Surging | M4 menos M3 | −1,287 | [−1,805, −0,822] | 17/18 | muy pequeño |


M3 frente a M2 queda por encima de cero en los dos protocolos: la recta por condición tiene más error que el polinomio. El intervalo de M4 frente a M2 también queda bajo cero en la sensibilidad por conglomerados. Seis conglomerados son pocos. El resultado dice que, en este reparto, la media pareada no se apoya en una sola hoja. No dice que las curvas sean independientes ni que el bosque entienda la bomba.

### 18.4.1 Alcance inferencial y multiplicidad de comparaciones

Las doce pruebas de Wilcoxon son exploratorias. La unidad es la curva. El contraste supone simetría de las diferencias pareadas alrededor de cero y excluye las diferencias nulas. Las curvas comparten banco, velocidad y procedimiento, así que el valor p no es la probabilidad de un experimento independiente. No había una corrección de multiplicidad en el protocolo. Un Bonferroni posterior, que multiplica cada valor p por 12 y lo corta en 1, no sustituye los originales y no se usa para elegir un modelo.

En M4 frente a M2 el valor p original es 0,013 en mapping y 0,012 en surging. Multiplicados por 12 quedan en 0,154 y 0,144. El intervalo por curvas de esa misma diferencia queda bajo cero. Las dos cuentas responden preguntas distintas. Los contrastes de M2 y de M4 frente a M1 siguen con valores p muy pequeños aun después de multiplicar por 12. M3 frente a M1 no se separa de cero.

**Seis conglomerados constituyen una base limitada para estimar incertidumbre de nivel superior.** En mapping, cada grupo de 1800 rpm tiene 4 curvas y cada grupo de 3500 rpm tiene 6. La media del remuestreo por conglomerados pondera más a 3500 rpm, porque promedia curvas y no grupos. En surging cada grupo tiene 3 curvas. No se dividieron condiciones para estrechar el intervalo.

Retirar un conglomerado completo es un diagnóstico posterior. No reajusta M1–M5. La media de M4 menos M2 sigue negativa en los seis retiros de cada protocolo. En mapping, la más cercana a cero es −0,232 psi, al quitar `100psig|3500`. En surging es −0,272 psi, al quitar `50psig|1800`.

### 18.5 Estabilidad

En mapping el MAE crece de 1800 a 3500 rpm en los cuatro modelos: M1 pasa de 1,430 psi a 5,711 psi, M2 de 0,636 psi a 1,850 psi, M3 de 1,527 psi a 5,288 psi y M4 de 0,436 psi a 1,449 psi. En surging el orden de las velocidades cambia: M1 y M3 tienen más error a 1800 rpm, y M2 y M4 a 3500 rpm.

M2 tiene menor MAE que M4 en todas las curvas de Qgd = 0,05 y en parte de Qgd = 0,015 y Qgd = 0,04. En surging, cada fracción tiene una curva de las seis en la que M2 es menor. El puesto global no es el puesto de cada condición.

### 18.6 Física

| Protocolo | Modelo | Predicciones negativas | Curvas | Mínimo (psi) |
|---|---|---:|---:|---:|
| Mapping | M1 | 1 | 1 | −0,207 |
| Mapping | M2 | 22 | 21 | −7,292 |
| Mapping | M3 | 4 | 3 | −1,897 |
| Mapping | M4 | 0 | 0 | 0,451 |
| Surging | M1 | 34 | 8 | −8,184 |
| Surging | M2 | 12 | 5 | −6,230 |
| Surging | M3 | 27 | 8 | −13,993 |
| Surging | M4 | 0 | 0 | 1,227 |

M4 no predice valores negativos porque promedia mediciones positivas. Tampoco llega al máximo medido de mapping ni al mínimo medido de surging.

En las seis curvas de agua, la medición, M1 y M3 no tienen pasos ascendentes. M2 y M4 sí, en las seis. El paso mayor de M4 es 11,291 psi en `50psig|3500|Single Phase`. El de M2, en la misma curva, es 5,248 psi.

En el caudal común, la medición, M1 y M2 no suben al aumentar Qgd. M4 sube en 1 de 6 grupos. M3 sube en 5 de 6. En surging, el Spearman de GVF0 con la presión es −1 en todas las curvas de M1, M2 y M3. En M4, tres curvas quedan por encima de −0,99; la menos negativa está cerca de −0,977.

El sesgo cambia de signo entre velocidades en mapping para M1, M2 y M4, y entre presiones para los cuatro. En surging el signo de la velocidad se mantiene positivo y el de la presión no.

### 18.7 Procedencia de la velocidad

| Hoja | Procedencia | Presión (psig) | Filas | Curvas |
|---|---|---:|---:|---:|
| 50psig | celda | 50 | 186 | 10 |
| 100psig | diseño experimental | 100 | 192 | 10 |
| 150psig | diseño experimental | 150 | 192 | 10 |

El contraste entre procedencias es el contraste entre 50 psig y las otras dos presiones. No se reajustó un modelo solo con la velocidad leída en la celda. Hacerlo dejaría fuera 100 y 150 psig y saldría del protocolo. La condición de 2.13 que pide repetir mapping sin esas filas queda no evaluable dentro de `2.14-A`.

### 18.8 M5

En las cinco curvas completas, el MAE por curva es 3,080 psi para M1, 1,048 psi para M2, 3,381 psi para M3, 1,206 psi para M4 y 2,078 psi para M5. No se compara con el MAE de las treinta curvas.

### 18.9 Dos matrices, no una

La matriz de 2.13 es anterior al entrenamiento. Puntúa idoneidad metodológica. Con sus pesos no hubo un candidato predictivo principal único. No se rellena con el MAE de la 2.14.

La matriz de la fase D es posterior. Cada nota discretiza una cifra continua. Los cortes de 1 psi y 10 psi para las subidas del agua, y los de −1 psi y −5 psi para las predicciones negativas, no son límites físicos. No hay en este estudio una referencia independiente que los fije. El corte de 10 psi queda entre el paso mayor de M2 (5,248 psi) y el de M4 (11,291 psi). Esa separación es una decisión del investigador después de ver los pasos.

| Criterio | Cifra continua | Nota | Cuándo se fijó la nota |
|---|---|---|---|
| Precisión | MAE por curva, en psi | Puesto de 3 a 0 | Después del error |
| Robustez | Fracción de curvas mejores que M1 | Esa fracción por 3 | Después del error |
| Agua | Pasos y mayor subida, en psi | 0, 1, 2 o 3 según 1 psi y 10 psi | Después de ver los pasos |
| Negativas | Conteo y mínimo, en psi | 0, 1, 2 o 3 según −5 psi y −1 psi | Después de ver los mínimos |
| Gas | Pasos al subir Qgd, o el peor Spearman | 0 a 3 | Después de ver las series |
| Lectura y simplicidad | Forma del estimador | M1: 3. M3: 2. M2: 1. M4: 0 | Por la definición del modelo, sin usar el MAE |

Los pesos escritos, no los de 2.13, son estos.

| Escenario | Precisión | Robustez | Agua | Negativas | Gas | Lectura | Simplicidad | Sentido |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Equilibrado | 1 | 1 | 1 | 1 | 1 | 1 | 1 | Cada criterio presente pesa igual |
| Precisión | 4 | 2 | 1 | 1 | 1 | 1 | 1 | Prioriza el MAE y la fracción de curvas |
| Tendencia observada | 1 | 1 | 4 | 2 | 3 | 1 | 1 | Prioriza agua, gas y predicciones negativas |
| Lectura y simplicidad | 1 | 1 | 1 | 1 | 1 | 4 | 4 | Prioriza la forma del modelo |

En surging no hay columna de agua. Ese peso se omite y el resto se divide por la suma que queda. En el escenario de tendencia, el agua pesa 4 de 13 en mapping. En surging la suma restante es 9, y el gas pasa de 3/13 a 3/9. La ponderación efectiva no es la misma. No se inventa una nota de agua para evitar ese reescalado.

Con las notas publicadas, en mapping el equilibrado, la tendencia y la lectura ponen primero a M1, y la precisión pone primero a M4. En surging, el equilibrado, la precisión y la tendencia ponen primero a M4, y la lectura pone primero a M1.

Al mover solo los cortes del agua, el primer puesto de mapping no cambia: con 5 psi, M2 y M4 reciben 0; con 15 psi, los dos reciben 1. Cambia el segundo puesto del escenario de tendencia, de M3 a M4, cuando el corte holgado sube la nota de agua de M4. El modo binario del gas, en el que cualquier subida anula la nota alta, deja primero a M1 en el equilibrado de mapping y segundo a M2, en lugar de M4.

Un corte holgado de las predicciones negativas, −10 psi y −5 psi, no se adopta. En surging, M1 y M2 pasan de la peor nota a la intermedia. La suma equilibrada de M2 queda igual a la de M4, y la de tendencia también. No aparece un ganador nuevo: es un empate de la nota discreta. La precisión sigue poniendo primero a M4 y la lectura sigue poniendo primero a M1. Las cifras que se conservan son el MAE, el paso en psi y el mínimo en psi.

### 18.10 Lectura de la fase

M4 tiene el mejor desempeño predictivo externo de este experimento. Su ventaja media frente a M2 queda bajo cero al remuestrear estas curvas, y también al retirar cualquier conglomerado de hoja y velocidad. Esa ventaja no es una ley de la bomba ni una prueba de mecanismo. El ajuste posterior de los doce valores p deja el contraste de M4 frente a M2 por encima de 0,05.

M1 y M3 conservan la caída punto a punto de las seis curvas de agua. M2 y M4 no. M2 tiene mejor MAE que M1 y que M3, y su mayor subida local en agua es menor que la de M4. M5 no cubre las treinta curvas. La matriz posterior no nombra un ganador: el primer puesto cambia con el peso. En surging, el corte holgado de las predicciones negativas empata a M2 con M4 en los escenarios equilibrado y de tendencia. La regla de 2.13 sigue sin cumplirse.

No es defendible seleccionar un ganador único. Precisión, consistencia con las curvas medidas, lectura matemática, validez de un mecanismo y generalización siguen siendo preguntas distintas.

La ejecución completa del cuaderno, de la fase A a la D, está en `resultados/04_ejecucion_fase_d.ipynb`. Los intervalos también están en `docs/derivados/intervalos_bootstrap_fase_d.csv`. La fase E no está iniciada. La actividad 2.14 no está cerrada.
