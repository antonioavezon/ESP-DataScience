# Matriz de modelos candidatos

Evaluación conceptual. No se entrenó ningún modelo. El objetivo de trabajo es la columna `DP2-3`, leída como incremento de presión de la etapa 3 en psi, según la tesis de Zhu (2017). El rótulo no está en la tesis; la certeza de ese enlace es media y está en el diccionario.

Entradas que el diseño experimental necesitaría, cuando estén definidas:

- Caudal de líquido, QL.
- Información de gas: Qgd, QG o GVF, sin mezclar definiciones distintas.
- Velocidad de rotación N.
- Presión del separador Psep.

Las entradas de trabajo son el caudal de líquido en bpd, una variable de gas (Qgd o `GVF0` en porcentaje, sin mezclarlas), N en rpm y Psep en psig. Véase `docs/diccionario_variables.md`.

## 1. Regresión lineal múltiple

| Campo | Contenido |
|---|---|
| Tipo | Modelo lineal en las entradas |
| Entradas | QL, una variable de gas, N y Psep, en unidades compatibles |
| Objetivo | `DP2-3`, incremento de la etapa 3 en psi |
| Ventaja | Coeficientes legibles y poca complejidad |
| Limitación | El artículo muestra quiebres de la curva al cambiar el régimen. Una recta no representa esos quiebres |
| Datos | Exige pocas filas, y exige que las unidades sean las mismas en todas |
| Interpretabilidad física | Alta si los coeficientes conservan un sentido, baja si las variables siguen mezcladas |
| Sobreajuste | Bajo frente a los otros modelos de esta lista, si las entradas son pocas |
| Validación | Separar curvas completas. No repartir al azar los puntos de una misma curva |

## 2. Regresión polinómica con Ridge

| Campo | Contenido |
|---|---|
| Tipo | Polinomio de las entradas, con penalización Ridge sobre los coeficientes |
| Entradas | Las mismas, más los productos y las potencias que se decida incluir |
| Objetivo | El mismo incremento de presión |
| Ventaja | Puede curvar la relación caudal-presión dentro de un régimen |
| Limitación | Un polinomio global sigue sin conocer la frontera entre regímenes que el artículo mapea |
| Datos | Los términos del polinomio crecen rápido. Hace falta acordar el grado antes de mirar el error de prueba |
| Interpretabilidad física | Media. Ridge encoge coeficientes y no distingue una ley de bomba |
| Sobreajuste | Sube con el grado. Ridge lo contiene solo si la penalización se elige fuera de las filas de prueba |
| Validación | La penalización y el grado se eligen en un conjunto distinto del de prueba, y por curvas completas |

## 3. Random Forest Regressor

| Campo | Contenido |
|---|---|
| Tipo | Conjunto de árboles de regresión |
| Entradas | Las mismas. Tolera relaciones no lineales y umbrales |
| Objetivo | El mismo incremento de presión |
| Ventaja | Puede partir el espacio cerca de cambios abruptos de desempeño |
| Limitación | No impone la curva de bomba ni la conservación de masa. Interpola mal fuera de las condiciones ensayadas |
| Datos | Con unos cientos de pares por archivo, un bosque grande memoriza curvas. La cantidad actual no justifica un bosque profundo |
| Interpretabilidad física | Baja. La importancia de una variable no es una definición de Qgd ni de ΔP |
| Sobreajuste | Alto si los árboles crecen sin límite y si la validación parte una misma curva |
| Validación | Profundidad y número de árboles fijados fuera de la prueba. Bloques por velocidad, Psep y protocolo |

## 4. HistGradientBoostingRegressor

| Campo | Contenido |
|---|---|
| Tipo | Boosting de árboles por histograma, disponible en scikit-learn, sin entrenarlo aquí |
| Entradas | Las mismas |
| Objetivo | El mismo incremento de presión |
| Ventaja | Ajusta interacciones con menos árboles que un bosque grande y admite valores faltantes en algunas implementaciones |
| Limitación | Esa tolerancia a faltantes no autoriza a tratar la velocidad ausente de mapping como un dato medido |
| Datos | Sigue siendo un modelo flexible para el tamaño de estas hojas |
| Interpretabilidad física | Baja |
| Sobreajuste | Alto si el número de iteraciones se elige con el mismo conjunto que se quiere reportar |
| Validación | Iteraciones, profundidad y tasa de aprendizaje fuera de la prueba, por condiciones completas |

## 5. MLPRegressor

| Campo | Contenido |
|---|---|
| Tipo | Red neuronal de capas densas |
| Entradas | Las mismas, después de una escala común. Sin unidad común, la escala no tiene sentido físico |
| Objetivo | El mismo incremento de presión |
| Ventaja | Puede aproximar una superficie suave de caudal, gas, velocidad y presión |
| Limitación | Con las filas disponibles, la red no aporta una ley y es difícil de vincular con el modelo de burbuja del artículo |
| Datos | Es el modelo de esta lista que más exige repetición de condiciones y una partición honesta |
| Interpretabilidad física | Muy baja |
| Sobreajuste | Alto |
| Validación | Arquitectura y regularización fuera de la prueba. No se considera en la etapa siguiente |

## 6. Corrección residual Física–Machine Learning

| Campo | Contenido |
|---|---|
| Tipo | Un cálculo físico entrega una presión o una frontera de régimen, y un modelo estadístico aprende solo el residuo |
| Entradas | Las del cálculo físico más las que falten para el residuo. Hay que declarar qué parte es física y qué parte es estadística |
| Objetivo | El residuo del incremento de presión, no un sustituto opaco de la bomba |
| Ventaja | Conserva el contenido de régimen que el artículo ya formuló y deja al modelo estadístico la desviación que la física no captura |
| Limitación | El modelo de Zhu en este artículo predice fronteras de patrón de flujo, no una curva completa de ΔP. Usarlo como base del residuo exige escribir esa base con ecuaciones cerradas y datos de geometría que estos Excel no traen |
| Datos | El residuo tendría que estar en psi, la misma escala en la que se lee `DP2-3`. La geometría de la etapa no está en los Excel |
| Interpretabilidad física | Alta en la parte mecanicista, si las ecuaciones son las del artículo. Baja si el residuo absorbe un error de unidades |
| Sobreajuste | Puede ser menor que una red que prediga la presión desde cero, y sigue existiendo si el residuo se ajusta con los mismos puntos usados para dibujar la frontera |
| Validación | Primero comprobar que la parte física reproduce una frontera ya publicada. Después ajustar el residuo en otras curvas |

## Lectura de conjunto

La actividad 2.13 no ajustó esta lista. El estudio completo está en `docs/estudio_modelos_2_13.md`. Las tablas de la actividad 2.12 ya existen y siguen separadas.

Decisión metodológica, no un resultado de predicción:

- Pasan a la actividad 2.14, si se autoriza y en este orden: regresión lineal, polinomio con cresta, recta separada por la condición de gas, cociente respecto de la curva de agua solo en mapping, y bosque aleatorio.
- El boosting de árboles y la regresión de vectores de soporte quedan condicionales, detrás del bosque y del polinomio.
- El modelo híbrido, la red densa, el modelo mecanicista como predictor de `dp2_3_psi`, la red informada por ecuaciones y la simulación de fluidos quedan pospuestos.
- Sigue descartado unir mapping con surging y repartir al azar los puntos de una misma curva.

No hay modelo ganador. La actividad 2.14 no está iniciada.
