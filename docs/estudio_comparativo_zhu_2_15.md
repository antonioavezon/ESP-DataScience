# Análisis comparativo de enfoques físico-experimentales y predictivos basados en datos para el estudio del comportamiento de bombas electrosumergibles bajo condiciones de flujo gas-líquido

Actividad 2.15. Laboratorio ESP-DataScience. Informe abierto el 16 de octubre de 2026.

Este informe no cierra la actividad 2.15. No compite con los trabajos de Jianjun Zhu ni declara que los modelos M1 a M5 sean superiores a sus formulaciones. La actividad 2.14 está cerrada y sus cifras no se recalculan aquí.

## 1. Propósito

El gas libre en una bomba electrosumergible, en adelante ESP, reduce el incremento de presión y puede volver inestable la operación. Zhu y sus colaboradores estudiaron ese fenómeno con ensayos, mapas de patrón de flujo y modelos mecanicistas. Este laboratorio, sobre el conjunto publicado de agua y aire sin isopropanol, estimó el incremento de presión de la etapa con varios predictores y un protocolo congelado.

La pregunta de esta actividad es cómo pueden usarse juntas la descripción física ya publicada y la predicción estadística reproducible. No se implementa un modelo híbrido de física e inteligencia artificial. No se estima presión de fondo ni se construye un detector de anomalías.

## 2. Fuentes localizadas

Se leyeron, en los archivos locales, las partes que se citan. No se afirma haber reescrito todas las ecuaciones de cada PDF.

| Documento | Archivo local | Qué se leyó en esta actividad |
|---|---|---|
| Zhu et al. (2019), *Journal of Petroleum Science and Engineering*, 180, 471–484. DOI 10.1016/j.petrol.2019.05.059 | `docs/esp_gassy_flow_paper.pdf`, 14 páginas | Resumen, diseño experimental, definición de los ensayos, conclusiones y la frase que llama a Qgd un caudal de gas adimensional |
| Zhu (2017), tesis doctoral, The University of Tulsa | `ProjectESP/Papers/Thesis/Two-phase/Zhu 2017 (PhD thesis).pdf`, 250 páginas | Bomba, sensores, ecuaciones (2.5) a (2.7) y el procedimiento de surging y mapping. No se releyó el texto completo |
| Zhu y Zhang (2018), *Energies*, 11, 180. DOI 10.3390/en11010180 | `ProjectESP/Papers/Zhu 2018.pdf`, 41 páginas | Resumen y el primer párrafo de la introducción. Las correlaciones internas de la revisión no se reimplementan |
| Zhu et al. (2018), *Experimental Thermal and Fluid Science*, 98, 95–111 | `ProjectESP/Papers/Zhu 2018b.pdf` | Portada y título. Es un estudio de surfactante. No se tratan sus ecuaciones como intercambiables con la serie sin isopropanol |
| Datos Mendeley, DOI 10.17632/fk2b4r69bs.1 | `data/raw/mapping.xlsx` y `data/raw/surging.xlsx` | Copias ya normalizadas en la actividad 2.12. No se volvió a descargar el conjunto |

Otros PDF de Zhu están en `ProjectESP/Papers/` (2014, 2016, 2016a, 2017, 2017a, 2018a, 2018c, 2018d, 2018e, 2019, 2019a, 2019b). En esta actividad solo se leyó el título de archivo o la ficha de `pdfinfo`. No se usan sus ecuaciones. El archivo `Zhu 2019c.pdf` es otra copia del artículo de 2019. `Zhu 2019.pdf` repite, según su ficha, el artículo numérico de 2018 sobre patrones de flujo.

## 3. Reconstrucción del enfoque de Zhu

### 3.1 Artículo de 2019

El resumen dice que el incremento de presión de la ESP se degrada cuando aumenta la fracción volumétrica de gas en la admisión, y que el surging y las inestabilidades dependen de esa fracción y de la velocidad de rotación. El modelo propuesto traza fronteras entre flujo de burbujas dispersas, flujo de burbujas, flujo intermitente y flujo segregado.

La sección experimental remite el banco a un trabajo previo y resume dos esquemas. En surging, el caudal de líquido queda fijo y el de gas sube desde cero hasta que la bomba se acerca a un desempeño nulo. En mapping, el caudal de gas queda fijo y el de líquido baja desde el caudal abierto. La comparación del modelo con los datos se hace buscando quiebres en las curvas de altura frente a caudal, no ajustando el incremento de presión punto a punto. Las conclusiones dicen que el mapa calculado concuerda con los quiebres de sus ensayos y con datos de Gamboa (2008) en otra bomba, la GC6100, a 2400 rpm. El propio artículo deja para después mejores correlaciones de tamaño de burbuja, coeficiente de arrastre y fracción crítica de gas.

Las figuras 3 y 4 del artículo, de surging y mapping en la etapa 3 a 50, 100 y 150 psig, aparecen atribuidas a Zhu et al. (2018). Este informe no comprobó, fila por fila, que el Excel de Mendeley coincida con los puntos impresos de esas figuras.

### 3.2 Tesis de 2017

En las páginas 20 a 80 del PDF se lee que la bomba estudiada es una TE-2700 de 14 etapas, serie 538. El punto de mejor eficiencia es 2700 bpd a 3500 rpm, con un incremento de presión de etapa de 22,5 psi. El caudal abierto máximo a 3500 rpm es 4900 bpd y la altura de corte es 30 psi. Los transductores de presión son Rosemount 2051S. Las diferencias de presión de las etapas usan Rosemount 3051S. La temperatura usa Rosemount 3144.

La sección 2.2.2 define, en la página impresa siguiente a la 52:

- fracción volumétrica de gas en la admisión, ecuación (2.5): GVF = Qg / (Qg + Ql);
- caudal de líquido normalizado, ecuación (2.6): Qld = Ql / Qmax;
- caudal de gas normalizado, ecuación (2.7): Qgd = Qg / Qmax.

Qg y Ql son caudales volumétricos en la admisión. Qmax es el caudal abierto de líquido. Qgd no es, por esa definición, un caudal en barriles por día.

El procedimiento 2.2.2.2 distingue surging, con líquido fijo y gas en aumento, de mapping, con gas fijo y líquido variable. El separador se regula a 50, 100 y 150 psig. La tesis también describe inyección de surfactante y concentraciones de isopropanol. Esas series no son el archivo «zero IPA» que usa este laboratorio.

### 3.3 Revisión de 2018

El resumen de *Energies* presenta una revisión de factores que afectan el desempeño con gas, de modelos empíricos y mecanicistas del incremento de presión, y de modelado por dinámica de fluidos computacional. En esta actividad se leyeron el resumen y el arranque de la introducción. No se verificó, ecuación por ecuación, el inventario de correlaciones de esas 41 páginas. Por eso no se calcula un error contra ninguna de ellas.

### 3.4 Lo que no se mezcla

La tesis, el artículo de surfactante de 2018, la revisión de 2018 y el artículo de fronteras de 2019 no son el mismo experimento ni el mismo objetivo. Una ecuación de tamaño de burbuja o de surfactante no se traslada al Excel sin volver a leer su fuente y su dominio.

## 4. Reconstrucción del enfoque de ESP-DataScience

Las actividades 2.11 a 2.13 identificaron variables, normalizaron las tablas y eligieron candidatos sin entrenar. La actividad 2.14, cerrada el 16 de octubre de 2026, estimó cinco modelos con el protocolo `2.14-A`. El objetivo es `dp2_3_psi`, el incremento de presión de la etapa 3 en psi, con certeza media. La unidad de validación es la curva completa. La métrica principal es el MAE por curva, en psi. Las huellas de los pliegues siguen siendo las publicadas.

Los papeles, tomados del informe de la 2.14 y no recalculados aquí, son estos:

- M1, regresión lineal, referencia interpretable.
- M2, polinomio de grado 2 con cresta, referencia no lineal declarada antes del error externo.
- M3, regresión por condición, con extrapolación de presión en parte de las curvas.
- M4, bosque aleatorio de profundidad limitada. Es el menor MAE observado: 1,044 psi en mapping y 0,754 psi en surging.
- M5, cociente respecto de la curva de agua de entrenamiento. Solo cubre 5 de 30 curvas de mapping, con MAE 2,078 psi en ese subconjunto.

No hay ganador único. La regla de la actividad 2.13 no se cumple: el signo del sesgo cambia entre velocidades o presiones, y la velocidad de diseño está confundida con la presión de la hoja. M4 no impone una restricción hidráulica; promedia valores de entrenamiento. En las curvas de agua, M1 y M3 no suben al aumentar el caudal; M2 y M4 sí tienen ascensos locales. El detalle y los intervalos están en `docs/informe_final_actividad_2_14.md` y en `docs/resultados_modelos_2_14.md`.

## 5. Comparabilidad

| Aspecto | Juicio |
|---|---|
| Objetivo | No comparable de forma directa. Zhu 2019 predice fronteras de patrón. Este laboratorio predice `dp2_3_psi` |
| Unidades del objetivo | El MAE en psi no tiene contraparte publicada, en los textos leídos, como error punto a punto del mismo incremento |
| Qgd y GVF | No son la misma variable. Qgd = Qg/Qmax. GVF = Qg/(Qg+Ql). En surging, `gvf0_porcentaje` es un porcentaje de esa fracción, no el código Qgd |
| Caudal líquido | Comparable solo como tendencia, en bpd, dentro de la TE-2700 y de las velocidades ensayadas |
| Velocidad y presión de separador | Las condiciones 1800 y 3500 rpm, y 50, 100 y 150 psig, aparecen en ambos usos de este banco. Eso no vuelve idénticos los objetivos |
| Geometría | La tesis describe la TE-2700. El artículo de 2019 también compara una GC6100 de Gamboa. El Excel no trae álabes, áreas ni ángulo de salida |
| Protocolo de validación | No comparable. Zhu diagnostica quiebres de curva. Aquí se apartan curvas completas antes de ver el error externo |
| Métricas | Un MAE solo sería comparable con equivalencia de objetivo, unidades, datos y protocolo. Esa equivalencia no está verificada |
| Conjunto | El Excel es el conjunto Mendeley asociado por el laboratorio al artículo de 2019, serie sin isopropanol. No se repitió una identidad punto a punto con las figuras |

Una comparación cuantitativa de error queda bloqueada. Faltan la ecuación verificada para un objetivo común, el dominio aplicable a `dp2_3_psi` y los datos de geometría que el modelo de fronteras utiliza. El módulo `src/esp_datascience/comparacion_zhu.py` rechaza ese cálculo si falta alguna condición. No estima variables ausentes.

## 6. Tendencias, separadas por tipo de enunciado

Observación de Zhu, en el resumen de 2019 y en la discusión de las curvas de mapping: el incremento de presión se degrada al aumentar el gas, y a mayor Qgd la caída respecto de la curva de agua aparece a un caudal de líquido más alto. Al bajar la presión del separador, la desviación también aparece antes. Esas frases describen sus curvas, no una predicción de M1–M5.

Observación de este laboratorio, ya publicada en la fase D y no reajustada: en las seis familias de hoja y velocidad de mapping, la medición, M1 y M2 no suben al aumentar Qgd en el caudal de líquido común. M3 sube en cinco de esas seis. M4 sube en una. En surging, la correlación de Spearman entre `gvf0_porcentaje` y la predicción de M1, M2 y M3 es −1 en las 18 curvas. Eso es una tendencia del mismo conjunto, no una confirmación independiente del experimento de Zhu.

Interpretación de Zhu: los quiebres de la curva de altura se asocian, siguiendo a Gamboa y Prado, con cambios de patrón. Este laboratorio no localizó esos quiebres en sus tablas. No se presentan como mediciones de este cuaderno.

Predicción de M1–M5: estiman `dp2_3_psi` dentro de las curvas apartadas. No clasifican burbuja dispersa, intermitente o segregado.

Hipótesis nueva, no resultado: un indicador de gas definido como en las ecuaciones (2.5) o (2.7) podría entrar después como restricción o como residuo. Hoy el Excel de mapping no trae Qg en barriles por día, y convertir Qgd exigiría el Qmax de cada velocidad. La tesis publica 4900 bpd a 3500 rpm. No se aplica esa cifra a las filas.

## 7. Modelos, sin tabla de error cruzada

El modelo de 2019 parte del balance de cantidad de movimiento en el rodete y formula fronteras. Pide geometría, propiedades del fluido y cierres de burbuja y arrastre. Su validación publicada, en lo leído, es el acuerdo visual con quiebres, no un MAE en psi.

M1 a M4 usan las columnas ya congeladas: en mapping, caudal, indicador de agua, Qgd, velocidad y presión de separador; en surging, fracción de gas, fracción del caudal de mejor eficiencia, velocidad y presión. No usan densidad de mezcla ni ángulo de álabe. M5 usa la curva de agua de la misma hoja y velocidad, solo si esa curva está en el entrenamiento y el caudal de la curva de gas cae dentro de ella.

No se implementan las ecuaciones de Zhu. No se calibran con las curvas externas de la 2.14.

## 8. Fortalezas y limitaciones, por criterio

| Criterio | Enfoque de Zhu, en lo leído | Enfoque de la actividad 2.14 |
|---|---|---|
| Mecanismo | Formula patrones y fronteras. Explica una degradación por gas | No identifica el patrón. Describe el incremento con predictores |
| Predicción de `dp2_3_psi` | No es el objetivo del artículo de 2019 | M1–M4 cubren las curvas del protocolo. M4 tiene el menor MAE observado en esas curvas |
| Sensibilidad al gas | El diseño varía gas a líquido fijo o líquido a gas fijo | La tendencia medida y varias predicciones bajan al aumentar el gas, con las excepciones ya publicadas de M3 y M4 |
| Generalización | El artículo muestra otra bomba, GC6100, para fronteras, no para el MAE de esta etapa | No hay otra bomba en el protocolo. El intervalo bootstrap no sale de estas curvas |
| Interpretabilidad | Alta en la estructura física, si se aceptan los cierres | M1 es la referencia legible. M4 no lo es |
| Instrumentación | Banco con caudal, presión de separador, etapa y, en la tesis, densidad | El modelo estadístico solo ve las columnas del Excel |
| Datos | Curvas de desempeño y, para el mapa, quiebres | Cientos de filas de dos protocolos, con pliegues por curva |
| Reproducibilidad | El artículo y la tesis publican el diseño. Este laboratorio no rehizo el ensayo | El protocolo, las huellas y las pruebas quedan en el repositorio |
| Incertidumbre | No se extrajo un intervalo estadístico del error de `dp2_3_psi` | Intervalos por curva en la fase D, con las limitaciones de conglomerado y de multiplicidad |
| Operación real | El banco es agua y aire, no un pozo | Tampoco es un pozo. No hay corriente, potencia ni presión de fondo |
| Híbrido | Ofrece relaciones y regímenes que un híbrido podría usar como restricción | Ofrece un residuo medible y un protocolo de curvas. El híbrido no está construido |

«Menor MAE en este protocolo» no equivale a «más útil para explicar el régimen» ni a «más aplicable en un pozo».

## 9. Aportes de este laboratorio

Son aportes de reanálisis, no un experimento nuevo.

- Metodológico: normalización con huella, diccionario con certeza, pliegues por curva y la misma métrica para M1–M4.
- Predictivo: cinco estimadores comparados en esas reglas, con M5 limitado a cinco curvas.
- Físico: no hay una medición nueva. Hay una lectura de coherencia empírica, por ejemplo la caída monótona del agua en M1 y M3 y los ascensos locales de M2 y M4.
- Hipótesis: la integración con fronteras o con un residuo queda propuesta, no demostrada.
- Evidencia experimental original: ninguna. Los puntos siguen siendo los de Zhu.

## 10. Oportunidades de integración

Cada línea es conceptual. Ninguna se implementa en esta actividad.

1. Curva física de referencia y residuo. Física disponible: la degradación respecto de la curva de agua, descrita por Zhu. Estadística disponible: M5, solo en cinco curvas, y el error de M1–M4. Falta: una curva de agua de referencia que no haya servido para elegir el modelo, y Qmax por velocidad si se quiere pasar de Qgd a caudal de gas. Límite: usar las curvas externas para calibrar y luego citar ese error sería circular. Validación futura: reservar curvas que no entren ni en el ajuste físico ni en la elección del predictor.

2. Restricción de monotonía donde el ensayo la respalde. Física: en el agua, la curva de la tesis baja al aumentar el caudal en el tramo mostrado. Estadística: M1 y M3 cumplen esa caída en las seis curvas de agua; M2 y M4 no. Falta un dominio donde la monotonía esté justificada también con gas. Límite: imponerla en todo el mapa puede contradecir un quiebre de régimen. Validación: declarar el dominio antes de ver el error externo.

3. Indicador de gas alineado con las ecuaciones (2.5) y (2.7). Física: GVF y Qgd están definidos. Estadística: mapping usa el código Qgd y surging usa el porcentaje de GVF, en modelos distintos. Falta Qg medido o el Qmax de 1800 rpm para no suponerlo. Límite: no se convierte el código con una hipótesis oculta. Validación: repetir la tendencia solo cuando ambas definiciones estén calculadas con la misma Qmax publicada.

4. Régimen como etiqueta, no como error de presión. Física: cuatro patrones y quiebres. Estadística: ninguna etiqueta de patrón en el Excel. Falta marcar los quiebres con una regla previa. Límite: el laboratorio no los localizó. Validación: una regla escrita antes de mirar el MAE, aplicada a curvas no usadas para afinarla.

5. Incertidumbre del residuo. Física: el artículo señala cierres incompletos de burbuja y arrastre. Estadística: el intervalo de la fase D es de estas curvas. Falta un esquema que separe error de medición, error de cierre y error del predictor. Validación: no leer ese intervalo como validez en otro pozo.

## 11. Brecha hacia el monitoreo sin sensores de fondo

El título amplio del proyecto habla de monitoreo y detección de anomalías sin sensores de fondo. Esta actividad no lo implementa.

En el Excel hay caudal de líquido, códigos de gas o fracción, velocidad, presión de separador e incremento de la etapa 3. En la tesis, el banco mide además densidad de agua, temperaturas de admisión y de la etapa 14, y varias diferencias de presión. No están en las columnas que usan M1–M5 la presión de fondo fluyente, el nivel dinámico, la corriente del motor, la potencia eléctrica, la frecuencia de un variador de pozo ni la presión en cabeza de pozo. La presión del separador del lazo no es la presión de fondo.

Que exista una relación de afinidad o un balance de momentum no vuelve estimable, con estos archivos, una variable de pozo. Habría que declarar la medición, la unidad y un conjunto que no sea el mismo banco de agua y aire.

## 12. Preguntas posteriores

Se ordenan por datos ya disponibles, no por un resultado inventado.

1. ¿El residuo de una curva de agua, ajustado solo con curvas de entrenamiento, reduce el MAE en curvas de gas no usadas para elegir el modelo? Fundamento: la degradación descrita por Zhu. Evidencia que la motiva: M5 cubre 5 de 30 curvas y no ganó el protocolo. Variables: `dp2_3_psi`, caudal, Qgd, velocidad, presión. Datos: una partición nueva, no los tres pliegues ya vistos. Confusión: la misma agua sirve hoy de referencia y de límite de cobertura. Respaldo: MAE menor, con intervalo que no cruce cero, en curvas apartadas de antemano. Rechazo: el residuo no baja el error o solo lo hace en las cinco curvas ya usadas.

2. ¿La monotonía del agua debe exigirse solo en la curva monofásica? Fundamento: la curva de agua de la tesis y la caída observada en M1 y M3. Evidencia: M4 sube 11,291 psi en la peor curva de agua de mapping. Confusión: un corte de 10 psi, usado en la fase D, separa M2 y M4 por estar entre 5,248 y 11,291. Respaldo: una restricción declarada antes del error conserva la caída sin empeorar el MAE de gas en curvas nuevas. Rechazo: la restricción aumenta el error de gas o no está justificada fuera del agua.

3. ¿Un mapa de patrones puede convivir con un predictor de presión sin compartir la misma métrica? Fundamento: objetivos distintos en el artículo de 2019 y en la 2.14. Evidencia: no hay quiebres marcados en las tablas. Datos necesarios: una regla de quiebre y la geometría que el modelo mecanicista pide. Respaldo: las fronteras clasifican regímenes y el predictor, por separado, mantiene su MAE. Rechazo: se publica un solo número de error que mezcla frontera y presión.

## 13. Conclusiones

El enfoque físico-experimental describe la degradación por gas, separa surging de mapping y propone fronteras de patrón. El enfoque de datos, sobre el mismo tipo de banco y la serie sin isopropanol, predice el incremento de la etapa con un protocolo de curvas y muestra que el menor MAE observado es el de M4, sin cumplir la regla que nombraría un ganador.

Coinciden en la bomba y en las presiones y velocidades del banco, y en que más gas se asocia con menos incremento en las tendencias leídas. Difieren en el objetivo, en la validación y en las variables de cierre. Comparten el límite del agua y el aire en un lazo, no en un pozo. Se complementan si la física aporta régimen y referencia, y si la estadística aporta un residuo evaluado en curvas que no sirvieron para elegir el modelo.

Todavía no puede compararse un MAE. No puede decirse que M1–M5 sustituyan los estudios de Zhu, ni que las fronteras hagan innecesario un predictor del incremento. Lo siguiente, si se autoriza, es una de las tres preguntas de la sección 12, con datos y reglas declarados antes de ver el error. Esta actividad queda abierta.

## 14. Cierre administrativo de la 2.14, repetido para quien lea solo este informe

La actividad 2.14 está formalmente cerrada, con las fases A, B, C, D y E completadas y verificadas, el 16 de octubre de 2026. Este párrafo no modifica sus conclusiones ni sus cifras.
