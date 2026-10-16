# Estudio científico y selección de modelos candidatos

Actividad 2.13. Este documento elige una metodología y un conjunto de modelos para una comparación posterior. No entrena ningún modelo, no publica errores de predicción y no declara un modelo superior.

Las frases se marcan así:

- **Publicado:** está en un texto citado y se resume sin copiar sus tablas.
- **Comprobado aquí:** sale de los Excel, de los CSV de la actividad 2.12 o de los conteos de las actividades 2.10 y 2.12.
- **Hipótesis:** se formula para ser contrastada en la actividad 2.14.
- **Decisión:** es una elección metodológica de este laboratorio.

## 1. Resumen

El problema es predecir el incremento de presión de la etapa 3 de una ESP TE-2700 cuando circulan agua y aire, en la serie sin isopropanol. La magnitud de trabajo es `dp2_3_psi`. Mapping y surging no describen el mismo experimento: el primero fija un caudal de gas adimensional y varía el líquido; el segundo fija una fracción del caudal de mejor eficiencia y registra la fracción de gas de admisión. Por eso no comparten un solo modelo.

Se revisaron familias estadísticas, de curvas de bomba, mecanicistas, de aprendizaje automático y híbridas. Con 30 curvas de mapping y 18 de surging, y sin la geometría de la etapa en los Excel, el conjunto que pasa a la actividad 2.14 es corto: regresión lineal, polinomio con penalización de cresta, un modelo lineal separado por la condición de gas, el cociente entre la presión bifásica y la curva de agua de la misma hoja y velocidad, y un bosque aleatorio. El modelo mecanicista de Zhu et al. (2019), el híbrido física–aprendizaje automático, las redes informadas por ecuaciones y la simulación numérica quedan pospuestos. No hay un ganador.

## 2. Introducción

Una bomba electrosumergible eleva el fluido desde el pozo. Si el líquido entra con gas, el aumento de presión de la bomba disminuye y la operación puede volverse inestable (Zhu et al., 2019). Ese artículo no ajusta una curva completa de presión. Construye un modelo mecanicista de las fronteras entre cuatro patrones de flujo dentro de la bomba en rotación: burbuja dispersa, burbuja, intermitente y segregado. Las fronteras se comparan con los quiebres leídos en curvas de surging y de mapping.

Los Excel de este laboratorio son el conjunto de Mendeley Data asociado a ese artículo, serie «zero IPA», DOI 10.17632/fk2b4r69bs.1. La actividad 2.11 fijó el diccionario. La actividad 2.12 dejó dos tablas largas. La matriz escrita entonces nombraba seis modelos y no los ajustaba. Esta actividad cierra la selección. El ajuste, si se autoriza, es la actividad 2.14.

## 3. Planteamiento del problema

### Contexto

La bomba de los ensayos es una TE-2700, serie 538, de 14 etapas (Zhu, 2017, sección 2.1.2). La primera toma de presión diferencial útil para la etapa publicada está en el difusor de la etapa 2, de modo que los resultados que el artículo y la tesis comentan corresponden a la etapa 3. El instrumento citado para la diferencia de presión es el Rosemount 3051S (Zhu, 2017).

Los ensayos de este conjunto usan dos protocolos, descritos en Zhu et al. (2019), sección 3, y en la tesis, sección 2.3:

- **Surging.** El caudal de líquido queda fijo en una fracción del punto de mejor eficiencia y el caudal de gas aumenta desde cero.
- **Mapping.** El caudal de gas queda fijo, como Qgd, y el caudal de líquido disminuye desde el caudal abierto.

Gamboa y Prado (2011a, 2011b), citados por Zhu et al. (2019), asocian los puntos de quiebre de esas curvas H–Q con cambios de patrón de flujo. Esa asociación es literatura. Este laboratorio todavía no ha localizado esos quiebres en sus tablas.

### Problema

No existe, en este laboratorio, una relación cuantitativa verificada entre las condiciones de operación y el incremento de presión de la etapa 3. Esta actividad fija el orden en que se ajustarán las formas candidatas y la regla para compararlas sin partir una curva entre entrenamiento y prueba. El ajuste mismo no se hace aquí.

### Pregunta científica

¿Qué familia de modelos puede representar el incremento de presión de la etapa 3, en cada protocolo por separado, con un error que se estime al dejar fuera curvas completas y sin contradecir el sentido físico ya publicado de la degradación por gas?

La pregunta no se responde en esta actividad. Se deja planteada para la 2.14.

### Hipótesis de trabajo

1. Dentro de una velocidad y una presión de separador fijas, el incremento de la etapa 3 disminuye cuando aumenta el gas de admisión, y la pendiente puede cambiar al cruzar una frontera de régimen. Es la lectura de Zhu et al. (2019) y de Gamboa (2008), no un cálculo de estos CSV.
2. La superficie de mapping no es la de surging. Un modelo único para las dos tablas confundiría un gas fijo con un líquido fijo.
3. Una referencia lineal, ajustada por curvas completas, es el piso contra el cual hay que mostrar que un modelo más flexible aporta algo. Si no lo aporta, la flexibilidad no se justifica.

## 4. Objetivos e hipótesis

### Objetivo general

Elegir, sin entrenar, los modelos que la actividad 2.14 deberá implementar y la regla común con la que se decidirá si uno es más adecuado que otro.

### Objetivos específicos

- Separar lo que los artículos demuestran de lo que estos archivos permiten calcular.
- Fijar la variable objetivo y las entradas de cada protocolo.
- Clasificar cada familia como seleccionada, condicional, pospuesta o descartada en esta etapa.
- Escribir la validación por curvas completas, las métricas y la regla de desempate.
- Dejar explícitas las condiciones que el modelo híbrido todavía no cumple.

La hipótesis de trabajo está en la sección 3. No es un resultado.

## 5. Antecedentes y marco teórico

### Lo que el artículo de 2019 modela

Zhu et al. (2019) parten del balance de cantidad de movimiento a lo largo de una línea de corriente en la bomba en rotación. El texto lo relaciona con la deducción de Sachdeva y de Sun, citados ahí como 1998 y 2003. A partir de ese balance formulan las fronteras entre los cuatro patrones. La comparación con los ensayos usa los quiebres de las curvas, no un ajuste estadístico del incremento de presión punto a punto. El artículo concluye que el mapa calculado acompaña las fronteras leídas en sus ensayos y en los de Gamboa (2008), a 1800 y 3500 rpm y a 50, 100 y 150 psig, y muestra además una comparación a 2400 rpm con datos de Gamboa.

Esa capacidad no se transfiere sola a estos CSV. El mapa necesita cierres de tamaño de burbuja, esfuerzos de corte y geometría que el artículo desarrolla y que las columnas de los Excel no traen. **Decisión:** el modelo mecanicista de 2019 es la referencia física de patrón de flujo. No es, todavía, un predictor del número `dp2_3_psi`.

### Degradación y curvas de agua

Lea y Bearden (1982) y Zhou y Sachdeva (2010) aparecen en Zhu et al. (2019) como antecedentes de la pérdida de cabeza y de la vida corta de la bomba con gas. No se reproduce aquí ninguna correlación numérica de esos trabajos: no se releyeron sus ecuaciones para esta actividad.

Zhu et al. (2018), el artículo de surfactante, definen un incremento de presión normalizado que multiplica el cociente de presiones bifásica y de agua por el cociente de densidades del agua y de la mezcla. Los Excel no tienen la densidad de la mezcla. **Decisión:** se puede estudiar después el cociente de presiones respecto de la curva de agua de la misma hoja y la misma velocidad. No se lo llamará con el símbolo normalizado de ese artículo, porque faltaría la densidad.

### Leyes de afinidad

Zhu (2017) atribuye a Stepanoff (1957) las relaciones de semejanza de una bomba centrífuga, escritas como ecuaciones (2.1) a (2.3) de la tesis: el caudal escala con la velocidad de rotación, la altura hidráulica con el cuadrado de esa velocidad y la potencia al freno con el cubo. Son relaciones de semejanza para la misma máquina en líquido, no una teoría del flujo con gas. **Decisión:** servirán, si la actividad 2.14 lo ejecuta, como comprobación de coherencia de las curvas de agua entre 1800 y 3500 rpm. No se usarán para fabricar un Qmax a 1800 rpm y luego un caudal de gas.

### Patrones y protocolos

El reconocimiento de patrones por la curva de desempeño es el procedimiento de Gamboa y Prado (2011a, 2011b), adoptado por Zhu et al. (2019). Surging recorre el gas a líquido fijo. Mapping recorre el líquido a gas fijo. Las figuras 1(a) y 1(b) de Zhu et al. (2019) los dibujan como ensayos distintos. **Decisión:** cada protocolo tiene su propia regresión.

### Lo que este laboratorio ya fijó

El diccionario (`docs/diccionario_variables.md`) y la normalización (`docs/normalizacion_datos.md`) quedan como están. Esta sección no los reemplaza.

## 6. Caracterización de los datos experimentales

**Comprobado aquí**, actividad 2.12:

| Tabla | Filas | Curvas | Qué es una curva |
|---|---:|---:|---|
| `mapping_long.csv` | 570 | 30 | hoja, velocidad y condición |
| `surging_long.csv` | 387 | 18 | hoja, velocidad y fracción de QBEP |

Una curva de mapping reúne entre 9 y 30 pares. Una de surging, entre 8 y 42. Esos puntos no son ensayos independientes: son lecturas de la misma curva H–Q.

Mapping, por velocidad: 62 y 124 pares en `50psig` con la velocidad escrita en la celda; 55 y 137 en `100psig`; 70 y 122 en `150psig`. En estas dos últimas hojas la velocidad es asignación del diseño experimental, 384 filas de las 570. Surging trae 1800 y 3500 rpm escritos en la celda en las tres presiones: 38 y 81, 36 y 93, 49 y 90 pares.

Rangos, sin convertir unidades: caudal de mapping de 1,35 bpd a 4702 bpd; `dp2_3_psi` de mapping de 0,08 psi a 31,2 psi; el de surging de 0,38 psi a 28,0 psi; `gvf0_porcentaje` de 0,0006 a 19,1.

No hubo pares con una sola celda numérica. Los huecos doblemente vacíos no son filas. `Single Phase` deja `qgd` vacío. No se escribió un cero.

### Variables

| Papel | Mapping | Surging | Unidad de trabajo | Certeza |
|---|---|---|---|---|
| Objetivo | `dp2_3_psi` | `dp2_3_psi` | psi | Media |
| Líquido | `ql_bpd` | no está; hay `fraccion_qbep` | bpd; fracción de QBEP | Alta como interpretación del caudal; alta para los rótulos 0,75, 1 y 1,25 |
| Gas | `qgd`, vacío en agua | `gvf0_porcentaje` | adimensional; porcentaje | Alta para Qgd; media para la columna GVF0 |
| Velocidad | `velocidad_rpm` y `origen_velocidad` | `velocidad_rpm` leída de la celda | rpm | Alta, con el origen declarado |
| Presión de admisión | `psep_psig` | `psep_psig` | psig | Alta por el nombre de la hoja |

QBEP a 3500 rpm es 2700 bpd en la tesis y 0,005 m³/s en Zhu et al. (2018). Qmax a 3500 rpm es 4900 bpd (Zhu, 2017, sección 2.1.2). No se multiplica la fracción de QBEP por 2700 bpd a 1800 rpm, ni se calcula QG con el Qmax de 3500 rpm a la otra velocidad.

### Limitaciones del conjunto

- Una sola bomba, agua y aire, serie sin surfactante, dos velocidades, tres presiones de separador.
- La geometría, la temperatura de cada fila, la densidad de la mezcla y el caudal de fuga no están en los Excel.
- La velocidad de dos hojas de mapping no es una medición de la celda.
- El rótulo `DP2-3` y el sufijo de `GVF0` no aparecen en la tesis.

## 7. Fundamentos de las familias de modelos

Ninguna familia se ajustó. Las ecuaciones de esta sección son la definición matemática de la familia o una relación ya escrita en la tesis. No son un ajuste a los CSV.

### Regresión lineal

El incremento de presión se escribe como una suma de las entradas, cada una con un coeficiente, más un resto. Los coeficientes salen de minimizar la suma de cuadrados. Hace falta que las entradas estén en una sola unidad dentro de cada protocolo. No representa un quiebre de régimen: Zhu et al. (2019) describen cambios de pendiente al pasar de un patrón a otro. Sirve como piso de comparación, porque cualquier modelo más flexible tiene que mejorar este error sin usar los mismos puntos de la curva.

### Polinomio y regresión de cresta

Un polinomio agrega potencias y productos de las entradas. El número de términos crece antes de ver el error de prueba, así que el grado tiene que quedar fijado fuera de las curvas de prueba. Hoerl y Kennard (1970) suman una constante positiva a la diagonal de la matriz de productos de las entradas para encoger los coeficientes cuando esas entradas están correlacionadas. El caudal, la velocidad y la presión del separador lo están, porque el diseño no las cruza de forma completa. La cresta no distingue una ley de bomba. Reduce la varianza del polinomio si la constante de penalización no se elige con las curvas que luego se reportan.

### Modelos aditivos generalizados

Hastie y Tibshirani (1986) sustituyen la suma de coeficientes por una suma de funciones suaves, una por entrada. La forma de cada función se estima. Permiten ver si el caudal o el gas entran de manera curva sin imponer un grado. No incluyen, por sí mismos, el producto entre gas y caudal, que es una interacción plausible entre Qgd y QL. El entorno actual no tiene una biblioteca de estos modelos. Construirlos con bases de la biblioteca científica ya instalada es una implementación, y queda fuera de esta actividad.

### Modelos por tramos y superficies de respuesta

Un modelo por tramos usa una relación distinta a cada lado de un corte. En estos ensayos el corte candidato no se inventa: es la condición ya escrita en el archivo, Qgd o la fracción de QBEP. Buscar el corte en el error de las mismas curvas sería usar la prueba para definir el modelo. Las superficies de respuesta polinómicas, en la línea de los diseños de Box y Wilson (1951), describen una superficie suave sobre factores controlados. El diseño de Zhu no es un factorial completo de caudal, gas, velocidad y presión. La superficie global se pospone. El modelo separado por la condición que el archivo ya trae sí entra en la lista experimental.

### Curva característica y leyes de afinidad

La curva de agua es la referencia monofásica de la misma bomba. En mapping está en el bloque `Single Phase`. Las leyes de afinidad de la tesis escalan caudal y altura entre dos velocidades. Aplicadas al gas, dirían más de lo que Stepanoff, según la tesis, escribió para la máquina en líquido. **Decisión:** la afinidad se reserva para preguntar si las dos curvas de agua, a 1800 y 3500 rpm, guardan esa proporción. No es el modelo del incremento con gas.

### Modelo mecanicista bifásico

Es el de Zhu et al. (2019), secciones 5 y 7: balance de cantidad de movimiento en la bomba en rotación y criterios de paso entre burbuja dispersa, burbuja, intermitente y flujo segregado. Predice fronteras, no la columna `dp2_3_psi`. Reconstruirlo exige geometría y cierres que no están en los CSV. Queda como antecedente y como condición previa del modelo híbrido, no como ajuste de esta etapa.

### Correlaciones de degradación

La forma utilizable con estos archivos es el cociente entre `dp2_3_psi` de una condición con gas y `dp2_3_psi` de la curva de agua a la misma velocidad, la misma hoja y un caudal de líquido comparable. Eso no añade parámetros de geometría. Tampoco es la presión normalizada de Zhu et al. (2018), porque falta la densidad. En surging no hay una columna de caudal de líquido, así que el emparejamiento con una curva de agua de mapping no está justificado. El cociente queda limitado a mapping.

### Árboles y ensambles

Un árbol parte el espacio de las entradas en regiones y asigna un valor a cada región. Puede situar un cambio abrupto cerca de un umbral de gas. También puede memorizar una curva si las hojas del árbol coinciden con los puntos de entrenamiento. Breiman (2001) define el bosque aleatorio como un conjunto de árboles, cada uno dependiente de un vector aleatorio, y muestra que la idea vale también para regresión. El error depende de la fuerza de cada árbol y de la correlación entre árboles. Con 30 o 18 curvas, un bosque profundo tiene pocos bloques independientes. La profundidad y el número de árboles se eligen fuera de las curvas de prueba.

Geurts, Ernst y Wehenkel (2006) aleatorizan también el corte dentro del árbol. Es la misma familia. No aporta, en esta primera ronda, una pregunta distinta de la del bosque. Friedman (2001) construye el boosting como una suma de árboles ajustados al resto del paso anterior. Es más sensible al número de iteraciones. Entra solo si el bosque, ya comparado con la referencia lineal, muestra un sesgo que esa suma pudiera reducir. Esa condición se mira en la actividad 2.14, no ahora.

### Regresión de vectores de soporte

Smola y Schölkopf (2004) revisan la regresión que penaliza los errores dentro de un margen y usa un núcleo para curvar la relación. Exige una escala común de las entradas. Con pocas curvas, el núcleo y el margen se pueden ajustar al ruido de una sola velocidad. No se descarta por ser poco popular: se deja condicional, detrás del polinomio, porque el polinomio ya ofrece una curvatura con menos decisiones ocultas.

### Procesos gaussianos

Rasmussen y Williams (2006) describen una función desconocida mediante un proceso gaussiano. La predicción trae una media y una varianza. Esa varianza sería útil para decir dónde el modelo no debe extrapolar. El núcleo tiene sus propios parámetros y, con 30 curvas, puede absorber la curva en vez de la tendencia. Se pospone hasta que exista una referencia lineal y una física simple contra las cuales comparar esa banda de incertidumbre.

### Redes neuronales

Una red de capas densas compone funciones simples y puede aproximar una superficie continua. Hornik, Stinchcombe y White (1989) dan una condición de aproximación universal para redes de una capa oculta. La existencia de esa capacidad no dice que 570 o 387 filas, agrupadas en pocas curvas, alcancen para estimarla. La escala de las entradas tendría que ser explícita. La red no conoce el quiebre de régimen ni la curva de agua. Queda pospuesta.

### Híbrido física–aprendizaje automático

La parte física calcularía una frontera o una presión de referencia. La parte estadística ajustaría solo el resto, en psi. Zhu et al. (2019) calculan fronteras, no la curva completa de presión. Mientras esa frontera no se reproduzca con datos que los Excel sí tienen, el resto mezclaría error de modelo, error de unidades y ausencia de geometría. **Decisión:** no entra en la 2.14 inicial.

### Redes informadas por la física

Raissi, Perdikaris y Karniadakis (2019) entrenan una red para que la solución cumpla una ecuación en derivadas parciales además de los datos. Hace falta escribir esa ecuación, sus condiciones de borde y la geometría. No están en los CSV. El método no se descarta como idea. Se descarta como próximo experimento de este laboratorio.

### Simulación numérica del flujo

Zhu, Zhu, Zhang y Zhang (2019), en el Journal of Petroleum Science and Engineering, volumen 173, comparan patrones calculados con experimentos de visualización. Es una vía de mecánica de fluidos computacional, no una regresión de estas tablas. Pediría malla, fluido y geometría que este repositorio no guarda. Queda como alternativa metodológica externa, no como modelo de la actividad 2.14.

## 8. Metodología de evaluación y selección

Esta sección obliga a la actividad 2.14. No se ejecuta aquí.

### Entradas y objetivo

El objetivo es siempre `dp2_3_psi`.

En mapping, las entradas son `ql_bpd`, la condición (`Single Phase` o el valor de `qgd`), `velocidad_rpm`, `psep_psig` y `origen_velocidad`. La última es una etiqueta de procedencia. No se rellena la celda vacía del Excel. Un ajuste puede repetirse sin las 384 filas de origen `diseño_experimental`, para ver si la conclusión depende de esa asignación.

En surging, las entradas son `fraccion_qbep`, `gvf0_porcentaje`, `velocidad_rpm` y `psep_psig`. No se importa `ql_bpd` desde mapping.

El agua de mapping conserva `qgd` vacío. El modelo debe recibir un indicador de fase, no un cero imputado.

### Separación

No se apilan las tablas. No se reparte una curva entre entrenamiento y prueba. La unidad de bloqueo es la curva: hoja, velocidad y condición. Con 30 y 18 curvas, la validación cruzada deja fuera, cada vez, curvas completas. Si una partición se queda sin una de las dos velocidades o sin una de las tres presiones, no se usa para declarar superioridad: solo para describir ese hueco.

La validación anidada, con la elección de grado, penalización o profundidad en un anillo interior, es viable si el anillo exterior conserva curvas de las dos velocidades. Si el número de curvas no alcanza para los dos anillos, se fija de antemano un conjunto pequeño de complejidades y se informa que la elección no fue anidada. No se elige la complejidad con el error que luego se publica.

### Métricas

Sobre las curvas dejadas fuera se calculan el error absoluto medio, la raíz del error cuadrático medio, el sesgo medio (predicción menos medición) y el coeficiente de determinación. Se tabulan además por velocidad, por presión de separador y por condición de gas. Un promedio global que esconde un fallo a 1800 rpm no declara superioridad.

Los residuos se grafican contra el caudal o contra `GVF0`, según el protocolo, y contra la predicción. No se imputan residuos.

### Coherencia, complejidad y desempate

Entre dos modelos cuyo error absoluto medio difiera en menos de lo que esa misma validación muestra como variación entre repeticiones de curvas parecidas, se prefiere el de menos parámetros libres y el que admite una lectura física. Un modelo flexible que gane solo al partir las curvas de entrenamiento queda descartado en esa prueba.

La coherencia física que se exigirá, como hipótesis y no como resultado, es que a velocidad y presión fijas el incremento predicho no crezca de forma sistemática al aumentar el gas dentro del rango ensayado. Una violación local puede ser un cambio de régimen. Tiene que quedar escrita, no absorbida por el error global.

### Extrapolación

Ningún modelo de la 2.14 podrá presentarse como válido fuera de la TE-2700, del agua con aire, de la serie sin isopropanol, de 1800 y 3500 rpm, de 50, 100 y 150 psig, ni fuera de los Qgd y de los porcentajes de `GVF0` realmente presentes en la curva de prueba. La afinidad no alarga ese dominio hacia otro fluido.

### Cuándo un modelo es superior

Solo en la actividad 2.14, y solo si se cumplen a la vez estas condiciones:

- El error absoluto medio y la raíz del error cuadrático medio, en la validación por curvas, son menores que los de la regresión lineal del mismo protocolo.
- El sesgo no cambia de signo de manera sistemática entre 1800 y 3500 rpm ni entre las tres presiones.
- El resultado se mantiene al repetir el ajuste de mapping sin las filas cuya velocidad viene del diseño.
- La complejidad adicional está declarada antes de ver el error de las curvas de prueba.
- Si la diferencia de error es pequeña, gana el modelo más legible.

Si nadie cumple la primera condición, la regresión lineal sigue siendo la referencia y no se anuncia un modelo avanzado.

## 9. Matriz comparativa

| Familia | Qué calcularía | Datos que faltan | Clase en esta etapa |
|---|---|---|---|
| Lineal múltiple | `dp2_3_psi` en cada protocolo | Ninguno de los que la tabla ya trae | Seleccionada |
| Polinomio con cresta | La misma presión, con curvatura | El grado y la penalización, que se elegirán fuera de la prueba | Seleccionada |
| Lineal por condición de gas | Una recta por Qgd o por fracción de QBEP | Ninguno; la condición ya está escrita | Seleccionada |
| Cociente respecto de la curva de agua | Degradación en mapping | Densidad, si se quisiera la forma normalizada publicada | Seleccionada, solo mapping, sin la densidad |
| Bosque aleatorio | La misma presión, con cortes | Profundidad y número de árboles, fuera de la prueba | Seleccionada |
| Boosting de árboles | La misma presión | Una razón, todavía no observada, para preferirlo al bosque | Condicional |
| Vectores de soporte | Una superficie con margen | Escala y núcleo, y curvas suficientes | Condicional |
| Leyes de afinidad | Coherencia de las curvas de agua | No describen el gas | Condicional, como diagnóstico |
| Modelo aditivo | Funciones suaves por entrada | Implementación no iniciada | Pospuesto |
| Proceso gaussiano | Media y banda de incertidumbre | Curvas suficientes para el núcleo | Pospuesto |
| Red densa | Superficie flexible | Repetición de condiciones | Pospuesto |
| Árboles extremadamente aleatorizados | Otra variante del bosque | Una pregunta distinta de la del bosque | Pospuesto |
| Mecanicista de 2019 | Fronteras de patrón | Geometría y cierres | Pospuesto |
| Híbrido física–estadística | Resto en psi | Una base física reproducible con estos archivos | Pospuesto |
| Red informada por ecuaciones | Solución de una ecuación | La ecuación y la geometría en los datos | Pospuesto |
| Simulación de fluidos | Campo de flujo | Malla y geometría | Pospuesto |
| Un solo ajuste de las dos tablas | Una superficie común | Los protocolos no son la misma superficie | Descartada |
| Reparto aleatorio de filas | Una métrica | Parte cada curva | Descartada |
| QG a 1800 rpm con el Qmax de 3500 rpm | Una entrada de gas | El Qmax a 1800 rpm no está publicado en la tesis | Descartada |

## 10. Resultados de la selección metodológica

No hay resultados de predicción. El resultado de esta actividad es la lista y el orden.

Orden propuesto para la actividad 2.14, en cada protocolo por separado:

1. Regresión lineal múltiple. Es el piso.
2. Polinomio con cresta. Pregunta si la curvatura, sin un quiebre explícito, basta.
3. Regresión lineal separada por la condición de gas ya escrita. Pregunta si el quiebre que la literatura asocia al régimen aparece como un cambio de recta entre condiciones.
4. En mapping, el cociente respecto de la curva de agua de la misma hoja y velocidad. Es la referencia semiempírica que estos archivos sí permiten. No usa la densidad.
5. Bosque aleatorio. Entra último para que su error se compare con los cuatro anteriores y no los reemplace de antemano.

Durante esas pruebas, un candidato se deja de lado si su error por curvas no mejora el de la regresión lineal, si el sesgo cambia de manera sistemática con la velocidad o la presión, o si la mejora desaparece al quitar las filas de velocidad asignada por el diseño. Esas reglas no se han aplicado: no hay ajustes.

El boosting queda detrás del bosque. La regresión con vectores de soporte queda detrás del polinomio. La afinidad queda como diagnóstico de las curvas de agua, no como quinto modelo del gas.

## 11. Discusión

La literatura consultada separa dos tareas. Una es saber en qué patrón está la bomba. Otra es saber cuántos psi aumenta la etapa. Zhu et al. (2019) trabajan la primera y leen la segunda solo para marcar quiebres. Este laboratorio tiene la segunda como columna y no tiene, en los CSV, los ingredientes de la primera. Elegir un bosque o una red porque aproximan superficies ignoraría esa diferencia. Elegir solo el modelo mecanicista ignoraría que no produce, por sí mismo, `dp2_3_psi` con las columnas disponibles.

Mapping y surging merecen modelos distintos porque el gas y el líquido no juegan el mismo papel. En uno, Qgd es la etiqueta del bloque y el líquido varía. En el otro, la fracción de QBEP es la etiqueta y `GVF0` varía. Unirlos exigiría inventar la entrada que el otro protocolo no midió.

Treinta curvas y dieciocho curvas son pocas para una validación anidada holgada. Por eso la lista experimental tiene cinco pasos y no quince. La escasez no elimina el bosque: lo pone al final y le impone la misma partición que a la recta. Si el bosque no gana con esa regla, no se pasa a una red.

La velocidad asignada por el diseño es la decisión más frágil de mapping. El modelo puede usarla, siempre que el informe de la 2.14 repita el cálculo sin esas filas. Si las dos cuentas discrepan, no hay una conclusión única sobre el efecto de la velocidad.

## 12. Limitaciones

- No se entrenó ningún modelo. Las métricas de la sección 8 están definidas y no calculadas.
- No se revisó de forma sistemática la literatura posterior a 2019. Las familias generales se apoyan en sus artículos fundacionales, no en un censo de aplicaciones a ESP.
- No se releyeron las correlaciones numéricas de Lea y Bearden (1982) ni de Zhou y Sachdeva (2010). Solo se usó el lugar que Zhu et al. (2019) les da como antecedentes.
- La certeza media de `dp2_3_psi` y de `gvf0_porcentaje` limita cualquier modelo que se ajuste después. Un error pequeño no convierte el rótulo en una cita de la tesis.
- El cociente respecto de la curva de agua requiere emparejar caudales. Cómo se interpola esa curva es una decisión de la 2.14, no un resultado de esta.
- Los ganchos que impiden una coautoría ajena en los commits están en este computador. No forman parte del estudio científico.

## 13. Conclusiones

El objeto de predicción es el incremento de presión de la etapa 3, en psi, con la certeza media ya declarada. Mapping y surging se modelan por separado. La actividad 2.14, si se autoriza, debe empezar por la regresión lineal, seguir con el polinomio penalizado y con la recta por condición de gas, añadir en mapping el cociente respecto de la curva de agua y solo después probar un bosque aleatorio. El modelo mecanicista, el híbrido, la red informada por ecuaciones y la simulación de fluidos no forman parte de esa primera comparación. No hay modelo ganador.

## 14. Recomendaciones para la fase experimental

La actividad 2.14 no está autorizada por este documento. Cuando lo esté, conviene este orden y estas condiciones:

- Implementar solo la lista de la sección 10.
- Mantener los CSV y los Excel como están.
- No calcular QG ni el caudal de surging en bpd.
- No llamar al cociente de presiones con el nombre normalizado del artículo de 2018.
- Elegir grado, penalización y profundidad sin las curvas de prueba.
- Publicar el error por velocidad, presión y condición de gas, además del error global.
- Repetir mapping sin la velocidad de origen `diseño_experimental`.
- No abrir el híbrido hasta que una base física, calculable con estos archivos o con magnitudes que la tesis escriba de forma explícita, reproduzca una frontera ya publicada en curvas que no se usen para ajustar el resto.
- No abrir una red densa ni una red informada por ecuaciones en esa misma fase.

## 15. Referencias bibliográficas

Las referencias de ESP que no se releyeron por completo se incluyen solo cuando Zhu et al. (2019) o la tesis las usan del modo que aquí se dice. Las de métodos estadísticos se contrastaron con su publicación de origen.

Box, G. E. P. y Wilson, K. B. (1951). On the experimental attainment of optimum conditions. *Journal of the Royal Statistical Society: Series B*, 13(1), 1–45.

Breiman, L. (2001). Random forests. *Machine Learning*, 45, 5–32. https://doi.org/10.1023/A:1010933404324

Friedman, J. H. (2001). Greedy function approximation: a gradient boosting machine. *Annals of Statistics*, 29(5), 1189–1232.

Gamboa, J. (2008). *Prediction of the Transition in Two-phase Performance of an Electrical Submersible Pump*. Tesis doctoral, The University of Tulsa. Citado por Zhu et al. (2019) como origen de la lectura de quiebres de la curva.

Gamboa, J. y Prado, M. G. (2011a). Review on ESP surging correlations and models. SPE Production and Operations Symposium, Oklahoma City. Society of Petroleum Engineers.

Gamboa, J. y Prado, M. (2011b). Review of electrical-submersible-pump surging correlation and models. *SPE Production & Operations*, 26(4), 314–324.

Geurts, P., Ernst, D. y Wehenkel, L. (2006). Extremely randomized trees. *Machine Learning*, 63, 3–42.

Hastie, T. y Tibshirani, R. (1986). Generalized additive models. *Statistical Science*, 1(3), 297–310. https://doi.org/10.1214/ss/1177013604

Hoerl, A. E. y Kennard, R. W. (1970). Ridge regression: biased estimation for nonorthogonal problems. *Technometrics*, 12(1), 55–67. https://doi.org/10.1080/00401706.1970.10488634

Hornik, K., Stinchcombe, M. y White, H. (1989). Multilayer feedforward networks are universal approximators. *Neural Networks*, 2(5), 359–366.

Lea, J. F. y Bearden, J. L. (1982). Effect of gaseous fluids on submersible pump performance. *Journal of Petroleum Technology*, 34(12). La ficha bibliográfica de Zhu et al. (2019) lo lista así. No se releyó el artículo para esta actividad y no se copia aquí un intervalo de páginas dudoso en la extracción del PDF.

Raissi, M., Perdikaris, P. y Karniadakis, G. E. (2019). Physics-informed neural networks: a deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations. *Journal of Computational Physics*, 378, 686–707. https://doi.org/10.1016/j.jcp.2018.10.045

Rasmussen, C. E. y Williams, C. K. I. (2006). *Gaussian Processes for Machine Learning*. MIT Press.

Smola, A. J. y Schölkopf, B. (2004). A tutorial on support vector regression. *Statistics and Computing*, 14, 199–222.

Stepanoff, A. J. (1957). Leyes de afinidad, en la forma citada por Zhu (2017), ecuaciones (2.1) a (2.3). No se consultó el libro aparte de esa cita.

Zhou, D. y Sachdeva, R. (2010). Simple model of electric submersible pump in gassy well. *Journal of Petroleum Science and Engineering*, 70, 204–213. Antecedente citado por Zhu et al. (2019). No se releyó el artículo para esta actividad.

Zhu, J. (2017). *Experiments, CFD Simulation and Modeling of ESP Performance under Gassy Conditions*. Tesis doctoral, The University of Tulsa. Archivo local: `ProjectESP/Papers/Thesis/Two-phase/Zhu 2017 (PhD thesis).pdf`.

Zhu, J. y Zhang, H.-Q. (2018). A review of experiments and modeling of gas-liquid flow in electrical submersible pumps. *Energies*, 11, 180.

Zhu, J., Zhu, H., Wang, Z., Zhang, J., Cuamatzi-Melendez, R., Martinez Farfan, J. A. y Zhang, H.-Q. (2018). Surfactant effect on air/water flow in a multistage electrical submersible pump (ESP). *Experimental Thermal and Fluid Science*, 98, 95–111. Archivo local: `ProjectESP/Papers/Zhu 2018b.pdf`.

Zhu, J., Zhu, H., Zhang, J. y Zhang, H.-Q. (2019). A numerical study on flow patterns inside an electrical submersible pump (ESP) and comparison with visualization experiments. *Journal of Petroleum Science and Engineering*, 173, 339–350.

Zhu, J., Zhang, J., Cao, G., Zhao, Q., Peng, J., Zhu, H. y Zhang, H.-Q. (2019). Modeling flow pattern transitions in electrical submersible pump under gassy flow conditions. *Journal of Petroleum Science and Engineering*, 180, 471–484. https://doi.org/10.1016/j.petrol.2019.05.059. Archivo local: `docs/esp_gassy_flow_paper.pdf`.

Zhu, J. (2019). Datos asociados. *Data for: Modeling Flow Pattern Transitions in Electrical Submersible Pump under Gassy Flow Conditions*. Mendeley Data, versión 1. https://doi.org/10.17632/fk2b4r69bs.1. Licencia CC BY 4.0.
