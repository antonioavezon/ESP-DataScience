# Informe de la actividad 2.14

Predicción del incremento de presión de una bomba electrosumergible en ensayos de agua y de agua con aire.

Este texto resume la actividad 2.14. No es el informe integral del proyecto de un modelo híbrido de física e inteligencia artificial. No implementa ese modelo ni abre la actividad siguiente.

## 1. Título y propósito

La actividad preguntó qué pueden reproducir, a partir de las curvas medidas, cinco estimadores del incremento de presión, y qué no puede sostenerse todavía como base de un modelo híbrido.

La variable es `dp2_3_psi`. En el diccionario del laboratorio se lee como el incremento de presión entre las tomas asociadas a la etapa 3, en psi, con certeza media. No es la presión absoluta, ni la presión de admisión, ni la presión de fondo, ni la altura manométrica de un pozo.

## 2. Resumen científico

Se usaron dos protocolos que no se mezclan. Mapping tiene 570 filas y 30 curvas. Surging tiene 387 filas y 18 curvas. La unidad de validación es la curva completa. El protocolo congelado es `2.14-A`.

El menor error absoluto medio por curva lo obtiene un bosque aleatorio de complejidad limitada: 1,044 psi en mapping y 0,754 psi en surging. Un polinomio de grado 2 con cresta queda en 1,364 psi y 1,114 psi. La recta global queda en 3,999 psi y 2,312 psi. La recta por condición queda en 3,783 psi y 2,041 psi.

La ventaja media del bosque frente al polinomio, en las mismas curvas, es −0,321 psi en mapping y −0,360 psi en surging. El intervalo percentil del 95 %, con 10.000 réplicas y semilla 214, queda bajo cero en los dos protocolos. Ese intervalo describe el remuestreo de estas curvas. No es una generalización a otras bombas. Un ajuste posterior de Bonferroni sobre doce contrastes exploratorios deja los valores p de esa comparación en 0,154 y 0,144. El intervalo y la prueba de rangos no responden la misma pregunta, y ninguno demuestra un mecanismo.

La recta global y la recta por condición conservan la caída punto a punto de las seis curvas de agua. El polinomio y el bosque no. Una referencia respecto del agua solo cubre cinco curvas de mapping, todas a 50 psig, con 2,078 psi de error en ese subconjunto. No hay un ganador científico único. La regla de superioridad escrita antes de ver el error no se cumple de forma conjunta.

## 3. Introducción

Una bomba electrosumergible eleva líquido desde un pozo. Cuando entra gas, la curva de presión puede degradarse. El artículo asociado a estos archivos estudia transiciones de patrón de flujo en una bomba experimental, no el cierre de un estimador de presión para cualquier pozo (Zhu et al., 2019). Los archivos usados son la serie sin isopropanol de ese conjunto (Zhu, 2019).

Esta actividad no modifica la bomba. Predice observaciones ya medidas. Un error menor no es una mejora operacional.

## 4. Contexto experimental

Los ensayos corresponden a una bomba TE-2700, agua y aire, sin isopropanol, a 1800 rpm y 3500 rpm, y a presiones de separador de 50 psig, 100 psig y 150 psig. Mapping recorre caudales de líquido a un código de gas Qgd fijo en cada curva. Surging recorre la fracción volumétrica de gas en la admisión, GVF0, a una fracción fija del caudal de mejor eficiencia.

Ese dominio no se extiende, con estos resultados, a otra bomba, otro fluido, otra velocidad ni a un pozo.

## 5. Datos y variables

| Símbolo | Lectura en esta actividad | Unidad | Certeza |
|---|---|---|---|
| `dp2_3_psi` | Incremento de presión de la etapa 3 | psi | Media. El rótulo del Excel no está en la tesis |
| `ql_bpd` | Caudal de líquido en mapping | bpd | La unidad se toma de la tesis; el Excel no imprime «bpd» |
| `qgd` | Código de gas de la curva de mapping | adimensional, como está en el archivo | Alta como etiqueta de bloque; no es un caudal de gas en bpd |
| `gvf0_porcentaje` | Fracción de gas en la admisión, surging | % | Media, por el sufijo del nombre |
| `velocidad_rpm` | 1800 o 3500 | rpm | Alta por el diseño; en parte de mapping la celda está vacía |
| `psep_psig` | Presión del separador | psig | La de la hoja |

En mapping, 186 filas de 50 psig tienen la velocidad leída en la celda. Las 384 filas de 100 psig y 150 psig la reciben del diseño experimental. Cada curva tiene una sola procedencia. No se puede separar el origen de la velocidad de la presión sin salir del dominio de tres presiones.

Mapping y surging no se apilan. No comparten la misma abscisa ni el mismo papel del gas.

## 6. Metodología

La curva, identificada por hoja, velocidad y condición, no se parte entre entrenamiento y prueba. Hay tres pliegues externos. En mapping quedan 10 curvas de prueba y 20 de entrenamiento. En surging, 6 y 12. La semilla es 214.

El error principal es el promedio, con igual peso, del error absoluto medio de cada curva:

\[
\mathrm{MAE} = \frac{1}{n_c}\sum_{i=1}^{n_c}\mathrm{MAE}_i
\]

\(n_c\) es el número de curvas. \(\mathrm{MAE}_i\) es el error absoluto medio dentro de la curva \(i\), en psi. No es el error absoluto medio de todas las filas juntas. El RMSE de las tablas es, del mismo modo, la media de los RMSE por curva. El sesgo es la media, por curva, de predicción menos medición. R² usa las observaciones externas reunidas y no es la métrica de selección.

La diferencia pareada en la curva \(i\) es

\[
\Delta\mathrm{MAE}_i = \mathrm{MAE}_i(\text{candidato}) - \mathrm{MAE}_i(\text{referencia}).
\]

Un valor negativo indica menor error del candidato en esa curva.

Los hiperparámetros que podían elegirse se eligieron en un anillo interno, sin las curvas de prueba. No se volvieron a elegir en esta síntesis.

## 7. Modelos evaluados

| Código | Estimador | Papel declarado antes del error externo |
|---|---|---|
| M1 | Regresión lineal múltiple | Piso de comparación |
| M2 | Polinomio de grado 2 con cresta (Hoerl y Kennard, 1970) | Curvatura regularizada; el grado quedó en 2 |
| M3 | Una recta por condición de gas | Especialización con la etiqueta ya escrita |
| M4 | Bosque aleatorio de 100 árboles (Breiman, 2001), profundidad y hoja mínima elegidas por el MAE interno | Único modelo de cortes de esta ronda |
| M5 | Cociente respecto de la curva de agua de la misma hoja y velocidad, solo mapping | Referencia parcial; no es la presión normalizada de Zhu y Zhang (2018), porque falta la densidad de la mezcla |

Las entradas de mapping son el caudal de líquido, una indicadora de agua, el código de gas, la velocidad y la presión del separador. En el agua, el código de gas entra al ajuste como cero técnico y el archivo conserva el hueco. Las de surging son GVF0, la fracción de QBEP, la velocidad y la presión del separador.

## 8. Diseño de validación

Las huellas de los pliegues son `f35be865a01a6255cc08afdccb96863184ad394a550d9a5249d42b4041a8d948` para mapping y `71c4818c4b3a5bce0d363c5df658e04141ce1c1301e72f754d5805a52c9dc742` para surging.

La actividad 2.13 fijó, antes de ver un error, que un modelo solo se llamaría superior si a la vez tenía menor MAE y menor RMSE que la recta del mismo protocolo, un sesgo que no cambiara de signo entre las dos velocidades ni entre las tres presiones, una repetición de mapping sin la velocidad asignada por el diseño, y la complejidad ya declarada. Si la diferencia de error era pequeña, se prefería el modelo más legible. Esa conjunción no se usa aquí como una puntuación nueva. Se comprueba y no se cumple.

## 9. Resultados cuantitativos

| Protocolo | Modelo | MAE (psi) | RMSE (psi) | Sesgo (psi) | R² | Curvas |
|---|---|---:|---:|---:|---:|---|
| Mapping | M1 | 3,999 | 4,865 | 0,043 | 0,543 | 30/30 |
| Mapping | M2 | 1,364 | 1,707 | 0,025 | 0,940 | 30/30 |
| Mapping | M3 | 3,783 | 4,488 | −0,153 | 0,591 | 30/30 |
| Mapping | M4 | 1,044 | 1,546 | −0,007 | 0,937 | 30/30 |
| Surging | M1 | 2,312 | 2,734 | 0,136 | 0,894 | 18/18 |
| Surging | M2 | 1,114 | 1,353 | 0,146 | 0,962 | 18/18 |
| Surging | M3 | 2,041 | 2,486 | 0,350 | 0,895 | 18/18 |
| Surging | M4 | 0,754 | 0,963 | 0,041 | 0,972 | 18/18 |

El sesgo positivo indica predicción por encima de la medición. En mapping el error de los cuatro modelos es mayor a 3500 rpm que a 1800 rpm. En surging, M1 y M3 fallan más a 1800 rpm, y M2 y M4 a 3500 rpm. M2 tiene menor MAE que M4 en las tres curvas de Qgd = 0,05. El puesto global no es el de cada condición.

En las cinco curvas que M5 cubre por completo, el MAE es 3,080 psi (M1), 1,048 psi (M2), 3,381 psi (M3), 1,206 psi (M4) y 2,078 psi (M5). Esas cinco cifras no se restan del MAE de las treinta curvas.

## 10. Incertidumbre

| Protocolo | M4 menos M2 | Intervalo del 95 % | Curvas en que M4 es menor |
|---|---:|---|---:|
| Mapping | −0,321 psi | [−0,562, −0,081] psi | 21 de 30 |
| Surging | −0,360 psi | [−0,588, −0,124] psi | 15 de 18 |

El intervalo es un percentil de la media de las diferencias por curva, no de las filas. Cada extracción conserva el par de modelos. Mapping y surging no se juntan. Hay dependencia: las curvas comparten banco, y en mapping los grupos de 3500 rpm tienen 6 curvas y los de 1800 rpm tienen 4. Seis conglomerados son una base limitada. Retirar cualquiera deja la media de M4 menos M2 bajo cero; la más cercana a cero es −0,232 psi en mapping y −0,272 psi en surging. Eso no crea una validación nueva.

Los valores p de Wilcoxon son exploratorios. Hay doce contrastes, las diferencias nulas se excluyen y no había una corrección fijada de antemano. Multiplicar por 12 los de M4 frente a M2 da aproximadamente 0,154 y 0,144. El bootstrap de la media y el rango con signo no estiman el mismo objeto. Varma y Simon (2006) y Cawley y Talbot (2010), leídos en su resumen durante la actividad 2.13, advierten que elegir un modelo con validación cruzada puede dejar demasiado optimista el error que luego se publica. El intervalo de esta actividad no descuenta por completo esa elección.

La comparación de M3 con M1 tiene un intervalo que incluye el cero en los dos protocolos.

## 11. Análisis físico

En las seis curvas de agua de mapping la medición baja al subir el caudal. M1 y M3 no tienen pasos ascendentes. M2 y M4 suben en las seis. El paso mayor de M4 es 11,291 psi y el de M2 es 5,248 psi, ambos en agua a 50 psig y 3500 rpm. Un corte de 10 psi, posterior y sin respaldo físico independiente, separa esas dos subidas. No es una ley.

M4 no produjo predicciones negativas. M1, M2 y M3 sí. En estos archivos el incremento medido es positivo. Un valor predicho negativo es una salida no observada aquí, no una demostración de que todo incremento negativo sea imposible en otra bomba. La ausencia de negativos en M4 sigue de promediar mediciones de entrenamiento que son positivas. El bosque tampoco alcanza el máximo medido de mapping ni el mínimo medido de surging.

A caudal de líquido común, la medición, M1 y M2 no suben al aumentar Qgd. M4 sube en uno de seis grupos de hoja y velocidad. M3 sube en cinco. En surging, el Spearman de GVF0 con la presión predicha es −1 en las 18 curvas de M1, M2 y M3. En M4 el peor es −0,977. Reproducir el orden de magnitud entre 1800 rpm y 3500 rpm no constituye una ley de afinidad.

M3 extrapola la presión del separador dentro de la condición en 18 de 30 curvas de mapping y en las 18 de surging. Su MAE medio frente a M1 es compatible con el remuestreo.

M5 ajusta, en el gas cuyo agua está en el entrenamiento, una recta del cociente de presiones respecto de Qgd. Las pendientes fueron negativas, del orden de −8 a −7. Describen ese ajuste. No identifican el mecanismo de la degradación. La referencia no usa el agua reservada para la prueba. La cobertura, cinco curvas de 50 psig, no alcanza para tratarla como predictor del protocolo.

Precisión, concordancia con la forma medida, lectura de la ecuación, validez de un mecanismo y extrapolación son preguntas distintas. El menor MAE no responde las otras cuatro.

## 12. Discusión científica

El candidato de mejor precisión en este experimento es M4, en los dos protocolos. El candidato de referencia interpretable sigue siendo M1, porque así se fijó antes del error: es el piso que los demás tenían que mejorar. El candidato no lineal de comparación, con una forma escrita de antemano, es M2. M4 se conserva como referencia de precisión, no como sustituto de esa forma. M5 queda como idea semiempírica exploratoria, no como modelo validado y no como un concepto que deba abandonarse solo porque esta fórmula cubre poco.

No se asignaron pesos nuevos para forzar un ganador. La matriz de notas de la fase D es posterior al error y cambia de puesto según el peso. La de 2.13 no se reescribió.

Estos estimadores predicen `dp2_3_psi` dentro de las curvas medidas. No estiman la presión de admisión, la de fondo ni un nivel dinámico. No detectan fallas. No hay etiquetas de anomalía en los archivos.

## 13. Limitaciones

1. Los datos son de una bomba experimental, la TE-2700.
2. Solo hay dos velocidades y tres presiones de separador, con agua y aire, sin isopropanol.
3. Mapping y surging no son el mismo experimento.
4. `dp2_3_psi` y `gvf0_porcentaje` tienen certeza media.
5. En mapping, la velocidad de 100 psig y 150 psig viene del diseño, no de la celda.
6. Las curvas comparten el banco de ensayo.
7. Treinta y dieciocho curvas no son una muestra de máquinas.
8. No hay otra bomba de contraste.
9. No hay datos de campo.
10. El resultado no se exporta fuera de las velocidades, presiones y códigos de gas presentes.
11. Ningún modelo fue confrontado con un balance hidráulico cerrado.
12. M5 cubre cinco curvas.
13. No se predicen otras variables de fondo.
14. No hay un detector de anomalías.

Cada una acota la frase que sí puede decirse: en estas curvas, y solo en ellas, el error y las irregularidades son los de las tablas anteriores.

## 14. Conclusiones

1. En las curvas externas de `2.14-A`, M4 tiene el menor MAE por curva: 1,044 psi y 0,754 psi. El alcance es este experimento. La limitación es que el menor error no es un mecanismo.
2. La media de M4 menos M2 queda bajo cero al remuestrear las curvas y al retirar cada grupo de hoja y velocidad. El alcance es la incertidumbre de estas curvas. La limitación es el tamaño, la dependencia y la selección previa de hiperparámetros. El valor p ajustado a posteriori no confirma la misma frase.
3. M2 reduce el MAE de M1 en 29 de 30 curvas de mapping y en 17 de 18 de surging. El alcance es la comparación con la recta. La limitación son las predicciones negativas y las subidas locales del agua.
4. M1 y M3 conservan la monotonía decreciente de las seis curvas de agua. M2 y M4 no. El alcance es la forma punto a punto de esas seis curvas. La limitación es que respetar la forma no implica el menor error, ni al revés.
5. M3 no muestra una ventaja estable frente a M1: el intervalo de la media pareada incluye el cero. Además extrapola la presión dentro de la condición en 18 curvas de mapping y en las 18 de surging.
6. M5 se calculó sin usar el agua de prueba y solo admite cinco curvas completas, con 2,078 psi. El concepto de una referencia de agua sigue siendo distinto del desempeño de esta fórmula.
7. La regla de superioridad de 2.13 no se cumple. El sesgo cambia de signo y la repetición sin la velocidad de diseño no es evaluable sin cambiar el dominio. No hay un ganador único.
8. El material actual no basta para un modelo híbrido de monitoreo sin sensores de fondo ni para un detector de anomalías. Hace falta otra bomba o datos de campo, más variables de operación y una restricción física que pueda comprobarse fuera del ajuste.

## 15. Recomendaciones futuras

Conviene conservar, para la comparación siguiente, a M1 como piso, a M2 como referencia no lineal escrita de antemano y a M4 como referencia de precisión de este experimento. M5 puede rehacerse cuando cada curva de gas tenga su agua en el entrenamiento y el caudal de líquido quede dentro de esa agua en más de una presión.

Un modelo híbrido, si se autoriza en otra actividad, podría restar una corrección a una curva de referencia, o imponer que el agua predicha no suba con el caudal, o estudiar la degradación relativa. Nada de eso está demostrado aquí. Una monotonía universal sobre el flujo con gas no se impone: en estos archivos el agua baja con el caudal, y el gas no autoriza la misma frase en todo régimen.

Para acercarse a un monitoreo sin sensores de fondo harían falta, como mediciones distintas de las de este cierre, corriente, potencia, frecuencia, presión en cabeza, temperatura, caudal de producción y una definición validada de la variable de fondo que se quiera estimar. Este conjunto no las trae como objetivos.

Tampoco conviene abrir otra familia de modelos sobre las mismas curvas externas. Esas curvas ya se usaron para comparar.

## 16. Referencias

Las fichas que la actividad 2.13 marcó como leídas solo en el resumen se citan con ese alcance. No se añaden trabajos no usados.

Breiman, L. (2001). Random forests. *Machine Learning*, 45, 5–32. https://doi.org/10.1023/A:1010933404324

Cawley, G. C. y Talbot, N. L. C. (2010). On over-fitting in model selection and subsequent selection bias in performance evaluation. *Journal of Machine Learning Research*, 11, 2079–2107. http://jmlr.org/papers/v11/cawley10a.html. En la actividad 2.13 se leyó el resumen.

Hoerl, A. E. y Kennard, R. W. (1970). Ridge regression: biased estimation for nonorthogonal problems. *Technometrics*, 12(1), 55–67. https://doi.org/10.1080/00401706.1970.10488634

Varma, S. y Simon, R. (2006). Bias in error estimation when using cross-validation for model selection. *BMC Bioinformatics*, 7, 91. https://doi.org/10.1186/1471-2105-7-91. En la actividad 2.13 se leyó el resumen.

Zhu, J. y Zhang, H.-Q. (2018). A review of experiments and modeling of gas-liquid flow in electrical submersible pumps. *Energies*, 11(1), 180. https://doi.org/10.3390/en11010180. Se usó el hecho de que la forma normalizada publicada requiere la densidad de la mezcla. Esa densidad no está en estos archivos. M5 no lleva ese nombre.

Zhu, J., Zhang, J., Cao, G., Zhao, Q., Peng, J., Zhu, H. y Zhang, H.-Q. (2019). Modeling flow pattern transitions in electrical submersible pump under gassy flow conditions. *Journal of Petroleum Science and Engineering*, 180, 471–484. https://doi.org/10.1016/j.petrol.2019.05.059

Zhu, J. (2019). *Data for: Modeling Flow Pattern Transitions in Electrical Submersible Pump under Gassy Flow Conditions*. Mendeley Data, versión 1. https://doi.org/10.17632/fk2b4r69bs.1. Licencia CC BY 4.0. Serie sin isopropanol.

## 17. Anexo de reproducibilidad

| Archivo | SHA-256 |
|---|---|
| `data/raw/mapping.xlsx` | `3b933ca84911484f5d912a44b025f5589abaf5ebc2b0426bf80c083869762bda` |
| `data/raw/surging.xlsx` | `acdcc6c5fc3d8969280c8712c45657fbb863f163a60829584fece5abf75f28cd` |
| `data/processed/mapping_long.csv` | `ff68e36703d3d3901b8bd964008c49b062afa9d89a817b9d66e7849f9b400648` |
| `data/processed/surging_long.csv` | `f58e8e2cac74acdf2081479ec8769422f39c4e4665f5b3ff472df4a70b15bd96` |

El código de los estimadores está en `src/esp_datascience/`. La fase E, en `fase_e.py`, solo clasifica papeles a partir del MAE ya calculado y rechaza comparar M5 con todas las curvas. No reentrena. Las pruebas viven en `tests/`. El cuaderno es `notebooks/04_entrenamiento_evaluacion_modelos.ipynb`. Los intervalos están en `docs/derivados/intervalos_bootstrap_fase_d.csv`.

La semilla es 214. El entorno de la fase D, y el de esta síntesis, fue el `.venv` del laboratorio: Python 3.14.8, NumPy 2.5.4, pandas 3.0.6, scikit-learn 1.9.1 y SciPy 1.18.1.
