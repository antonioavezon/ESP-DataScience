# Resultados de la actividad 2.14, fase B

Auditoría de cierre de la fase B. No es el cierre de la actividad 2.14 y no inicia la fase C. No hay un modelo definitivo ni un modelo físicamente validado.

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

La fase B está desarrollada, vuelta a ejecutar y documentada. Los datos originales y las huellas no cambiaron. Las predicciones negativas están identificadas. Las curvas de agua y el sesgo están desglosados. La fase C no está iniciada.

La fase B queda técnicamente preparada para la revisión de cierre. La decisión de cerrarla corresponde a esa revisión. No es el cierre de la actividad 2.14.
