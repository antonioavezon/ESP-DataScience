# Diccionario de `Copia de FINAL BES-jun.xlsx`

El catálogo que consume el software está en `catalogo_variables_BES-jun.md` y en `../integracion/variables.json`. Este diccionario conserva la lectura de los rótulos. El rango observado no es un límite de operación.

Fuente leída: `entrada/BES_jun.xlsx`. SHA-256 `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`. El libro no se guardó. El perfil está en `data_procesados/`.

El perfil numérico está en `data_procesados/resumen_pozos.csv`.

## Cómo se distingue un registro

Cada hoja se dejó sola. El rótulo `Cluster:` coincide con el nombre de la hoja. El rótulo `Pozo:` trae otro código. El libro no dice cuál de los dos es la llave. No se agruparon hojas. La inspección independiente del libro llega a la misma lectura, en `data_procesados/calidad.md`.

| Hoja | Clúster (B8) | Pozo (B10) | Bomba escrita | Etapas | Hz de operación |
|---|---|---|---|---:|---:|
| QF-554H | QF-554H | QF-084 | S 8000N | 53 | 63 |
| QF-545H | QF-545H | QF-301 | S 8000N | 50 | 57 |
| QF-500H | QF-500H | QF-147 | S 8000N | 36 | 56 |
| QF-378HST | QF-378HST | QF-005 | S6000N | 31 | 67 |
| QF-549HST | QF-549HST | QF-306 | S6000N | 31 | 62 |

Todas las hojas están visibles. No hay nombres definidos de Excel. Hay celdas combinadas y fórmulas. En `QF-549HST`, columna D, hay 13 cachés `#DIV/0!` (promedios de rangos vacíos y fórmulas que los citan). No están en el balance de PIP y THD. Las otras hojas no muestran ese error en la caché.

## Fecha

| Hoja | Fórmula o valor en B6 | Valor cacheado |
|---|---|---|
| QF-554H, QF-545H, QF-500H, QF-378HST | `=TODAY()` | 2026-10-17 |
| QF-549HST | fecha escrita | 2017-09-06 |

`=TODAY()` no es la fecha de una prueba. El cache 2026-10-17 es el día en que el archivo tenía el cálculo guardado.

## Campos usados, con la unidad que escribe la hoja

La fila no es la misma en todas las hojas. El lector busca el rótulo.

| Rótulo | Unidad escrita | Uso en esta iteración | Confianza del mapeo |
|---|---|---|---|
| Pozo | no declarada | Texto del rótulo Pozo. El libro no lo declara llave única frente a Cluster | Pendiente como llave; el rótulo sí está escrito |
| Cluster | no declarada | Identificador de hoja | Alta |
| Referencia | no declarada | Nombre de bomba escrito en la hoja | Alta como texto; no se verificó contra catálogo |
| Etapas | Nº | Número de etapas escrito | Alta como número de la celda |
| ID | inch | Diámetro interno del tubing en la fórmula de fricción | Alta respecto de la celda; no se contrastó con una tabla de tubería |
| Velocidad (condiciones actuales) | Hz | Frecuencia del punto | Alta |
| Caudal (condiciones actuales) | BFPD | Caudal del punto. En QF-005 la celda es `296.5*24` | Alta como BFPD rotulado. El 24 no está definido en otra celda |
| Presión de Sensor | psi | Entrada de «PIP en (ft)». No se renombró a PIP medida | Alta |
| THP | psi | Entrada de «THP en (ft)» | Alta |
| API | ºAPI | F-01 | Alta |
| BS&W | % | La fórmula de densidad lo usa como fracción `(1 - BS&W)` | Pendiente. El número está entre 0.9557 y 0.9766 |
| Densidad del Agua | Lb/gln o Lb/galn, según la hoja | Entrada de la densidad de mezcla | Alta respecto del rótulo; la grafía de la unidad cambia |
| Temperatura de fondo | ºF y, en la celda siguiente, ºC con `(°F-32)/1.8` | Entrada de la corrección de gravedad | Alta |
| Presión de Yacimiento | psi | Inventariada. No entra en el balance transcrito | Alta como número |
| Presión de Burbuja | psi | 130 en las cinco hojas. No se comparó con PIP porque PIP de la hoja está en ft | Alta como número |
| Presión de Prueba | psi | Inventariada | Alta |
| Caudal de Prueba | BFPD | En QF-005 es `295.6*24` = 7094.4, distinto del caudal de operación 7116 | Alta |
| Limite minimo, Cono de eficiencia, Limite maximo | BFPD | Umbrales escritos en la hoja para las reglas candidatas | Alta como texto de la hoja. «Cono de eficiencia» no se interpretó como BEP de catálogo |
| MD (ft), TVD (ft) | ft | La TVD de descarga, intake y sensor entra al balance. La columna Vertical del survey está almacenada como valor, no como fórmula en los puntos leídos | Alta como número cacheado. El método que produjo la columna Vertical no está escrito en un rótulo de ecuación |
| Curva: Caudal, Head, Brake, EFF | BFPD, ft, HP, % | Puntos tabulados. EFF numérico máximo 7.6 en S 8000N y 7.3 en S6000N | El rótulo existe. El significado de esos porcentajes frente al cociente de potencias queda pendiente |

## Fórmulas frente a valores

Vista de fórmulas: `data_only=False`. Vista de valores cacheados: `data_only=True`, sin guardar el libro. Donde ambos existen, el código recalcula y la prueba compara con el cache.

Ejemplos de fórmula, hoja QF-554H:

- `B96 = 141.5/(131.5+G32)` gravedad del crudo.
- `B100 = 8.33*((G26*G34/8.33)+((1-G26)*B98))` densidad.
- `B102 = B100*0.052` gradiente. Rótulo de salida: `psi*ft`.
- `G96 = (B73-((C20-C24)*B102))/B102` PIP en ft.
- `G100 = (2.083*((100/120)^1.85)*((B71/34.3)^1.85)*(1/(B38)^4.8566))*(C18/1000)` fricción.
- `G102 = C18+G100+G98-G96` THD TOTAL.
- Celdas de afinidad, por ejemplo `A86 = E50*($B$83/$G$47)` y la cabeza con el cuadrado de la relación de frecuencias por el número de etapas.

En QF-378HST y QF-500H el caudal de operación o de prueba multiplica un número por 24. El rótulo de unidad de esa fila es BFPD. No se asignó unidad al factor 24.

## Calidad observada

- Un punto de operación por hoja. No hay fechas diarias que ordenar.
- QF-084: caudal 10301 BFPD y límite máximo escrito 10000 BFPD.
- QF-005: caudal de prueba 7094.4 BFPD y caudal de operación 7116 BFPD.
- Las cinco hojas repiten presión de yacimiento 1100 psi, presión de burbuja 130 psi y API 12.
- El survey llega a inclinaciones de unos 90 grados. Hay MD y TVD distintos. No se aplicó el supuesto S-10 del plan («las profundidades informadas son verticales») a este archivo.
- La celda de densidad del bloque de variables copia la densidad en lb/gal y en una hoja el rótulo vecino dice Kg/Lt. No se convirtió.

## Lo que este diccionario no afirma

No afirma que la presión de sensor sea PIP, que el cono de eficiencia sea el BEP del fabricante, ni que los límites BFPD sean un rango operativo aprobado.
