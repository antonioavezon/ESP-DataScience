# Diccionario científico de variables

Fuentes, en este orden:

1. Jianjun Zhu, Jiecheng Zhang, Guangqiang Cao, Qingqi Zhao, Jianlin Peng, Haiwen Zhu y Hong-Quan Zhang, *Modeling flow pattern transitions in electrical submersible pump under gassy flow conditions*, Journal of Petroleum Science and Engineering, 180 (2019), 471-484. Archivo local: `docs/esp_gassy_flow_paper.pdf`. No está en Git.
2. Jianjun Zhu, Haiwen Zhu, Zhihua Wang, Jiecheng Zhang, Ruben Cuamatzi-Melendez, Jose Alberto Martinez Farfan y Hong-Quan Zhang, *Surfactant effect on air/water flow in a multistage electrical submersible pump (ESP)*, Experimental Thermal and Fluid Science, 98 (2018), 95-111. Archivo local: `ProjectESP/Papers/Zhu 2018b.pdf`.
3. Jianjun Zhu, *Experiments, CFD Simulation and Modeling of ESP Performance under Gassy Conditions*, tesis doctoral, The University of Tulsa, 2017. Archivo local: `ProjectESP/Papers/Thesis/Two-phase/Zhu 2017 (PhD thesis).pdf`.

La bomba de esos ensayos es una TE-2700, serie 538, de 14 etapas. Los Excel de Mendeley se llaman «zero IPA». IPA es isopropanol. El artículo de 2018b y la tesis incluyen la serie sin surfactante, concentración 0 %.

Una correspondencia es interpretación cuando el texto define la magnitud y el Excel usa otro rótulo. Eso se declara. No se inventa una unidad que contradiga el rango de los números.

Niveles de certeza:

- Alta: el texto define el símbolo, la fórmula, la unidad o el número.
- Media: el diseño del ensayo o el orden de magnitud enlazan un rótulo del Excel con esa definición, y el archivo no escribe el símbolo.
- Pendiente: ninguna de las tres fuentes lo confirma.

## Qgd

| Campo | Contenido |
|---|---|
| Nombre original | Qgd, caudal de gas adimensional |
| Traducción | Caudal de gas adimensional |
| Definición física | Caudal de gas dividido por el caudal de flujo abierto de la ESP |
| Unidad | Adimensional |
| Fórmula | Qgd = QG / Qmax |
| Ubicación | Artículo de 2019, sección 4. Artículo de 2018b, ecuación (5). Tesis, ecuación (2.7) |
| Correspondencia | Rótulo de condición en `mapping.xlsx`. No es una columna fila a fila |
| Certeza | Alta |

Qmax, en la tesis, sección 2.1.2, es el caudal abierto de la TE-2700 a 3500 rpm: **4900 bpd**. El artículo de 2018b lo define como caudal líquido máximo, en m³/s, y no da ese número. No se calcula aquí el Qmax a 1800 rpm.

## QL

| Campo | Contenido |
|---|---|
| Nombre original | QL |
| Traducción | Caudal de líquido |
| Definición física | Caudal volumétrico de líquido en la admisión. En mapping disminuye desde el caudal abierto. En surging queda fijo en una fracción de QBEP |
| Unidad | En la tesis, las curvas de este ensayo se comentan en bpd. En el artículo de 2018b, la nomenclatura usa m³/s y la matriz de ensayos lista L/s. El punto de mejor eficiencia es 2700 bpd, equivalentes a 0,005 m³/s, a 3500 rpm |
| Fórmula | No aplica |
| Ubicación | Tesis, secciones 2.1.2 y 2.3.3. Artículo de 2018b, nomenclatura y sección 2 |
| Correspondencia | Columna `Flow rate` de `mapping.xlsx` |
| Certeza | Alta para el significado. Alta, como interpretación, para leer esa columna en bpd |

Los valores de `Flow rate` llegan a unos 4500 y quedan por debajo de 4900 bpd. No coinciden con 0,005 m³/s ni con 5 L/s. El encabezado del Excel no imprime «bpd». La unidad se toma de la tesis, que describe estas mismas curvas.

## QG

| Campo | Contenido |
|---|---|
| Nombre original | QG |
| Traducción | Caudal de gas |
| Definición física | Caudal volumétrico de gas en la admisión. En mapping queda fijo. En surging aumenta desde cero |
| Unidad | Volumétrica en la definición de Qgd. La matriz del artículo de 2018b anota además el caudal másico de gas en g/min. No hay una columna QG en los Excel |
| Fórmula | Qgd = QG / Qmax. También entra en GVF = QG / (QG + QL) |
| Ubicación | Artículo de 2018b, ecuaciones (3) y (5). Tesis, ecuaciones (2.5) y (2.7) |
| Correspondencia | En mapping, el rótulo Qgd. En surging, no hay caudal de gas; hay `GVF0` |
| Certeza | Alta para la definición. No se reconstruye QG numérico: haría falta aplicar Qmax, y Qmax está dado a 3500 rpm |

## DP2-3

| Campo | Contenido |
|---|---|
| Nombre original | DP2-3, solo en los Excel. En los textos, diferencial de presión de etapa |
| Traducción | Incremento de presión de la etapa 3 |
| Definición física | Presión diferencial medida entre etapas. La primera toma está en el difusor de la etapa 2, así que no hay incremento de las etapas 1 y 2. Los resultados publicados son de la etapa 3. El instrumento citado es el transductor diferencial Rosemount 3051S |
| Unidad | psi en la tesis. El incremento en el mejor punto, a 3500 rpm, es 22,5 psi. La altura a caudal nulo es 30 psi. El artículo de 2018b grafica esa misma magnitud en kPa. El artículo de 2019 llama ΔP al incremento de etapa y lo lista en Pa |
| Fórmula | No hay una fórmula del rótulo. Np = (ΔP bifásico / ΔP agua) × (ρ agua / ρ mezcla) es otra variable, normalizada, del artículo de 2018b |
| Ubicación | Tesis, sección 2.1.2 y eje de la Figura 2.2. Artículo de 2018b, sección 2.1 y sección 3.2 |
| Correspondencia | Columna `DP2-3` de mapping y de surging |
| Certeza | Media. El rótulo `DP2-3` no aparece en la tesis ni en los artículos. El enlace es la toma de la etapa 3 y el hecho de que los números del Excel están en el orden de 22,5 psi y de 30 psi, no en el de los pascales |

## Flow rate

| Campo | Contenido |
|---|---|
| Nombre original | Flow rate, rótulo de `mapping.xlsx` |
| Traducción | Caudal |
| Definición física | Caudal de líquido del bloque, QL |
| Unidad | bpd, por la tesis. Véase QL |
| Fórmula | No aplica |
| Ubicación | Tesis, sección 2.3.3, donde los quiebres de mapping se dan en bpd |
| Correspondencia | Columna pareja de `DP2-3` en cada condición de mapping |
| Certeza | Alta como interpretación de QL en bpd. El encabezado no escribe la unidad |

`surging.xlsx` no tiene esta columna. El líquido queda en `0.75Qbep`, `Qbep` y `1.25Qbep`.

## Rotary speed

| Campo | Contenido |
|---|---|
| Nombre original | N, *rotational speed*. En mapping, `rotary speed`. En surging, `Rotary Speed (rpm)` |
| Traducción | Velocidad de rotación |
| Definición física | Velocidad de giro de la ESP |
| Unidad | rpm |
| Fórmula | No aplica |
| Ubicación | Tesis, sección 2.3.3. Artículo de 2018b, sección 3.3. Artículo de 2019, Figs. 7 a 9 |
| Correspondencia | 1800 y 3500 escritos en Mapping/`50psig` y en las tres hojas de surging |
| Certeza | Alta |

En Mapping/`100psig` y Mapping/`150psig` la celda de velocidad está vacía. El diseño del ensayo asigna de todos modos la velocidad por el conjunto de Qgd, igual en las tres hojas:

- Primera franja, Qgd = 0,005, 0,01 y 0,015: **1800 rpm**.
- Segunda franja, Qgd = 0,01, 0,02, 0,03, 0,04 y 0,05: **3500 rpm**.

Esa asignación está en la tesis, sección 2.3.3, y en el artículo de 2018b, sección 3.3. La certeza de la velocidad es alta por el diseño experimental, y la celda sigue vacía.

## Psep

| Campo | Contenido |
|---|---|
| Nombre original | Psep, presión del separador |
| Traducción | Presión del separador |
| Definición física | Presión regulada en el separador para fijar la admisión. La tesis la establece en 50, 100 y 150 psig. El artículo de 2018b usa 345, 689 y 1034 kPa, los mismos tres niveles |
| Unidad | psig en la tesis y en el artículo de 2019. kPa en el artículo de 2018b |
| Fórmula | No aplica |
| Ubicación | Tesis, sección 2.1.1. Artículo de 2019, Figs. 3, 4 y 7 a 9 |
| Correspondencia | Nombres de hoja `50psig`, `100psig` y `150psig` |
| Certeza | Alta |

## GVF

| Campo | Contenido |
|---|---|
| Nombre original | GVF, fracción volumétrica de gas en la admisión. En el Excel, `GVF0` |
| Traducción | Fracción volumétrica de gas de entrada |
| Definición física | Cociente entre el caudal de gas y la suma de los caudales de gas y de líquido, ambos en la admisión |
| Unidad | La fórmula es una fracción. Las figuras de la tesis rotulan el eje como Intake GVF (%). La nomenclatura del artículo de 2018b también dice % |
| Fórmula | GVF = QG / (QG + QL) |
| Ubicación | Tesis, ecuación (2.5). Artículo de 2018b, ecuación (3) |
| Correspondencia | Columna `GVF0` de `surging.xlsx` |
| Certeza | Alta para la fórmula. Media para la columna: el sufijo 0 no está definido, y los valores superan 1, así que coinciden con el porcentaje de las figuras y no con una fracción entre 0 y 1 |

## Single Phase

| Campo | Contenido |
|---|---|
| Nombre original | Ensayo monofásico de agua. En mapping, `Single Phase` |
| Traducción | Agua sin gas y sin IPA |
| Definición física | Curva de la bomba con agua. En la serie zero IPA no hay isopropanol. En surging, el gas parte de cero |
| Unidad | No aplica al rótulo |
| Fórmula | No aplica |
| Ubicación | Tesis, sección 2.3.1. Artículo de 2018b, sección 3.1, concentración de surfactante 0 % |
| Correspondencia | Bloque `Single Phase` de mapping, al mismo nivel que los rótulos Qgd |
| Certeza | Alta para la curva de agua. Media para afirmar que cada celda del bloque tiene QG exactamente nulo: el archivo no lo escribe |

## Stage pressure increment

| Campo | Contenido |
|---|---|
| Nombre original | *Stage pressure increment*. Símbolo ΔP en el artículo de 2019 |
| Traducción | Incremento de presión de una etapa |
| Definición física | Aumento de presión de una etapa. En estos ensayos, la etapa 3 |
| Unidad | psi en la tesis. kPa en las figuras del artículo de 2018b. Pa en la nomenclatura de 2019 |
| Fórmula | La de Np, citada en DP2-3, normaliza este incremento. No sustituye a la columna |
| Ubicación | Tesis, sección 2.1.2. Artículo de 2019, nomenclatura |
| Correspondencia | Columna `DP2-3`, con la certeza media indicada arriba |
| Certeza | Alta para la magnitud en el ensayo. Media para el nombre de la columna |

## QBEP

| Campo | Contenido |
|---|---|
| Nombre original | QBEP |
| Traducción | Caudal de líquido en el punto de mejor eficiencia |
| Definición física | Caudal al que la eficiencia de la etapa es máxima |
| Unidad | 2700 bpd a 3500 rpm en la tesis. 0,005 m³/s a 3500 rpm en el artículo de 2018b. Son el mismo punto |
| Fórmula | Los ensayos de surging fijan el líquido en 0,75 QBEP, QBEP y 1,25 QBEP |
| Ubicación | Tesis, sección 2.1.2. Artículo de 2018b, sección 3.2 |
| Correspondencia | Rótulos `0.75Qbep`, `Qbep` y `1.25Qbep` de `surging.xlsx` |
| Certeza | Alta |

## Lo que ninguna fuente escribe

El sufijo de `GVF0` y el nombre `DP2-3` no aparecen en la tesis ni en los dos artículos. Mendeley Data no publicó otro archivo que los defina. La lectura de esta actividad es la de las tablas anteriores, con la certeza que cada fila declara.
