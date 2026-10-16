# Resultados de la actividad 2.14, fase B

La fase A permanece en la versión `2.14-A`. No se cambiaron los pliegues, las huellas ni la métrica principal. Esta fase estima solo M1, la regresión lineal, y M2, el polinomio de grado 2 con cresta. El registro ejecutable es `notebooks/04_entrenamiento_evaluacion_modelos.ipynb`. Las funciones están en `src/esp_datascience/entrenamiento.py`.

No es el cierre de la actividad. La fase C, con la recta por condición, el bosque y el cociente de agua, no está iniciada. No hay un ganador.

## Objetivo e hipótesis

El objetivo es `dp2_3_psi`, leído como el incremento de presión de la etapa 3, en psi, con la certeza media del diccionario. No es la presión absoluta. Mapping y surging se ajustan por separado.

- H0: M2 no mejora el error absoluto medio de M1.
- H1: M2 reduce ese error sobre curvas independientes.

Estas hipótesis orientan la comparación. El protocolo no fijó una prueba de significación. La métrica principal es el MAE en psi con igual peso por curva. La diferencia pareada es ΔMAE = MAE(M2) − MAE(M1). Un valor negativo indica menor error de M2 en esa curva.

## Diseño que no se reabrió

Huella de mapping: `f35be865a01a6255cc08afdccb96863184ad394a550d9a5249d42b4041a8d948`.

Huella de surging: `71c4818c4b3a5bce0d363c5df658e04141ce1c1301e72f754d5805a52c9dc742`.

Hay 30 curvas de mapping y 18 de surging, en tres pliegues externos. Cada curva es prueba una sola vez. Alpha de M2 se elige en el anillo interno, entre 0,01, 0,1, 1, 10 y 100, por el MAE interno con igual peso por curva. El grado sigue fijo en 2. El escalado y el polinomio se ajustan solo con las filas de entrenamiento de ese paso. En mapping, el cero de Qgd existe solo en la copia técnica del pipeline. El CSV conserva 87 ausencias y ese cero no es una medición.

El orden de M2 es: preparar, polinomio, quitar la columna idénticamente nula, escalar, cresta. En mapping la columna nula es el producto del indicador de agua por el Qgd técnico.

## Tabla comparativa

MAE, RMSE y sesgo dan el mismo peso a cada curva. R² usa las observaciones externas juntas, así que las curvas largas pesan más. El MAE por fila queda como referencia secundaria.

| Protocolo | Modelo | MAE por curva (psi) | RMSE por curva (psi) | Sesgo (psi) | R² |
|---|---|---:|---:|---:|---:|
| Mapping | M1 | 3,999 | 4,865 | 0,043 | 0,543 |
| Mapping | M2 | 1,364 | 1,707 | 0,025 | 0,940 |
| Surging | M1 | 2,312 | 2,734 | 0,136 | 0,894 |
| Surging | M2 | 1,114 | 1,353 | 0,146 | 0,962 |

El MAE por fila, secundario, es 4,382 psi y 1,462 psi en mapping, y 2,132 psi y 1,225 psi en surging. No cambia cuál modelo queda más bajo. La resta de los MAE ya redondeados no coincide en la milésima con la media de ΔMAE: esa media, sin redondear antes, es −2,634 psi en mapping y −1,199 psi en surging.

La media de ΔMAE es −2,634 psi en mapping y −1,199 psi en surging. La mediana es −2,883 psi y −0,902 psi. El mínimo es −5,139 psi y −3,378 psi. El máximo es +0,451 psi y +0,265 psi. M2 tiene menor MAE en 29 de 30 curvas de mapping y en 17 de 18 de surging.

Las dos curvas en que M2 no mejora son `150psig|1800|Single Phase` (0,892 psi frente a 1,343 psi) y `150psig|3500|0.75Qbep` (1,024 psi frente a 1,290 psi).

## Alpha y error de entrenamiento

En mapping los tres pliegues eligen alpha = 0,1. En surging eligen 0,01, 1 y 0,01. La penalización de surging depende del pliegue. No se usó la prueba externa para esa elección, y no se refinó la rejilla después de ver el error externo.

El MAE de entrenamiento no es evidencia de generalización. En mapping, M2 queda cerca: alrededor de 1,27 psi en entrenamiento y 1,364 psi fuera. En surging el pliegue 0 separa 0,702 psi de entrenamiento y 1,335 psi externos. Ese externo sigue por debajo de los 2,468 psi de M1 en el mismo pliegue. M1 no abre un hueco parecido entre entrenamiento y prueba.

## Dónde se concentra el error

En mapping, M1 pasa de 1,430 psi a 1800 rpm a 5,711 psi a 3500 rpm. M2 baja esas cifras a 0,636 psi y 1,850 psi. El peor MAE de M1 es `150psig|3500|Qgd=0.01`, 7,666 psi; M2 lo deja en 2,527 psi. Entre presiones, M2 se mantiene entre 1,200 psi y 1,466 psi.

En surging, M1 se equivoca más a 1800 rpm (2,809 psi) que a 3500 rpm (1,816 psi), y más en 0,75 de QBEP (2,931 psi). M2 deja 0,859 psi a 1800 rpm y 1,368 psi a 3500 rpm. El sesgo de surging no se corrige: sigue cerca de 0,14 psi y cambia de signo entre el bloque 0,75, positivo, y el bloque QBEP, negativo.

En mapping el sesgo de los dos modelos es positivo a 1800 rpm y negativo a 3500 rpm. También cambia de signo entre las tres presiones. La bajada del MAE no elimina ese patrón.

## Lectura física

Las predicciones se evaluaron en los caudales y GVF0 medidos. No se alargó la abscisa. Aun así hay incrementos predichos negativos, y ninguna medición de estos CSV lo es. M1 produce 1 fila negativa en mapping y 34 en surging. M2 produce 22 y 12. El mínimo de M2 llega a −7,292 psi en mapping y a −6,230 psi en surging. Esas filas coinciden con mediciones bajas, del orden de 0,1 psi a 2,5 psi.

La media por curva respeta el salto de velocidad: en mapping, cerca de 4,3 psi a 1800 rpm y de 15,4 psi a 3500 rpm, tanto en la medición como en las dos predicciones. Eso no convierte al coeficiente lineal de la velocidad en una ley de afinidad. En los tres pliegues de mapping ese coeficiente es de unos 0,010 psi/rpm, y el de Qgd técnico es de unos −190 psi por unidad de ese código, cerca de −1,9 psi por cada 0,01. El cero técnico no es un Qgd medido, y el coeficiente no es un efecto aislado.

En las curvas de agua, la medición y M1 decrecen de forma estricta con el caudal. M2 no llega a ese −1 de Spearman. El caso más débil es `50psig|3500|Single Phase`, con −0,655. La curvatura que baja el error también dobla la curva de agua.

Entre curvas de mapping de la misma hoja y velocidad, ordenadas por el Qgd medido, la medición no sube al aumentar el gas a 1800 rpm. A 3500 rpm sube en uno de cada cuatro pasos. M1 no sube en ningún paso. M2 sube solo en el grupo de 100 psig y 3500 rpm. En surging, dentro de cada curva, la medición y las dos predicciones bajan al subir GVF0.

Los coeficientes de M2 no se tabulan como efectos físicos. Están escalados, y el cuadrado del indicador de agua repite al indicador.

## Qué queda provisional

En estas particiones, M2 tiene menor MAE y menor RMSE que M1 en los dos protocolos, y la diferencia tiene el mismo signo en casi todas las curvas. H0 no describe ese resultado. No se declara rechazada por una prueba que el protocolo no definió.

Tampoco se declara a M2 superior según la regla completa de la actividad 2.13. El sesgo todavía cambia de signo entre velocidades o bloques, no se repitió mapping sin la velocidad asignada por el diseño, y faltan los otros modelos. La fase D es la que puede cerrar esa comparación.
