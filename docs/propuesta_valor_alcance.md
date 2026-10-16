# Propuesta de valor y alcance

## Qué investigó y validó Zhu y colaboradores

El artículo de 2019 formula un modelo mecanicista de las fronteras entre regímenes de flujo gas-líquido dentro de una ESP en rotación: burbuja dispersa, burbuja, intermitente y segregado. Compara esas fronteras con los quiebres de las curvas de desempeño medidas en ensayos de surging y de mapping, a Psep de 50, 100 y 150 psig y a velocidades de 1800 y 3500 rpm. El desempeño que comentan es el incremento de presión de la etapa 3.

Ese trabajo no entrena un modelo de Machine Learning. No publica tampoco, en este texto, el diccionario de columnas de los Excel de Mendeley Data.

## Qué podemos reproducir

Con los archivos locales se puede reconstruir la organización de los ensayos: hojas por presión, dos velocidades cuando el número está escrito, bloques de Qgd en mapping y bloques de caudal respecto de Qbep en surging. La actividad 2.10 ya dejó verificado el conteo de Mapping/`50psig`.

Las unidades de trabajo de estos Excel quedan leídas en la tesis: caudal en bpd, incremento de etapa en psi y GVF de admisión en porcentaje. Qmax a 3500 rpm es 4900 bpd. No se reproducen todavía las figuras de frontera de régimen: el artículo las obtiene interpretando quiebres de la curva, y esta actividad no localiza esos quiebres.

## Qué se pretende predecir

El objetivo de esta línea es el incremento de presión de la etapa 3, columna `DP2-3`, leída en psi según la tesis. La etiqueta `DP2-3` no está escrita en la tesis; el enlace tiene certeza media y queda declarado en el diccionario.

## Qué aportaría Machine Learning

Podría representar relaciones no lineales entre caudal, gas, velocidad y presión cuando esas variables estén en una tabla con unidades únicas. No sustituye la definición de régimen que el artículo construye con el tamaño de burbuja y el balance de cantidad de movimiento.

## Qué aportaría un modelo híbrido

Podría dejar al modelo mecanicista la frontera de régimen y a un modelo estadístico solo el residuo de presión. Qmax a 3500 rpm ya está en la tesis. La geometría de la etapa no está en los Excel. El híbrido sigue siendo una propuesta, no un resultado.

## Qué podría llegar a ser un aporte adicional

Un aporte adicional tendría que hacer algo que este artículo no hace: por ejemplo, predecir el incremento de presión fuera de las curvas usadas para estimar la frontera, con el error medido en condiciones no vistas. Declarar ese aporte ahora sería anterior a la evidencia. Esta actividad no revisó la bibliografía posterior a 2019.

## Qué no se puede sostener

- Que el rótulo `DP2-3` esté definido con esas letras en la tesis o en los artículos. La lectura en psi es una interpretación.
- Que `Flow rate` esté en m³/s o en L/s. Esas son unidades del artículo de 2018b. Los números del Excel siguen a los bpd de la tesis.
- Que `GVF0` sea una fracción entre 0 y 1. Las figuras usan porcentaje.
- Que un modelo de Machine Learning mejore el modelo mecanicista de Zhu.
- Que el trabajo de este laboratorio sea original frente a la literatura posterior a 2019. Las fuentes leídas son el artículo de 2019, el de 2018b, la tesis de 2017 y los Excel de Mendeley Data, DOI 10.17632/fk2b4r69bs.1, licencia CC BY 4.0.

Los datos experimentales siguen siendo de Jianjun Zhu y colaboradores. Este laboratorio no los midió.
