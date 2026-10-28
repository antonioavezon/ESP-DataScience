# Perfil de hojas — BES_jun

Perfilado de estructura. No es una predicción ni una interpretación de funcionamiento.

## Método de lectura

- Archivo leído: `entrada/BES_jun.xlsx`, copia de trabajo de este expediente.
- SHA-256 verificado (archivo de trabajo y `Copia de FINAL BES-jun.xlsx`): `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`.
- El libro no se guardó. No se llamó a `workbook.save()`.
- Vista de fórmulas: `openpyxl` 3.1.5 con `data_only=False`.
- Vista de valores cacheados: segunda carga con `data_only=True`.
- `fullCalcOnLoad` del libro: `True`. `calcMode`: `None`.
- Propiedades del libro: creator=`Alzate`, lastModifiedBy=`Alexander zambrano`, created=`2017-09-06 19:13:28`, modified=`2026-10-17 16:06:09`, title=`None`.
- Tipos de columna: `pandas` 3.0.6, `pandas.api.types.infer_dtype` sobre los valores cacheados (no sobre el texto de la fórmula).
- Significado de etiquetas: se cita el texto del libro. Si el libro no define el término más allá de la etiqueta y de un texto corto en la celda vecina, queda como significado pendiente de documentación.

## Libro

- Hojas: 5 — `QF-554H`, `QF-545H`, `QF-500H`, `QF-378HST`, `QF-549HST`.
- Hojas de gráfico (`chartsheets`): 0.
- Nombres definidos del libro: 0.
- Todas las hojas están en estado `visible`. No hay filas ni columnas ocultas en `row_dimensions` / `column_dimensions`.
- No hay tablas de Excel (`ws.tables` vacío en las cinco hojas).
- No hay validaciones de datos ni comentarios de celda.
- Cada hoja tiene 6 gráficos de tipo `ScatterChart` y 1 imagen embebida. El título del gráfico no pudo leerse (`AttributeError` al acceder a `title.tx`). Abajo se anotan ancla y referencias de serie cuando openpyxl las expone.
- El diseño es un formulario de varias páginas, no una tabla con una fila de encabezados. La misma frase de título se repite. Hay celdas combinadas. El valor de una combinación está en la esquina superior izquierda; el resto de la combinación se lee vacío.

## Títulos repetidos (texto real)

En las cinco hojas aparece, en la columna B, el texto `Análisis de Comportamiento de un Sistema ESP` más de una vez. También aparecen, con variaciones de fila, estos textos:

- `Información Mecánica del Pozo`
- `Información de Producción y Fluido`
- `Condiciones de Operación Actuales`
- `Curva de la Bomba Según Velocidad Actual`
- `Cálculo de Gradiente de Presión`
- `Cálculo de la THD TOTAL`
- `Cálculo de Producción y consumo`
- `Difrencia entre calculos y medición`
- `Cálculo de Consumo Energetico`
- `Analisis de Data Simulada Vs Medida`
- `Actividad de Revisión Equipos 10/08/2017`

Esos textos se citan tal como están escritos, incluidas las grafías `Difrencia`, `Perdidad` y `Energetico` cuando aparecen así en la celda.

La fila donde empieza `Información Mecánica del Pozo` (columna A):

- `QF-554H`: fila 14.
- `QF-545H`: fila 13.
- `QF-500H`: fila 13.
- `QF-378HST`: fila 13.
- `QF-549HST`: fila 13.

`QF-554H` coloca ese título una fila más abajo que las otras cuatro hojas. A partir de ahí, muchas etiquetas de `QF-554H` van desplazadas +1 fila respecto de las demás. Las otras cuatro hojas comparten la misma secuencia de textos de la columna A; `QF-554H` también, con ese desplazamiento, salvo que el conteo de filas finales cambia con el bloque numérico inferior.

Comparación de la secuencia de textos de la columna A:

- QF-554H: la secuencia de textos de la columna A coincide con QF-554H.
- QF-545H: la secuencia de textos de la columna A coincide con QF-554H.
- QF-500H: la secuencia de textos de la columna A coincide con QF-554H.
- QF-378HST: la secuencia de textos de la columna A coincide con QF-554H.
- QF-549HST: la secuencia de textos de la columna A coincide con QF-554H.

## Identificadores escritos en el libro

Cada hoja tiene, en las filas superiores, la etiqueta `Cluster:` junto a un texto en B, y la etiqueta `Pozo:` junto a otro texto en B. El nombre de la hoja coincide con el texto situado junto a `Cluster:`. El texto situado junto a `Pozo:` es distinto en las cinco hojas y distinto del de `Cluster:`. El libro no define qué identifica cada etiqueta. Significado pendiente de documentación. No se agrupó ningún cálculo por una llave supuesta.

| Hoja | Celda junto a `Cluster:` | Celda junto a `Pozo:` | B6 (fórmula o constante) | B6 cacheado | Celda de la etiqueta `Responsable:` |
|---|---|---|---|---|---|
| `QF-554H` | QF-554H | QF-084 | `=TODAY()` | 2026-10-17 | C6 |
| `QF-545H` | QF-545H | QF-301 | `=TODAY()` | 2026-10-17 | D6 |
| `QF-500H` | QF-500H | QF-147 | `=TODAY()` | 2026-10-17 | C6 |
| `QF-378HST` | QF-378HST | QF-005 | `=TODAY()` | 2026-10-17 | D6 |
| `QF-549HST` | QF-549HST | QF-306 | `2017-09-06` | 2017-09-06 | D6 |

Otros textos con el patrón `QF-` se listan en `calidad.md`. El texto `SLACOL R&D` aparece en E6 en las cinco hojas, junto a la etiqueta de responsable. Las celdas de `Cargo:` y `Correo:` se describen en `calidad.md`.

## Encabezados de profundidad y de curva (texto real)

En la zona mecánica, una fila contiene `Profundidad  de` (con dos espacios), `MD (ft)`, `TVD (ft)`, `Variable`, `Valor`, `Unidad`. La fila siguiente contiene `introducir` bajo MD y `Calculada` bajo TVD. Esas palabras están en el libro. El significado de MD, TVD y del resto de etiquetas, más allá de esos textos y de la unidad escrita al lado, queda pendiente de documentación.

La curva con columnas `Caudal`, `Head`, `Brake`, `EFF` y la fila siguiente `BFPD`, `ft`, `HP`, `%` está en las cinco hojas. Detalle numérico en la sección de cada hoja y en `calidad.md`.

## Hojas

### QF-554H

- Estado: `visible`.
- Dimensión openpyxl: `A1:S388` (388 filas × 19 columnas, A–S).
- Celdas no vacías en la vista de fórmulas (valor no nulo): 1234.
- De esas celdas: fórmulas 261; constantes 973 (numéricas 499, texto 472, fechas-tipo en la constante 2).
- Fórmulas con caché nulo: 0. Fórmulas cuyo caché es el mismo texto de la fórmula: 0.
- Celdas combinadas: 82.
- Tablas: ninguna. Nombres definidos: ninguno a nivel de libro.
- Filas vacías dentro de 1..388: 142.
- Columnas vacías dentro de A..S: P.
- Filas ocultas: ninguna. Columnas ocultas: ninguna.
- Vista: `pageBreakPreview`, zoom `90`. Paneles congelados: `None`. Títulos de impresión: filas `None`, columnas `None`.
- Formato condicional (reglas): 0. Validaciones: 0. Comentarios: 0. Imágenes: 1. Gráficos: 6.
- Errores de Excel en fórmula o en caché: 0.

Títulos largos o de sección localizados (coordenada y texto):

- `B2`: `Análisis de Comportamiento de un Sistema ESP`
- `A14`: `Información Mecánica del Pozo`
- `E14`: `Información de Producción y Fluido`
- `E18`: `Presión de Yacimiento`
- `E20`: `Presión de Burbuja`
- `E28`: `Temperatura de fondo`
- `A30`: `Tuberia de Producción`
- `E30`: `Temperatura de fondo`
- `E36`: `Información de Cable Instalado`
- `A40`: `Información de Bomba Instalada`
- `E46`: `Curva de Performance de Bomba`
- `E57`: `Cono de eficiencia`
- `B63`: `Análisis de Comportamiento de un Sistema ESP`
- `B67`: `Condiciones de Operación Actuales`
- `E71`: `Corriente de Motor`
- `E73`: `Factor de Potencia`
- `E75`: `Eficiencia del motor`
- `A77`: `Vibración del Motor`
- `E77`: `Temperatura de Motor`
- `B80`: `Curva de la Bomba Según Velocidad Actual`
- `A82`: `Curva de Performance de Bomba`
- `A94`: `Cálculo de Gradiente de Presión`
- `E94`: `Cálculo de la THD TOTAL`
- `A96`: `Gravedad Oil @ 60ºF`
- `A98`: `Gravedad Oil @ T fondo`
- `A100`: `Densidad de Fluido`
- `E100`: `Perdidad por Fricción`
- `A102`: `Gradiente de Presión`
- `A104`: `Cálculo de Producción y consumo`
- `E104`: `Difrencia entre calculos y medición`
- `A108`: `Potencia a consumir`
- `A110`: `Potencia Transferida`
- `A112`: `Eficiencia de la bomba`
- `B119`: `Análisis de Comportamiento de un Sistema ESP`
- `B123`: `Cálculo de Consumo Energetico`
- `B125`: `Consumo de Potencia Bomba`
- `B127`: `Consumo de Potencia Sello`
- `B129`: `Potencia a entregar por el motor`
- `E131`: `Datos de operación del Motor`
- `E133`: `Porcentaje de carga`
- `E139`: `Caida de Voltaje en el Cable`
- `E141`: `Voltaje @ 1000 ft (V)`
- `B155`: `Información del SUT`
- `B183`: `Análisis de Comportamiento de un Sistema ESP`
- `B187`: `Analisis de Data Simulada Vs Medida`
- `E189`: `Fecha Prueba de Pozo`
- `B229`: `Análisis de Comportamiento de un Sistema ESP`
- `B232`: `Actividad de Revisión Equipos 10/08/2017`
- `A239`: `Temperatura de Fluido`
- `A289`: `Perdida de Energia`
- `B323`: `Análisis de Comportamiento de un Sistema ESP`

Fechas con tipo fecha, o fórmula cuya caché es fecha:

- `B6`: fórmula/constante `=TODAY()`; caché `2026-10-17`.
- `G189`: fórmula/constante `2017-08-07`; caché `2017-08-07`.
- `G195`: fórmula/constante `2017-08-10`; caché `2017-08-10`.

Textos que contienen una secuencia `dd/mm/aaaa` o similar:

- `B232`: `Actividad de Revisión Equipos 10/08/2017` (fragmentos ['10/08/2017']).

Gráficos (ancla = celda aproximada de la esquina superior; referencias de serie tal como las expone openpyxl):

- Gráfico 1: tipo `ScatterChart`, ancla `A47`.
  - Serie 1: title=`Head (ft)`, val=`None`, cat=`None`, xVal=`'QF-554H'!$E$50:$E$55`, yVal=`'QF-554H'!$F$50:$F$55`.
  - Serie 2: title=`None`, val=`None`, cat=`None`, xVal=`'QF-554H'!$I$56:$I$57`, yVal=`'QF-554H'!$J$56:$J$57`.
  - Serie 3: title=`None`, val=`None`, cat=`None`, xVal=`'QF-554H'!$K$56:$K$57`, yVal=`'QF-554H'!$L$56:$L$57`.
  - Serie 4: title=`None`, val=`None`, cat=`None`, xVal=`'QF-554H'!$M$56:$M$57`, yVal=`'QF-554H'!$N$56:$N$57`.
- Gráfico 2: tipo `ScatterChart`, ancla `D81`.
  - Serie 1: title=`Head (ft)`, val=`None`, cat=`None`, xVal=`'QF-554H'!$A$86:$A$91`, yVal=`'QF-554H'!$B$86:$B$91`.
  - Serie 2: title=`Operación Real`, val=`None`, cat=`None`, xVal=`'QF-554H'!$B$71`, yVal=`'QF-554H'!$G$102`.
  - Serie 3: title=`Operación Ideal`, val=`None`, cat=`None`, xVal=`'QF-554H'!$B$106`, yVal=`'QF-554H'!$G$102`.
  - Serie 4: title=`'QF-554H'!$I$83`, val=`None`, cat=`None`, xVal=`'QF-554H'!$J$85:$J$90`, yVal=`'QF-554H'!$K$85:$K$90`.
  - Serie 5: title=`'QF-554H'!$M$83`, val=`None`, cat=`None`, xVal=`'QF-554H'!$N$85:$N$90`, yVal=`'QF-554H'!$O$85:$O$90`.
  - Serie 6: title=`'QF-554H'!$Q$83`, val=`None`, cat=`None`, xVal=`'QF-554H'!$R$85:$R$90`, yVal=`'QF-554H'!$S$85:$S$90`.
  - Serie 7: title=`Menos etapas`, val=`None`, cat=`None`, xVal=`'QF-554H'!$I$72:$I$77`, yVal=`'QF-554H'!$J$72:$J$77`.
- Gráfico 3: tipo `ScatterChart`, ancla `F327`.
  - Serie 1: title=`None`, val=`None`, cat=`None`, xVal=`'QF-554H'!$A$329:$A$384`, yVal=`'QF-554H'!$D$329:$D$384`.
- Gráfico 4: tipo `ScatterChart`, ancla `F359`.
  - Serie 1: title=`None`, val=`None`, cat=`None`, xVal=`'QF-554H'!$E$329:$E$384`, yVal=`'QF-554H'!$A$329:$A$384`.
  - Serie 2: title=`Bomba`, val=`None`, cat=`None`, xVal=`'QF-554H'!$G$357:$G$358`, yVal=`'QF-554H'!$H$357:$H$358`.
- Gráfico 5: tipo `ScatterChart`, ancla `A143`.
  - Serie 1: title=`1 AWG`, val=`None`, cat=`None`, xVal=`'QF-554H'!$J$142:$J$152`, yVal=`'QF-554H'!$K$142:$K$152`.
  - Serie 2: title=`2 AWG`, val=`None`, cat=`None`, xVal=`'QF-554H'!$J$142:$J$152`, yVal=`'QF-554H'!$L$142:$L$152`.
  - Serie 3: title=`'QF-554H'!$N$141`, val=`None`, cat=`None`, xVal=`'QF-554H'!$J$142:$J$152`, yVal=`'QF-554H'!$N$142:$N$152`.
  - Serie 4: title=`Punto de operación`, val=`None`, cat=`None`, xVal=`'QF-554H'!$G$77`, yVal=`'QF-554H'!$G$71`.
- Gráfico 6: tipo `ScatterChart`, ancla `E143`.
  - Serie 1: title=`1 AWG`, val=`None`, cat=`None`, xVal=`'QF-554H'!$J$155:$J$156`, yVal=`'QF-554H'!$K$155:$K$156`.
  - Serie 2: title=`2 AWG`, val=`None`, cat=`None`, xVal=`'QF-554H'!$L$155:$L$156`, yVal=`'QF-554H'!$M$155:$M$156`.
  - Serie 3: title=`4 AWG`, val=`None`, cat=`None`, xVal=`'QF-554H'!$N$155:$N$156`, yVal=`'QF-554H'!$O$155:$O$156`.
  - Serie 4: title=`None`, val=`None`, cat=`None`, xVal=`'QF-554H'!$G$135`, yVal=`'QF-554H'!$G$141`.

Bloque numérico inferior (`Measured`):

- Bloque con encabezado en fila 327: A=Measured, B=Incl. (deg), C=Azim. (deg), D=Vertical, E=Dogleg.
- Fila siguiente: A=Depth (ft), D=Depth(ft), E=(º/100ft).
- Filas con valor numérico en la columna A dentro de ese bloque: 56.
- Columna A (etiqueta de encabezado Measured / Depth (ft)): n=56, min=0, max=4530, p05=636, mediana=2332.5, p95=4258.
- Diferencias entre filas consecutivas de A: n=55, min=31, mediana=78, max=437, p05=44, p95=122.5.
- La columna A de este bloque es estrictamente creciente entre filas consecutivas con número.
- Criterio de espaciamiento irregular: diferencia consecutiva ≤ 0, o mayor que 3× la mediana (78), o positiva y menor que la mediana/3. Pasos que cumplen el criterio: 1 de 55.
- Ejemplos: fila 330 Δ=437.
- Columna B (texto de encabezado Incl. (deg), fila de unidades/subtítulo —): constantes=56, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=56.
  Descriptivo: min=0, p05=0.3725, Q1=9.8375, mediana=31.12, Q3=75.835, p95=90.0925, max=90.68.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-89.1587, 174.831] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
  Diferencia absoluta consecutiva: min=0.01, mediana=1, max=5.99. Pasos con |Δ|>180: 0.
- Columna C (texto de encabezado Azim. (deg), fila de unidades/subtítulo —): constantes=56, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=56.
  Descriptivo: min=0, p05=22.0575, Q1=24.2525, mediana=26.425, Q3=31.67, p95=104.127, max=350.07.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [13.1262, 42.7963] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 4.
  Ejemplos: C329=0; C330=294.02; C331=319.34; C332=350.07.
  Diferencia absoluta consecutiva: min=0.04, mediana=1.23, max=309.24. Pasos con |Δ|>180: 2.
  Esos pasos: filas 329->330: 0 a 294.02 (Δ=294.02); filas 332->333: 350.07 a 40.83 (Δ=-309.24).
- Columna D (texto de encabezado Vertical, fila de unidades/subtítulo Depth(ft)): constantes=56, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=56.
  Descriptivo: min=0, p05=635.993, Q1=1480.33, mediana=2290.47, Q3=2843.63, p95=2892.39, max=2893.18.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-564.626, 4888.58] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
- Columna E (texto de encabezado Dogleg, fila de unidades/subtítulo (º/100ft)): constantes=56, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=56.
  Descriptivo: min=0, p05=0.195, Q1=0.6625, mediana=2.01, Q3=4.8325, p95=6.46, max=6.86.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-5.5925, 11.0875] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
- No hay valores repetidos en la columna A de este bloque.
- No hay filas duplicadas por tupla cacheada A–E en este bloque.

Puntos de la curva con encabezados `Caudal` / `Head` / `Brake` / `EFF`:

- Fila 48: E=Caudal, F=Head, G=Brake, H=EFF.
- Fila 49: E=BFPD, F=ft, G=HP, H=%.
- Filas de puntos con E numérico constante: 6 (filas [50, 51, 52, 53, 54, 55]).
- Puntos (fila, E, F, G, H): 50: 0, 64, 2.5, 0; 51: 2500, 62, 2.6, 4.6; 52: 5000, 58, 2.6, 6.6; 53: 8000, 48, 3, 7.6; 54: 10000, 36, 3.2, 7; 55: 12500, 10, 3.5, 2.4.
- La secuencia de la columna E en esos puntos es estrictamente creciente.
- La secuencia de la columna F en esos puntos es no creciente.
- Fila 56: E=`Limite minimo`, G=2500 (fórmula=False), H=BFPD, caché G=2500.
- Fila 57: E=`Cono de eficiencia`, G=8000 (fórmula=False), H=BFPD, caché G=8000.
- Fila 58: E=`Limite maximo`, G=10000 (fórmula=False), H=BFPD, caché G=10000.

Textos de la columna A que aparecen más de una vez en la misma hoja (etiqueta repetida, no una columna duplicada de una tabla):

- `Caudal`: 4 veces (filas 71, 84, 191, 238).
- `Promedio`: 4 veces (filas 262, 266, 276, 282).
- `Velocidad`: 3 veces (filas 69, 83, 234).
- `Potencia`: 3 veces (filas 201, 208, 215).
- `I Promedio`: 3 veces (filas 256, 270, 286).
- `Potencia KVA`: 3 veces (filas 257, 271, 287).
- `THP`: 2 veces (filas 75, 241).
- `Voltaje entrada`: 2 veces (filas 199, 206).
- `U-V`: 2 veces (filas 259, 273).
- `V-W`: 2 veces (filas 260, 274).
- `U-W`: 2 veces (filas 261, 275).
- `U-N`: 2 veces (filas 263, 279).
- `V-N`: 2 veces (filas 264, 280).
- `W-N`: 2 veces (filas 265, 281).
- `I(U)`: 2 veces (filas 267, 283).
- `I(V)`: 2 veces (filas 268, 284).
- `I(W)`: 2 veces (filas 269, 285).

Rangos combinados:

`C6:D6`, `E71:F71`, `E73:F73`, `E137:F137`, `E34:F34`, `E8:H8`, `E10:H10`, `G110:H110`, `B125:D125`, `B232:G232`, `E100:F100`, `C327:C328`, `A272:G272`, `E75:F75`, `E22:F22`, `B327:B328`, `E102:F102`, `E36:H36`, `A244:G244`, `B323:H324`, `B131:C131`, `A104:C104`, `E38:F38`, `A14:C14`, `F155:H155`, `E40:F40`, `E14:H14`, `A289:C289`, `A40:C40`, `E139:G139`, `E26:F26`, `B187:F187`, `A82:C82`, `B63:H64`, `E16:F16`, `E131:G131`, `E104:H104`, `E58:F58`, `E189:F189`, `E18:F18`, `B67:G67`, `E141:F141`, `E135:F135`, `I68:K68`, `E44:F44`, `A258:G258`, `E20:F20`, `B42:C42`, `E69:F69`, `B80:G80`, `B119:H120`, `B44:C44`, `E77:F77`, `E133:F133`, `B183:H184`, `A30:C30`, `E94:H94`, `B229:H229`, `E57:F57`, `E32:F32`, `B155:D155`, `E6:H6`, `E46:H46`, `B123:F123`, `E96:F96`, `E56:F56`, `B233:C233`, `E24:F24`, `E195:F195`, `E98:F98`, `E42:F42`, `B2:H3`, `D233:E233`, `F233:G233`, `B127:D127`, `E28:F28`, `A61:G61`, `E30:F30`, `B129:D129`, `A94:C94`, `B36:C36`, `E47:F47`

Filas vacías:

1, 3, 4, 5, 7, 9, 11, 12, 13, 15, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 41, 43, 45, 59, 60, 62, 64, 65, 66, 78, 79, 81, 92, 93, 99, 101, 103, 109, 111, 113, 114, 115, 116, 118, 120, 121, 122, 124, 126, 128, 130, 132, 134, 136, 138, 140, 153, 158, 160, 162, 164, 166, 168, 170, 172, 174, 176, 177, 178, 179, 180, 182, 184, 185, 186, 188, 190, 192, 194, 196, 198, 200, 202, 205, 207, 209, 212, 214, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 228, 230, 231, 277, 288, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 322, 324, 325, 326, 385, 386, 387

### QF-545H

- Estado: `visible`.
- Dimensión openpyxl: `A1:S382` (382 filas × 19 columnas, A–S).
- Celdas no vacías en la vista de fórmulas (valor no nulo): 1219.
- De esas celdas: fórmulas 240; constantes 979 (numéricas 506, texto 471, fechas-tipo en la constante 2).
- Fórmulas con caché nulo: 0. Fórmulas cuyo caché es el mismo texto de la fórmula: 0.
- Celdas combinadas: 80.
- Tablas: ninguna. Nombres definidos: ninguno a nivel de libro.
- Filas vacías dentro de 1..382: 125.
- Columnas vacías dentro de A..S: P.
- Filas ocultas: ninguna. Columnas ocultas: ninguna.
- Vista: `pageBreakPreview`, zoom `110`. Paneles congelados: `None`. Títulos de impresión: filas `None`, columnas `None`.
- Formato condicional (reglas): 0. Validaciones: 0. Comentarios: 0. Imágenes: 1. Gráficos: 6.
- Errores de Excel en fórmula o en caché: 0.

Títulos largos o de sección localizados (coordenada y texto):

- `B2`: `Análisis de Comportamiento de un Sistema ESP`
- `A13`: `Información Mecánica del Pozo`
- `E13`: `Información de Producción y Fluido`
- `E17`: `Presión de Yacimiento`
- `E19`: `Presión de Burbuja`
- `E27`: `Temperatura de fondo`
- `A29`: `Tuberia de Producción`
- `E29`: `Temperatura de fondo`
- `E35`: `Información de Cable Instalado`
- `A39`: `Información de Bomba Instalada`
- `E45`: `Curva de Performance de Bomba`
- `E56`: `Cono de eficiencia`
- `B61`: `Análisis de Comportamiento de un Sistema ESP`
- `B65`: `Condiciones de Operación Actuales`
- `E69`: `Corriente de Motor`
- `E71`: `Factor de Potencia`
- `E73`: `Eficiencia del motor`
- `A75`: `Vibración del Motor`
- `E75`: `Temperatura de Motor`
- `B78`: `Curva de la Bomba Según Velocidad Actual`
- `A80`: `Curva de Performance de Bomba`
- `A92`: `Cálculo de Gradiente de Presión`
- `E92`: `Cálculo de la THD TOTAL`
- `A94`: `Gravedad Oil @ 60ºF`
- `A96`: `Gravedad Oil @ T fondo`
- `A98`: `Densidad de Fluido`
- `E98`: `Perdidad por Fricción`
- `A100`: `Gradiente de Presión`
- `A102`: `Cálculo de Producción y consumo`
- `E102`: `Difrencia entre calculos y medición`
- `A106`: `Potencia a consumir`
- `A108`: `Potencia Transferida`
- `A110`: `Eficiencia de la bomba`
- `B115`: `Análisis de Comportamiento de un Sistema ESP`
- `B119`: `Cálculo de Consumo Energetico`
- `B121`: `Consumo de Potencia Bomba`
- `B123`: `Consumo de Potencia Sello`
- `B125`: `Potencia a entregar por el motor`
- `E127`: `Datos de operación del Motor`
- `E129`: `Porcentaje de carga`
- `E135`: `Caida de Voltaje en el Cable`
- `E137`: `Voltaje @ 1000 ft (V)`
- `B151`: `Información del SUT`
- `B177`: `Análisis de Comportamiento de un Sistema ESP`
- `B181`: `Analisis de Data Simulada Vs Medida`
- `E183`: `Fecha Prueba de Pozo`
- `B222`: `Análisis de Comportamiento de un Sistema ESP`
- `B226`: `Actividad de Revisión Equipos 10/08/2017`
- `A233`: `Temperatura de Fluido`
- `A283`: `Perdida de Energia`
- `B309`: `Análisis de Comportamiento de un Sistema ESP`

Fechas con tipo fecha, o fórmula cuya caché es fecha:

- `B6`: fórmula/constante `=TODAY()`; caché `2026-10-17`.
- `G183`: fórmula/constante `2017-08-06`; caché `2017-08-06`.
- `G189`: fórmula/constante `2017-08-01`; caché `2017-08-01`.

Textos que contienen una secuencia `dd/mm/aaaa` o similar:

- `B226`: `Actividad de Revisión Equipos 10/08/2017` (fragmentos ['10/08/2017']).

Gráficos (ancla = celda aproximada de la esquina superior; referencias de serie tal como las expone openpyxl):

- Gráfico 1: tipo `ScatterChart`, ancla `D79`.
  - Serie 1: title=`Head (ft)`, val=`None`, cat=`None`, xVal=`'QF-545H'!$A$84:$A$89`, yVal=`'QF-545H'!$B$84:$B$89`.
  - Serie 2: title=`Operación Real`, val=`None`, cat=`None`, xVal=`'QF-545H'!$B$69`, yVal=`'QF-545H'!$G$100`.
  - Serie 3: title=`Operación Ideal`, val=`None`, cat=`None`, xVal=`'QF-545H'!$B$104`, yVal=`'QF-545H'!$G$100`.
  - Serie 4: title=`'QF-545H'!$I$81`, val=`None`, cat=`None`, xVal=`'QF-545H'!$J$83:$J$88`, yVal=`'QF-545H'!$K$83:$K$88`.
  - Serie 5: title=`'QF-545H'!$M$81`, val=`None`, cat=`None`, xVal=`'QF-545H'!$N$83:$N$88`, yVal=`'QF-545H'!$O$83:$O$88`.
  - Serie 6: title=`'QF-545H'!$Q$81`, val=`None`, cat=`None`, xVal=`'QF-545H'!$R$83:$R$88`, yVal=`'QF-545H'!$S$83:$S$88`.
  - Serie 7: title=`Menos etapas`, val=`None`, cat=`None`, xVal=`'QF-545H'!$I$70:$I$75`, yVal=`'QF-545H'!$J$70:$J$75`.
- Gráfico 2: tipo `ScatterChart`, ancla `F313`.
  - Serie 1: title=`None`, val=`None`, cat=`None`, xVal=`'QF-545H'!$A$315:$A$370`, yVal=`'QF-545H'!$D$315:$D$370`.
- Gráfico 3: tipo `ScatterChart`, ancla `F346`.
  - Serie 1: title=`None`, val=`None`, cat=`None`, xVal=`'QF-545H'!$E$315:$E$370`, yVal=`'QF-545H'!$A$315:$A$370`.
  - Serie 2: title=`Bomba`, val=`None`, cat=`None`, xVal=`'QF-545H'!$G$343:$G$344`, yVal=`'QF-545H'!$H$343:$H$344`.
- Gráfico 4: tipo `ScatterChart`, ancla `A139`.
  - Serie 1: title=`1 AWG`, val=`None`, cat=`None`, xVal=`'QF-545H'!$J$138:$J$148`, yVal=`'QF-545H'!$K$138:$K$148`.
  - Serie 2: title=`2 AWG`, val=`None`, cat=`None`, xVal=`'QF-545H'!$J$138:$J$148`, yVal=`'QF-545H'!$L$138:$L$148`.
  - Serie 3: title=`'QF-545H'!$N$137`, val=`None`, cat=`None`, xVal=`'QF-545H'!$J$138:$J$148`, yVal=`'QF-545H'!$N$138:$N$148`.
  - Serie 4: title=`Punto de operación`, val=`None`, cat=`None`, xVal=`'QF-545H'!$G$75`, yVal=`'QF-545H'!$G$69`.
- Gráfico 5: tipo `ScatterChart`, ancla `E139`.
  - Serie 1: title=`1 AWG`, val=`None`, cat=`None`, xVal=`'QF-545H'!$J$151:$J$152`, yVal=`'QF-545H'!$K$151:$K$152`.
  - Serie 2: title=`2 AWG`, val=`None`, cat=`None`, xVal=`'QF-545H'!$L$151:$L$152`, yVal=`'QF-545H'!$M$151:$M$152`.
  - Serie 3: title=`4 AWG`, val=`None`, cat=`None`, xVal=`'QF-545H'!$N$151:$N$152`, yVal=`'QF-545H'!$O$151:$O$152`.
  - Serie 4: title=`None`, val=`None`, cat=`None`, xVal=`'QF-545H'!$G$131`, yVal=`'QF-545H'!$G$137`.
- Gráfico 6: tipo `ScatterChart`, ancla `A46`.
  - Serie 1: title=`Head (ft)`, val=`None`, cat=`None`, xVal=`'QF-554H'!$E$50:$E$55`, yVal=`'QF-554H'!$F$50:$F$55`.
  - Serie 2: title=`None`, val=`None`, cat=`None`, xVal=`'QF-554H'!$I$56:$I$57`, yVal=`'QF-554H'!$J$56:$J$57`.
  - Serie 3: title=`None`, val=`None`, cat=`None`, xVal=`'QF-554H'!$K$56:$K$57`, yVal=`'QF-554H'!$L$56:$L$57`.
  - Serie 4: title=`None`, val=`None`, cat=`None`, xVal=`'QF-554H'!$M$56:$M$57`, yVal=`'QF-554H'!$N$56:$N$57`.

Bloque numérico inferior (`Measured`):

- Bloque con encabezado en fila 313: A=Measured, B=Incl. (deg), C=Azim. (deg), D=Vertical, E=Dogleg.
- Fila siguiente: A=Depth (ft), D=Depth(ft), E=(º/100ft).
- Filas con valor numérico en la columna A dentro de ese bloque: 68.
- Columna A (etiqueta de encabezado Measured / Depth (ft)): n=68, min=0, max=4576, p05=449.05, mediana=2339.5, p95=4339.95.
- Diferencias entre filas consecutivas de A: n=67, min=60, mediana=63, max=300, p05=61, p95=80.4.
- La columna A de este bloque es estrictamente creciente entre filas consecutivas con número.
- Criterio de espaciamiento irregular: diferencia consecutiva ≤ 0, o mayor que 3× la mediana (63), o positiva y menor que la mediana/3. Pasos que cumplen el criterio: 1 de 67.
- Ejemplos: fila 316 Δ=300.
- Columna B (texto de encabezado Incl. (deg), fila de unidades/subtítulo —): constantes=68, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=68.
  Descriptivo: min=0, p05=2.5765, Q1=12.7175, mediana=46.425, Q3=73.36, p95=90.2045, max=91.5.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-78.2463, 164.324] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
  Diferencia absoluta consecutiva: min=0.03, mediana=1.42, max=3.05. Pasos con |Δ|>180: 0.
- Columna C (texto de encabezado Azim. (deg), fila de unidades/subtítulo —): constantes=68, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=68.
  Descriptivo: min=0, p05=223.846, Q1=227.13, mediana=229.355, Q3=248.285, p95=332.637, max=344.11.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [195.397, 280.017] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 17.
  Ejemplos: C315=0; C316=55.06; C317=5.12; C318=344.11; C319=342.55; C320=336.57; C321=322.16; C322=321.12; y 9 más.
  Diferencia absoluta consecutiva: min=0.01, mediana=0.86, max=338.99. Pasos con |Δ|>180: 1.
  Esos pasos: filas 317->318: 5.12 a 344.11 (Δ=338.99).
- Columna D (texto de encabezado Vertical, fila de unidades/subtítulo Depth(ft)): constantes=68, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=68.
  Descriptivo: min=0, p05=448.976, Q1=1288.27, mediana=2189.26, Q3=2675.52, p95=2764.19, max=2764.71.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-792.598, 4756.38] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
- Columna E (texto de encabezado Dogleg, fila de unidades/subtítulo (º/100ft)): constantes=68, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=68.
  Descriptivo: min=0, p05=0.4605, Q1=1.64, mediana=2.615, Q3=3.8475, p95=4.839, max=4.98.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-1.67125, 7.15875] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
- No hay valores repetidos en la columna A de este bloque.
- No hay filas duplicadas por tupla cacheada A–E en este bloque.

Puntos de la curva con encabezados `Caudal` / `Head` / `Brake` / `EFF`:

- Fila 47: E=Caudal, F=Head, G=Brake, H=EFF.
- Fila 48: E=BFPD, F=ft, G=HP, H=%.
- Filas de puntos con E numérico constante: 6 (filas [49, 50, 51, 52, 53, 54]).
- Puntos (fila, E, F, G, H): 49: 0, 64, 2.5, 0; 50: 2500, 62, 2.6, 4.6; 51: 5000, 58, 2.6, 6.6; 52: 8000, 48, 3, 7.6; 53: 10000, 36, 3.2, 7; 54: 12500, 10, 3.5, 2.4.
- La secuencia de la columna E en esos puntos es estrictamente creciente.
- La secuencia de la columna F en esos puntos es no creciente.
- Fila 55: E=`Limite minimo`, G=2500 (fórmula=False), H=BFPD, caché G=2500.
- Fila 56: E=`Cono de eficiencia`, G=8000 (fórmula=False), H=BFPD, caché G=8000.
- Fila 57: E=`Limite maximo`, G=10000 (fórmula=False), H=BFPD, caché G=10000.

Textos de la columna A que aparecen más de una vez en la misma hoja (etiqueta repetida, no una columna duplicada de una tabla):

- `Caudal`: 4 veces (filas 69, 82, 185, 232).
- `Promedio`: 4 veces (filas 256, 260, 272, 276).
- `Velocidad`: 3 veces (filas 67, 81, 228).
- `Potencia`: 3 veces (filas 195, 202, 209).
- `I Promedio`: 3 veces (filas 250, 264, 280).
- `Potencia KVA`: 3 veces (filas 251, 265, 281).
- `THP`: 2 veces (filas 73, 235).
- `Voltaje entrada`: 2 veces (filas 193, 200).
- `U-V`: 2 veces (filas 253, 269).
- `V-W`: 2 veces (filas 254, 270).
- `U-W`: 2 veces (filas 255, 271).
- `U-N`: 2 veces (filas 257, 273).
- `V-N`: 2 veces (filas 258, 274).
- `W-N`: 2 veces (filas 259, 275).
- `I(U)`: 2 veces (filas 261, 277).
- `I(V)`: 2 veces (filas 262, 278).
- `I(W)`: 2 veces (filas 263, 279).

Rangos combinados:

`A80:C80`, `E129:F129`, `E71:F71`, `E23:F23`, `E73:F73`, `E131:F131`, `B65:G65`, `E137:F137`, `A59:G59`, `B177:H178`, `B313:B314`, `E8:H8`, `G108:H108`, `E27:F27`, `B127:C127`, `E10:H10`, `B309:H310`, `B125:D125`, `E100:F100`, `E183:F183`, `E135:G135`, `E75:F75`, `B41:C41`, `B35:C35`, `E45:H45`, `E55:F55`, `E67:F67`, `B61:H62`, `B78:G78`, `E102:H102`, `B226:G226`, `A29:C29`, `A13:C13`, `F151:H151`, `E25:F25`, `B222:H223`, `E189:F189`, `B115:H116`, `I66:K66`, `F227:G227`, `E39:F39`, `B43:C43`, `E29:F29`, `E94:F94`, `A266:G266`, `E69:F69`, `B181:F181`, `E31:F31`, `E92:H92`, `E133:F133`, `E15:F15`, `E46:F46`, `B123:D123`, `A252:G252`, `E13:H13`, `E57:F57`, `E127:G127`, `A238:G238`, `E41:F41`, `E6:H6`, `E96:F96`, `E56:F56`, `E43:F43`, `B151:D151`, `B227:C227`, `E33:F33`, `E98:F98`, `B2:H3`, `E17:F17`, `E19:F19`, `B119:F119`, `A102:C102`, `E35:H35`, `D227:E227`, `A92:C92`, `A39:C39`, `B121:D121`, `E37:F37`, `C313:C314`, `E21:F21`

Filas vacías:

1, 3, 4, 5, 7, 9, 11, 12, 14, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 40, 42, 44, 58, 60, 62, 63, 64, 76, 77, 79, 90, 91, 97, 99, 101, 107, 109, 111, 112, 114, 116, 117, 118, 120, 122, 124, 126, 128, 130, 132, 134, 136, 149, 154, 156, 158, 160, 162, 164, 166, 168, 170, 172, 173, 174, 176, 178, 179, 180, 182, 184, 186, 188, 190, 192, 194, 196, 199, 201, 203, 206, 208, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 221, 223, 224, 225, 267, 282, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 308, 310, 311, 312

### QF-500H

- Estado: `visible`.
- Dimensión openpyxl: `A1:S357` (357 filas × 19 columnas, A–S).
- Celdas no vacías en la vista de fórmulas (valor no nulo): 1291.
- De esas celdas: fórmulas 260; constantes 1031 (numéricas 564, texto 465, fechas-tipo en la constante 2).
- Fórmulas con caché nulo: 0. Fórmulas cuyo caché es el mismo texto de la fórmula: 0.
- Celdas combinadas: 80.
- Tablas: ninguna. Nombres definidos: ninguno a nivel de libro.
- Filas vacías dentro de 1..357: 103.
- Columnas vacías dentro de A..S: P.
- Filas ocultas: ninguna. Columnas ocultas: ninguna.
- Vista: `pageBreakPreview`, zoom `None`. Paneles congelados: `None`. Títulos de impresión: filas `None`, columnas `None`.
- Formato condicional (reglas): 0. Validaciones: 0. Comentarios: 0. Imágenes: 1. Gráficos: 6.
- Errores de Excel en fórmula o en caché: 0.

Títulos largos o de sección localizados (coordenada y texto):

- `B2`: `Análisis de Comportamiento de un Sistema ESP`
- `A13`: `Información Mecánica del Pozo`
- `E13`: `Información de Producción y Fluido`
- `E17`: `Presión de Yacimiento`
- `E19`: `Presión de Burbuja`
- `E27`: `Temperatura de fondo`
- `A29`: `Tuberia de Producción`
- `E29`: `Temperatura de fondo`
- `E35`: `Información de Cable Instalado`
- `A39`: `Información de Bomba Instalada`
- `E45`: `Curva de Performance de Bomba`
- `E56`: `Cono de eficiencia`
- `B62`: `Análisis de Comportamiento de un Sistema ESP`
- `B66`: `Condiciones de Operación Actuales`
- `E70`: `Corriente de Motor`
- `E72`: `Factor de Potencia`
- `E74`: `Eficiencia del motor`
- `A76`: `Vibración del Motor`
- `E76`: `Temperatura de Motor`
- `B79`: `Curva de la Bomba Según Velocidad Actual`
- `A81`: `Curva de Performance de Bomba`
- `A93`: `Cálculo de Gradiente de Presión`
- `E93`: `Cálculo de la THD TOTAL`
- `A95`: `Gravedad Oil @ 60ºF`
- `A97`: `Gravedad Oil @ T fondo`
- `A99`: `Densidad de Fluido`
- `E99`: `Perdidad por Fricción`
- `A101`: `Gradiente de Presión`
- `A103`: `Cálculo de Producción y consumo`
- `E103`: `Difrencia entre calculos y medición`
- `A107`: `Potencia a consumir`
- `A109`: `Potencia Transferida`
- `A111`: `Eficiencia de la bomba`
- `B115`: `Análisis de Comportamiento de un Sistema ESP`
- `B119`: `Cálculo de Consumo Energetico`
- `B121`: `Consumo de Potencia Bomba`
- `B123`: `Consumo de Potencia Sello`
- `B125`: `Potencia a entregar por el motor`
- `E127`: `Datos de operación del Motor`
- `E129`: `Porcentaje de carga`
- `E135`: `Caida de Voltaje en el Cable`
- `E137`: `Voltaje @ 1000 ft (V)`
- `B151`: `Información del SUT`
- `B175`: `Análisis de Comportamiento de un Sistema ESP`
- `B179`: `Analisis de Data Simulada Vs Medida`
- `E181`: `Fecha Prueba de Pozo`
- `B219`: `Análisis de Comportamiento de un Sistema ESP`
- `B223`: `Actividad de Revisión Equipos 10/08/2017`
- `A230`: `Temperatura de Fluido`
- `A278`: `Perdida de Energia`
- `B281`: `Análisis de Comportamiento de un Sistema ESP`

Fechas con tipo fecha, o fórmula cuya caché es fecha:

- `B6`: fórmula/constante `=TODAY()`; caché `2026-10-17`.
- `G181`: fórmula/constante `2017-08-07`; caché `2017-08-07`.
- `G187`: fórmula/constante `2017-08-01`; caché `2017-08-01`.

Textos que contienen una secuencia `dd/mm/aaaa` o similar:

- `B223`: `Actividad de Revisión Equipos 10/08/2017` (fragmentos ['10/08/2017']).

Gráficos (ancla = celda aproximada de la esquina superior; referencias de serie tal como las expone openpyxl):

- Gráfico 1: tipo `ScatterChart`, ancla `D80`.
  - Serie 1: title=`Head (ft)`, val=`None`, cat=`None`, xVal=`'QF-500H'!$A$85:$A$90`, yVal=`'QF-500H'!$B$85:$B$90`.
  - Serie 2: title=`Operación Real`, val=`None`, cat=`None`, xVal=`'QF-500H'!$B$70`, yVal=`'QF-500H'!$G$101`.
  - Serie 3: title=`Operación Ideal`, val=`None`, cat=`None`, xVal=`'QF-500H'!$B$105`, yVal=`'QF-500H'!$G$101`.
  - Serie 4: title=`'QF-500H'!$I$82`, val=`None`, cat=`None`, xVal=`'QF-500H'!$J$84:$J$89`, yVal=`'QF-500H'!$K$84:$K$89`.
  - Serie 5: title=`'QF-500H'!$M$82`, val=`None`, cat=`None`, xVal=`'QF-500H'!$N$84:$N$89`, yVal=`'QF-500H'!$O$84:$O$89`.
  - Serie 6: title=`'QF-500H'!$Q$82`, val=`None`, cat=`None`, xVal=`'QF-500H'!$R$84:$R$89`, yVal=`'QF-500H'!$S$84:$S$89`.
  - Serie 7: title=`Menos etapas`, val=`None`, cat=`None`, xVal=`'QF-500H'!$I$71:$I$76`, yVal=`'QF-500H'!$J$71:$J$76`.
- Gráfico 2: tipo `ScatterChart`, ancla `F285`.
  - Serie 1: title=`None`, val=`None`, cat=`None`, xVal=`'QF-500H'!$A$287:$A$342`, yVal=`'QF-500H'!$D$287:$D$342`.
- Gráfico 3: tipo `ScatterChart`, ancla `F316`.
  - Serie 1: title=`None`, val=`None`, cat=`None`, xVal=`'QF-500H'!$E$287:$E$342`, yVal=`'QF-500H'!$A$287:$A$342`.
  - Serie 2: title=`Bomba`, val=`None`, cat=`None`, xVal=`'QF-500H'!$G$315:$G$316`, yVal=`'QF-500H'!$H$315:$H$316`.
- Gráfico 4: tipo `ScatterChart`, ancla `A139`.
  - Serie 1: title=`1 AWG`, val=`None`, cat=`None`, xVal=`'QF-500H'!$J$138:$J$148`, yVal=`'QF-500H'!$K$138:$K$148`.
  - Serie 2: title=`2 AWG`, val=`None`, cat=`None`, xVal=`'QF-500H'!$J$138:$J$148`, yVal=`'QF-500H'!$L$138:$L$148`.
  - Serie 3: title=`'QF-500H'!$N$137`, val=`None`, cat=`None`, xVal=`'QF-500H'!$J$138:$J$148`, yVal=`'QF-500H'!$N$138:$N$148`.
  - Serie 4: title=`Punto de operación`, val=`None`, cat=`None`, xVal=`'QF-500H'!$G$76`, yVal=`'QF-500H'!$G$70`.
- Gráfico 5: tipo `ScatterChart`, ancla `E139`.
  - Serie 1: title=`1 AWG`, val=`None`, cat=`None`, xVal=`'QF-500H'!$J$151:$J$152`, yVal=`'QF-500H'!$K$151:$K$152`.
  - Serie 2: title=`2 AWG`, val=`None`, cat=`None`, xVal=`'QF-500H'!$L$151:$L$152`, yVal=`'QF-500H'!$M$151:$M$152`.
  - Serie 3: title=`4 AWG`, val=`None`, cat=`None`, xVal=`'QF-500H'!$N$151:$N$152`, yVal=`'QF-500H'!$O$151:$O$152`.
  - Serie 4: title=`None`, val=`None`, cat=`None`, xVal=`'QF-500H'!$G$131`, yVal=`'QF-500H'!$G$137`.
- Gráfico 6: tipo `ScatterChart`, ancla `A46`.
  - Serie 1: title=`Head (ft)`, val=`None`, cat=`None`, xVal=`'QF-554H'!$E$50:$E$55`, yVal=`'QF-554H'!$F$50:$F$55`.
  - Serie 2: title=`None`, val=`None`, cat=`None`, xVal=`'QF-554H'!$I$56:$I$57`, yVal=`'QF-554H'!$J$56:$J$57`.
  - Serie 3: title=`None`, val=`None`, cat=`None`, xVal=`'QF-554H'!$K$56:$K$57`, yVal=`'QF-554H'!$L$56:$L$57`.
  - Serie 4: title=`None`, val=`None`, cat=`None`, xVal=`'QF-554H'!$M$56:$M$57`, yVal=`'QF-554H'!$N$56:$N$57`.

Bloque numérico inferior (`Measured`):

- Bloque con encabezado en fila 285: A=Measured, B=Incl. (deg), C=Azim. (deg), D=Vertical, E=Dogleg.
- Fila siguiente: A=Depth (ft), D=Depth(ft), E=(º/100ft).
- Filas con valor numérico en la columna A dentro de ese bloque: 71.
- Columna A (etiqueta de encabezado Measured / Depth (ft)): n=71, min=0, max=4637, p05=425.5, mediana=2380, p95=4393.5.
- Diferencias entre filas consecutivas de A: n=70, min=30, mediana=63, max=267, p05=60.45, p95=64.
- La columna A de este bloque es estrictamente creciente entre filas consecutivas con número.
- Criterio de espaciamiento irregular: diferencia consecutiva ≤ 0, o mayor que 3× la mediana (63), o positiva y menor que la mediana/3. Pasos que cumplen el criterio: 1 de 70.
- Ejemplos: fila 288 Δ=267.
- Columna B (texto de encabezado Incl. (deg), fila de unidades/subtítulo —): constantes=71, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=71.
  Descriptivo: min=0, p05=1.76, Q1=9.72, mediana=39.34, Q3=85.46, p95=90.71, max=90.8.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-103.89, 199.07] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
  Diferencia absoluta consecutiva: min=0.01, mediana=1.15, max=3.87. Pasos con |Δ|>180: 0.
- Columna C (texto de encabezado Azim. (deg), fila de unidades/subtítulo —): constantes=71, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=71.
  Descriptivo: min=0, p05=278.285, Q1=280.525, mediana=282.35, Q3=285.93, p95=292.61, max=327.24.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [272.417, 294.038] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 6.
  Ejemplos: C287=0; C288=86.85; C289=57.21; C290=327.24; C291=311.47; C292=296.58.
  Diferencia absoluta consecutiva: min=0.01, mediana=0.73, max=270.03. Pasos con |Δ|>180: 1.
  Esos pasos: filas 289->290: 57.21 a 327.24 (Δ=270.03).
- Columna D (texto de encabezado Vertical, fila de unidades/subtítulo Depth(ft)): constantes=71, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=71.
  Descriptivo: min=0, p05=425.475, Q1=1301.38, mediana=2304.17, Q3=2799.42, p95=2827.4, max=2828.85.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-945.693, 5046.49] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
- Columna E (texto de encabezado Dogleg, fila de unidades/subtítulo (º/100ft)): constantes=71, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=71.
  Descriptivo: min=0, p05=0.125, Q1=0.855, mediana=1.96, Q3=4.805, p95=5.93, max=6.44.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-5.07, 10.73] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
- No hay valores repetidos en la columna A de este bloque.
- No hay filas duplicadas por tupla cacheada A–E en este bloque.

Puntos de la curva con encabezados `Caudal` / `Head` / `Brake` / `EFF`:

- Fila 47: E=Caudal, F=Head, G=Brake, H=EFF.
- Fila 48: E=BFPD, F=ft, G=HP, H=%.
- Filas de puntos con E numérico constante: 6 (filas [49, 50, 51, 52, 53, 54]).
- Puntos (fila, E, F, G, H): 49: 0, 64, 2.5, 0; 50: 2500, 62, 2.6, 4.6; 51: 5000, 58, 2.6, 6.6; 52: 8000, 48, 3, 7.6; 53: 10000, 36, 3.2, 7; 54: 12500, 10, 3.5, 2.4.
- La secuencia de la columna E en esos puntos es estrictamente creciente.
- La secuencia de la columna F en esos puntos es no creciente.
- Fila 55: E=`Limite minimo`, G=2500 (fórmula=False), H=BFPD, caché G=2500.
- Fila 56: E=`Cono de eficiencia`, G=8000 (fórmula=False), H=BFPD, caché G=8000.
- Fila 57: E=`Limite maximo`, G=10000 (fórmula=False), H=BFPD, caché G=10000.

Textos de la columna A que aparecen más de una vez en la misma hoja (etiqueta repetida, no una columna duplicada de una tabla):

- `Caudal`: 4 veces (filas 70, 83, 183, 229).
- `Promedio`: 4 veces (filas 253, 257, 267, 271).
- `Velocidad`: 3 veces (filas 68, 82, 225).
- `Potencia`: 3 veces (filas 193, 200, 207).
- `I Promedio`: 3 veces (filas 247, 261, 275).
- `Potencia KVA`: 3 veces (filas 248, 262, 276).
- `THP`: 2 veces (filas 74, 232).
- `Voltaje entrada`: 2 veces (filas 191, 198).
- `U-V`: 2 veces (filas 250, 264).
- `V-W`: 2 veces (filas 251, 265).
- `U-W`: 2 veces (filas 252, 266).
- `U-N`: 2 veces (filas 254, 268).
- `V-N`: 2 veces (filas 255, 269).
- `W-N`: 2 veces (filas 256, 270).
- `I(U)`: 2 veces (filas 258, 272).
- `I(V)`: 2 veces (filas 259, 273).
- `I(W)`: 2 veces (filas 260, 274).

Rangos combinados:

`C6:D6`, `B62:H63`, `E129:F129`, `E23:F23`, `E181:F181`, `E131:F131`, `B175:H176`, `E137:F137`, `B179:F179`, `E99:F99`, `F224:G224`, `E8:H8`, `A93:C93`, `E27:F27`, `B127:C127`, `E101:F101`, `E10:H10`, `B125:D125`, `E135:G135`, `B41:C41`, `B35:C35`, `E45:H45`, `E55:F55`, `B219:H220`, `E93:H93`, `A29:C29`, `A81:C81`, `A13:C13`, `F151:H151`, `E187:F187`, `E76:F76`, `B66:G66`, `E25:F25`, `A235:G235`, `B224:C224`, `B115:H116`, `E68:F68`, `E39:F39`, `B43:C43`, `E29:F29`, `I67:K67`, `E31:F31`, `E133:F133`, `E15:F15`, `E46:F46`, `B123:D123`, `E95:F95`, `B79:G79`, `E103:H103`, `E70:F70`, `E13:H13`, `E57:F57`, `B281:H282`, `E127:G127`, `E72:F72`, `E41:F41`, `E6:H6`, `B223:G223`, `E56:F56`, `E43:F43`, `C285:C286`, `B151:D151`, `A263:G263`, `E33:F33`, `B2:H3`, `E17:F17`, `A249:G249`, `E19:F19`, `E74:F74`, `B119:F119`, `E35:H35`, `D224:E224`, `A39:C39`, `B285:B286`, `B121:D121`, `G109:H109`, `A103:C103`, `E37:F37`, `E97:F97`, `E21:F21`

Filas vacías:

1, 3, 4, 5, 7, 9, 11, 12, 14, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 40, 42, 44, 58, 59, 60, 61, 63, 64, 65, 77, 78, 80, 91, 92, 98, 100, 102, 108, 110, 112, 113, 114, 116, 117, 118, 120, 122, 124, 126, 128, 130, 132, 134, 136, 149, 154, 156, 158, 160, 162, 164, 166, 168, 170, 172, 173, 174, 176, 177, 178, 180, 182, 184, 186, 188, 190, 192, 194, 197, 199, 201, 204, 206, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 220, 221, 222, 277, 279, 280, 282, 283, 284

### QF-378HST

- Estado: `visible`.
- Dimensión openpyxl: `A1:S343` (343 filas × 19 columnas, A–S).
- Celdas no vacías en la vista de fórmulas (valor no nulo): 1230.
- De esas celdas: fórmulas 263; constantes 967 (numéricas 499, texto 466, fechas-tipo en la constante 2).
- Fórmulas con caché nulo: 0. Fórmulas cuyo caché es el mismo texto de la fórmula: 0.
- Celdas combinadas: 79.
- Tablas: ninguna. Nombres definidos: ninguno a nivel de libro.
- Filas vacías dentro de 1..343: 101.
- Columnas vacías dentro de A..S: P.
- Filas ocultas: ninguna. Columnas ocultas: ninguna.
- Vista: `pageBreakPreview`, zoom `90`. Paneles congelados: `None`. Títulos de impresión: filas `None`, columnas `None`.
- Formato condicional (reglas): 0. Validaciones: 0. Comentarios: 0. Imágenes: 1. Gráficos: 6.
- Errores de Excel en fórmula o en caché: 0.

Títulos largos o de sección localizados (coordenada y texto):

- `B2`: `Análisis de Comportamiento de un Sistema ESP`
- `A13`: `Información Mecánica del Pozo`
- `E13`: `Información de Producción y Fluido`
- `E17`: `Presión de Yacimiento`
- `E19`: `Presión de Burbuja`
- `E27`: `Temperatura de fondo`
- `A29`: `Tuberia de Producción`
- `E29`: `Temperatura de fondo`
- `E35`: `Información de Cable Instalado`
- `A39`: `Información de Bomba Instalada`
- `E45`: `Curva de Performance de Bomba`
- `E56`: `Cono de eficiencia`
- `B60`: `Análisis de Comportamiento de un Sistema ESP`
- `B64`: `Condiciones de Operación Actuales`
- `E68`: `Corriente de Motor`
- `E70`: `Factor de Potencia`
- `E72`: `Eficiencia del motor`
- `A74`: `Vibración del Motor`
- `E74`: `Temperatura de Motor`
- `B77`: `Curva de la Bomba Según Velocidad Actual`
- `A79`: `Curva de Performance de Bomba`
- `A91`: `Cálculo de Gradiente de Presión`
- `E91`: `Cálculo de la THD TOTAL`
- `A93`: `Gravedad Oil @ 60ºF`
- `A95`: `Gravedad Oil @ T fondo`
- `A97`: `Densidad de Fluido`
- `E97`: `Perdidad por Fricción`
- `A99`: `Gradiente de Presión`
- `A101`: `Cálculo de Producción y consumo`
- `E101`: `Difrencia entre calculos y medición`
- `A105`: `Potencia a consumir`
- `A107`: `Potencia Transferida`
- `A109`: `Eficiencia de la bomba`
- `B113`: `Análisis de Comportamiento de un Sistema ESP`
- `B117`: `Cálculo de Consumo Energetico`
- `B119`: `Consumo de Potencia Bomba`
- `B121`: `Consumo de Potencia Sello`
- `B123`: `Potencia a entregar por el motor`
- `E125`: `Datos de operación del Motor`
- `E127`: `Porcentaje de carga`
- `E133`: `Caida de Voltaje en el Cable`
- `E135`: `Voltaje @ 1000 ft (V)`
- `B149`: `Información del SUT`
- `B173`: `Análisis de Comportamiento de un Sistema ESP`
- `B177`: `Analisis de Data Simulada Vs Medida`
- `E179`: `Fecha Prueba de Pozo`
- `B217`: `Análisis de Comportamiento de un Sistema ESP`
- `B221`: `Actividad de Revisión Equipos 10/08/2017`
- `A228`: `Temperatura de Fluido`
- `A276`: `Perdida de Energia`
- `B279`: `Análisis de Comportamiento de un Sistema ESP`

Fechas con tipo fecha, o fórmula cuya caché es fecha:

- `B6`: fórmula/constante `=TODAY()`; caché `2026-10-17`.
- `G179`: fórmula/constante `2017-08-07`; caché `2017-08-07`.
- `G185`: fórmula/constante `2017-08-01`; caché `2017-08-01`.

Textos que contienen una secuencia `dd/mm/aaaa` o similar:

- `B221`: `Actividad de Revisión Equipos 10/08/2017` (fragmentos ['10/08/2017']).

Gráficos (ancla = celda aproximada de la esquina superior; referencias de serie tal como las expone openpyxl):

- Gráfico 1: tipo `ScatterChart`, ancla `A46`.
  - Serie 1: title=`Head (ft)`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$E$49:$E$54`, yVal=`'QF-378HST'!$F$49:$F$54`.
- Gráfico 2: tipo `ScatterChart`, ancla `D78`.
  - Serie 1: title=`Head (ft)`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$A$83:$A$88`, yVal=`'QF-378HST'!$B$83:$B$88`.
  - Serie 2: title=`Operación Real`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$B$68`, yVal=`'QF-378HST'!$G$99`.
  - Serie 3: title=`Operación Ideal`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$B$103`, yVal=`'QF-378HST'!$G$99`.
  - Serie 4: title=`'QF-378HST'!$I$80`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$J$82:$J$87`, yVal=`'QF-378HST'!$K$82:$K$87`.
  - Serie 5: title=`'QF-378HST'!$M$80`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$N$82:$N$87`, yVal=`'QF-378HST'!$O$82:$O$87`.
  - Serie 6: title=`'QF-378HST'!$Q$80`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$R$82:$R$87`, yVal=`'QF-378HST'!$S$82:$S$87`.
  - Serie 7: title=`Menos etapas`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$I$69:$I$74`, yVal=`'QF-378HST'!$J$69:$J$74`.
- Gráfico 3: tipo `ScatterChart`, ancla `F283`.
  - Serie 1: title=`None`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$A$285:$A$340`, yVal=`'QF-378HST'!$D$285:$D$340`.
- Gráfico 4: tipo `ScatterChart`, ancla `E311`.
  - Serie 1: title=`None`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$E$285:$E$340`, yVal=`'QF-378HST'!$A$285:$A$340`.
  - Serie 2: title=`Bomba`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$G$313:$G$314`, yVal=`'QF-378HST'!$H$313:$H$314`.
- Gráfico 5: tipo `ScatterChart`, ancla `A137`.
  - Serie 1: title=`1 AWG`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$J$136:$J$146`, yVal=`'QF-378HST'!$K$136:$K$146`.
  - Serie 2: title=`2 AWG`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$J$136:$J$146`, yVal=`'QF-378HST'!$L$136:$L$146`.
  - Serie 3: title=`'QF-378HST'!$N$135`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$J$136:$J$146`, yVal=`'QF-378HST'!$N$136:$N$146`.
  - Serie 4: title=`Punto de operación`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$G$74`, yVal=`'QF-378HST'!$G$68`.
- Gráfico 6: tipo `ScatterChart`, ancla `E137`.
  - Serie 1: title=`1 AWG`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$J$149:$J$150`, yVal=`'QF-378HST'!$K$149:$K$150`.
  - Serie 2: title=`2 AWG`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$L$149:$L$150`, yVal=`'QF-378HST'!$M$149:$M$150`.
  - Serie 3: title=`4 AWG`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$N$149:$N$150`, yVal=`'QF-378HST'!$O$149:$O$150`.
  - Serie 4: title=`None`, val=`None`, cat=`None`, xVal=`'QF-378HST'!$G$129`, yVal=`'QF-378HST'!$G$135`.

Bloque numérico inferior (`Measured`):

- Bloque con encabezado en fila 283: A=Measured, B=Incl. (deg), C=Azim. (deg), D=Vertical, E=Dogleg.
- Fila siguiente: A=Depth (ft), D=Depth(ft), E=(º/100ft).
- Filas con valor numérico en la columna A dentro de ese bloque: 59.
- Columna A (etiqueta de encabezado Measured / Depth (ft)): n=59, min=0, max=4598, p05=458.1, mediana=2351, p95=4366.8.
- Diferencias entre filas consecutivas de A: n=58, min=38, mediana=81, max=275, p05=50.1, p95=93.65.
- La columna A de este bloque es estrictamente creciente entre filas consecutivas con número.
- Criterio de espaciamiento irregular: diferencia consecutiva ≤ 0, o mayor que 3× la mediana (81), o positiva y menor que la mediana/3. Pasos que cumplen el criterio: 1 de 58.
- Ejemplos: fila 286 Δ=275.
- Columna B (texto de encabezado Incl. (deg), fila de unidades/subtítulo —): constantes=59, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=59.
  Descriptivo: min=0, p05=3.201, Q1=10.015, mediana=33.37, Q3=62.16, p95=90.196, max=90.49.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-68.2025, 140.377] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
  Diferencia absoluta consecutiva: min=0, mediana=1.465, max=7.2. Pasos con |Δ|>180: 0.
- Columna C (texto de encabezado Azim. (deg), fila de unidades/subtítulo —): constantes=59, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=59.
  Descriptivo: min=0, p05=96.191, Q1=99.725, mediana=106.84, Q3=122.37, p95=268.053, max=280.42.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [65.7575, 156.338] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 13.
  Ejemplos: C285=0; C287=237.34; C288=247.12; C289=258.69; C290=267.55; C291=277.45; C292=280.42; C293=272.58; y 5 más.
  Diferencia absoluta consecutiva: min=0.01, mediana=1.68, max=144.91. Pasos con |Δ|>180: 0.
- Columna D (texto de encabezado Vertical, fila de unidades/subtítulo Depth(ft)): constantes=59, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=59.
  Descriptivo: min=0, p05=457.933, Q1=1447.46, mediana=2286.68, Q3=2896.88, p95=3015.57, max=3015.86.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-726.662, 5071] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
- Columna E (texto de encabezado Dogleg, fila de unidades/subtítulo (º/100ft)): constantes=59, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=59.
  Descriptivo: min=0, p05=0.235, Q1=1.465, mediana=2.95, Q3=4.34, p95=6.643, max=8.35.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-2.8475, 8.6525] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
- No hay valores repetidos en la columna A de este bloque.
- No hay filas duplicadas por tupla cacheada A–E en este bloque.

Puntos de la curva con encabezados `Caudal` / `Head` / `Brake` / `EFF`:

- Fila 47: E=Caudal, F=Head, G=Brake, H=EFF.
- Fila 48: E=BFPD, F=ft, G=HP, H=%.
- Filas de puntos con E numérico constante: 6 (filas [49, 50, 51, 52, 53, 54]).
- Puntos (fila, E, F, G, H): 49: 333, 68, 1.656, 1.069; 50: 2000, 63.522, 2.174, 4.3; 51: 4000, 59.772, 2.833, 6.2; 52: 6000, 52.296, 3.166, 7.3; 53: 8000, 29.814, 3.027, 6.9; 54: 10000, 1.532, 2.766, 0.4082.
- La secuencia de la columna E en esos puntos es estrictamente creciente.
- La secuencia de la columna F en esos puntos es no creciente.
- Fila 55: E=`Limite minimo`, G=2000 (fórmula=False), H=BFPD, caché G=2000.
- Fila 56: E=`Cono de eficiencia`, G=6000 (fórmula=False), H=BFPD, caché G=6000.
- Fila 57: E=`Limite maximo`, G=8000 (fórmula=False), H=BFPD, caché G=8000.

Textos de la columna A que aparecen más de una vez en la misma hoja (etiqueta repetida, no una columna duplicada de una tabla):

- `Caudal`: 4 veces (filas 68, 81, 181, 227).
- `Promedio`: 4 veces (filas 251, 255, 265, 269).
- `Velocidad`: 3 veces (filas 66, 80, 223).
- `Potencia`: 3 veces (filas 191, 198, 205).
- `I Promedio`: 3 veces (filas 245, 259, 273).
- `Potencia KVA`: 3 veces (filas 246, 260, 274).
- `THP`: 2 veces (filas 72, 230).
- `Voltaje entrada`: 2 veces (filas 189, 196).
- `U-V`: 2 veces (filas 248, 262).
- `V-W`: 2 veces (filas 249, 263).
- `U-W`: 2 veces (filas 250, 264).
- `U-N`: 2 veces (filas 252, 266).
- `V-N`: 2 veces (filas 253, 267).
- `W-N`: 2 veces (filas 254, 268).
- `I(U)`: 2 veces (filas 256, 270).
- `I(V)`: 2 veces (filas 257, 271).
- `I(W)`: 2 veces (filas 258, 272).

Rangos combinados:

`E129:F129`, `E23:F23`, `E131:F131`, `A91:C91`, `E99:F99`, `E8:H8`, `B221:G221`, `E27:F27`, `I65:K65`, `B217:H218`, `E10:H10`, `E93:F93`, `B41:C41`, `B35:C35`, `E45:H45`, `E101:H101`, `E55:F55`, `E91:H91`, `E127:F127`, `E185:F185`, `E133:G133`, `A261:G261`, `F149:H149`, `A29:C29`, `B64:G64`, `E125:G125`, `A13:C13`, `A233:G233`, `E25:F25`, `B113:H114`, `E66:F66`, `B77:G77`, `A247:G247`, `B125:C125`, `E68:F68`, `A101:C101`, `E135:F135`, `E39:F39`, `B43:C43`, `E29:F29`, `B283:B284`, `E31:F31`, `E15:F15`, `E46:F46`, `B123:D123`, `E95:F95`, `E70:F70`, `E13:H13`, `E57:F57`, `E72:F72`, `A79:C79`, `E41:F41`, `C283:C284`, `B149:D149`, `E6:H6`, `F222:G222`, `E56:F56`, `E43:F43`, `D222:E222`, `E33:F33`, `B119:D119`, `G107:H107`, `B2:H3`, `E17:F17`, `B117:F117`, `E19:F19`, `B60:H61`, `E74:F74`, `B279:H280`, `E35:H35`, `A39:C39`, `B173:H174`, `E179:F179`, `B121:D121`, `B222:C222`, `B177:F177`, `E37:F37`, `E97:F97`, `E21:F21`

Filas vacías:

1, 3, 4, 5, 7, 9, 11, 12, 14, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 40, 42, 44, 58, 59, 61, 62, 63, 75, 76, 78, 89, 90, 96, 98, 100, 106, 108, 110, 111, 112, 114, 115, 116, 118, 120, 122, 124, 126, 128, 130, 132, 134, 147, 152, 154, 156, 158, 160, 162, 164, 166, 168, 170, 171, 172, 174, 175, 176, 178, 180, 182, 184, 186, 188, 190, 192, 195, 197, 199, 202, 204, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 218, 219, 220, 275, 277, 278, 280, 281, 282

### QF-549HST

- Estado: `visible`.
- Dimensión openpyxl: `A1:S351` (351 filas × 19 columnas, A–S).
- Celdas no vacías en la vista de fórmulas (valor no nulo): 1181.
- De esas celdas: fórmulas 246; constantes 935 (numéricas 466, texto 466, fechas-tipo en la constante 3).
- Fórmulas con caché nulo: 0. Fórmulas cuyo caché es el mismo texto de la fórmula: 0.
- Celdas combinadas: 79.
- Tablas: ninguna. Nombres definidos: ninguno a nivel de libro.
- Filas vacías dentro de 1..351: 101.
- Columnas vacías dentro de A..S: P.
- Filas ocultas: ninguna. Columnas ocultas: ninguna.
- Vista: `pageBreakPreview`, zoom `90`. Paneles congelados: `None`. Títulos de impresión: filas `None`, columnas `None`.
- Formato condicional (reglas): 0. Validaciones: 0. Comentarios: 0. Imágenes: 1. Gráficos: 6.
- Errores de Excel en fórmula o en caché: 13.

Títulos largos o de sección localizados (coordenada y texto):

- `B2`: `Análisis de Comportamiento de un Sistema ESP`
- `A13`: `Información Mecánica del Pozo`
- `E13`: `Información de Producción y Fluido`
- `E17`: `Presión de Yacimiento`
- `E19`: `Presión de Burbuja`
- `E27`: `Temperatura de fondo`
- `A29`: `Tuberia de Producción`
- `E29`: `Temperatura de fondo`
- `E35`: `Información de Cable Instalado`
- `A39`: `Información de Bomba Instalada`
- `E45`: `Curva de Performance de Bomba`
- `E56`: `Cono de eficiencia`
- `B60`: `Análisis de Comportamiento de un Sistema ESP`
- `B64`: `Condiciones de Operación Actuales`
- `E68`: `Corriente de Motor`
- `E70`: `Factor de Potencia`
- `E72`: `Eficiencia del motor`
- `A74`: `Vibración del Motor`
- `E74`: `Temperatura de Motor`
- `B77`: `Curva de la Bomba Según Velocidad Actual`
- `A79`: `Curva de Performance de Bomba`
- `A91`: `Cálculo de Gradiente de Presión`
- `E91`: `Cálculo de la THD TOTAL`
- `A93`: `Gravedad Oil @ 60ºF`
- `A95`: `Gravedad Oil @ T fondo`
- `A97`: `Densidad de Fluido`
- `E97`: `Perdidad por Fricción`
- `A99`: `Gradiente de Presión`
- `A101`: `Cálculo de Producción y consumo`
- `E101`: `Difrencia entre calculos y medición`
- `A105`: `Potencia a consumir`
- `A107`: `Potencia Transferida`
- `A109`: `Eficiencia de la bomba`
- `B113`: `Análisis de Comportamiento de un Sistema ESP`
- `B117`: `Cálculo de Consumo Energetico`
- `B119`: `Consumo de Potencia Bomba`
- `B121`: `Consumo de Potencia Sello`
- `B123`: `Potencia a entregar por el motor`
- `E125`: `Datos de operación del Motor`
- `E127`: `Porcentaje de carga`
- `E133`: `Caida de Voltaje en el Cable`
- `E135`: `Voltaje @ 1000 ft (V)`
- `B149`: `Información del SUT`
- `B173`: `Análisis de Comportamiento de un Sistema ESP`
- `B177`: `Analisis de Data Simulada Vs Medida`
- `E179`: `Fecha Prueba de Pozo`
- `B217`: `Análisis de Comportamiento de un Sistema ESP`
- `B221`: `Actividad de Revisión Equipos 10/08/2017`
- `A228`: `Temperatura de Fluido`
- `A276`: `Perdida de Energia`
- `B279`: `Análisis de Comportamiento de un Sistema ESP`

Fechas con tipo fecha, o fórmula cuya caché es fecha:

- `B6`: fórmula/constante `2017-09-06`; caché `2017-09-06`.
- `G179`: fórmula/constante `2017-08-07`; caché `2017-08-07`.
- `G185`: fórmula/constante `2017-08-01`; caché `2017-08-01`.

Textos que contienen una secuencia `dd/mm/aaaa` o similar:

- `B221`: `Actividad de Revisión Equipos 10/08/2017` (fragmentos ['10/08/2017']).

Gráficos (ancla = celda aproximada de la esquina superior; referencias de serie tal como las expone openpyxl):

- Gráfico 1: tipo `ScatterChart`, ancla `A46`.
  - Serie 1: title=`Head (ft)`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$E$49:$E$54`, yVal=`'QF-549HST'!$F$49:$F$54`.
- Gráfico 2: tipo `ScatterChart`, ancla `D78`.
  - Serie 1: title=`Head (ft)`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$A$83:$A$88`, yVal=`'QF-549HST'!$B$83:$B$88`.
  - Serie 2: title=`Operación Real`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$B$68`, yVal=`'QF-549HST'!$G$99`.
  - Serie 3: title=`Operación Ideal`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$B$103`, yVal=`'QF-549HST'!$G$99`.
  - Serie 4: title=`'QF-549HST'!$I$80`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$J$82:$J$87`, yVal=`'QF-549HST'!$K$82:$K$87`.
  - Serie 5: title=`'QF-549HST'!$M$80`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$N$82:$N$87`, yVal=`'QF-549HST'!$O$82:$O$87`.
  - Serie 6: title=`'QF-549HST'!$Q$80`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$R$82:$R$87`, yVal=`'QF-549HST'!$S$82:$S$87`.
  - Serie 7: title=`Menos etapas`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$I$69:$I$74`, yVal=`'QF-549HST'!$J$69:$J$74`.
- Gráfico 3: tipo `ScatterChart`, ancla `F283`.
  - Serie 1: title=`None`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$A$285:$A$340`, yVal=`'QF-549HST'!$D$285:$D$340`.
- Gráfico 4: tipo `ScatterChart`, ancla `F316`.
  - Serie 1: title=`None`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$E$285:$E$340`, yVal=`'QF-549HST'!$A$285:$A$340`.
  - Serie 2: title=`Bomba`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$G$313:$G$314`, yVal=`'QF-549HST'!$H$313:$H$314`.
- Gráfico 5: tipo `ScatterChart`, ancla `A137`.
  - Serie 1: title=`1 AWG`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$J$136:$J$146`, yVal=`'QF-549HST'!$K$136:$K$146`.
  - Serie 2: title=`2 AWG`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$J$136:$J$146`, yVal=`'QF-549HST'!$L$136:$L$146`.
  - Serie 3: title=`'QF-549HST'!$N$135`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$J$136:$J$146`, yVal=`'QF-549HST'!$N$136:$N$146`.
  - Serie 4: title=`Punto de operación`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$G$74`, yVal=`'QF-549HST'!$G$68`.
- Gráfico 6: tipo `ScatterChart`, ancla `E137`.
  - Serie 1: title=`1 AWG`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$J$149:$J$150`, yVal=`'QF-549HST'!$K$149:$K$150`.
  - Serie 2: title=`2 AWG`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$L$149:$L$150`, yVal=`'QF-549HST'!$M$149:$M$150`.
  - Serie 3: title=`4 AWG`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$N$149:$N$150`, yVal=`'QF-549HST'!$O$149:$O$150`.
  - Serie 4: title=`None`, val=`None`, cat=`None`, xVal=`'QF-549HST'!$G$129`, yVal=`'QF-549HST'!$G$135`.

Bloque numérico inferior (`Measured`):

- Bloque con encabezado en fila 283: A=Measured, B=Incl. (deg), C=Azim. (deg), D=Vertical, E=Dogleg.
- Fila siguiente: A=Depth (ft), D=Depth(ft), E=(º/100ft).
- Filas con valor numérico en la columna A dentro de ese bloque: 67.
- Columna A (etiqueta de encabezado Measured / Depth (ft)): n=67, min=0, max=4592, p05=514.2, mediana=2339, p95=4342.1.
- Diferencias entre filas consecutivas de A: n=66, min=54, mediana=63, max=362, p05=61, p95=94.75.
- La columna A de este bloque es estrictamente creciente entre filas consecutivas con número.
- Criterio de espaciamiento irregular: diferencia consecutiva ≤ 0, o mayor que 3× la mediana (63), o positiva y menor que la mediana/3. Pasos que cumplen el criterio: 1 de 66.
- Ejemplos: fila 286 Δ=362.
- Columna B (texto de encabezado Incl. (deg), fila de unidades/subtítulo —): constantes=67, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=67.
  Descriptivo: min=0, p05=3.159, Q1=10.38, mediana=28.26, Q3=85.465, p95=90.332, max=91.48.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-102.248, 198.093] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
  Diferencia absoluta consecutiva: min=0.11, mediana=1.575, max=7.07. Pasos con |Δ|>180: 0.
- Columna C (texto de encabezado Azim. (deg), fila de unidades/subtítulo —): constantes=67, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=67.
  Descriptivo: min=0, p05=4.556, Q1=12.905, mediana=17.82, Q3=251.45, p95=296.701, max=353.62.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-344.913, 609.267] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
  Diferencia absoluta consecutiva: min=0.03, mediana=1.465, max=351.35. Pasos con |Δ|>180: 2.
  Esos pasos: filas 285->286: 0 a 214.47 (Δ=214.47); filas 315->316: 353.62 a 2.27 (Δ=-351.35).
- Columna D (texto de encabezado Vertical, fila de unidades/subtítulo Depth(ft)): constantes=67, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=67.
  Descriptivo: min=0, p05=514.006, Q1=1307.67, mediana=2281.96, Q3=2841.34, p95=2857.85, max=2859.3.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-992.835, 5141.85] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
- Columna E (texto de encabezado Dogleg, fila de unidades/subtítulo (º/100ft)): constantes=67, fórmulas=0, vacías=0, errores cacheados=0, numéricos leídos=67.
  Descriptivo: min=0, p05=0.524, Q1=1.495, mediana=3.3, Q3=5.96, p95=7.67, max=7.91.
  Criterio de rango atípico (Tukey, dentro de este bloque y esta columna): fuera de [-5.2025, 12.6575] (Q1−1.5·IQR, Q3+1.5·IQR). Celdas que cumplen el criterio: 0.
- No hay valores repetidos en la columna A de este bloque.
- No hay filas duplicadas por tupla cacheada A–E en este bloque.

Puntos de la curva con encabezados `Caudal` / `Head` / `Brake` / `EFF`:

- Fila 47: E=Caudal, F=Head, G=Brake, H=EFF.
- Fila 48: E=BFPD, F=ft, G=HP, H=%.
- Filas de puntos con E numérico constante: 6 (filas [49, 50, 51, 52, 53, 54]).
- Puntos (fila, E, F, G, H): 49: 333, 68, 1.656, 1.069; 50: 2000, 63.522, 2.174, 4.3; 51: 4000, 59.772, 2.833, 6.2; 52: 6000, 52.296, 3.166, 7.3; 53: 8000, 29.814, 3.027, 6.9; 54: 10000, 1.532, 2.766, 0.4082.
- La secuencia de la columna E en esos puntos es estrictamente creciente.
- La secuencia de la columna F en esos puntos es no creciente.
- Fila 55: E=`Limite minimo`, G=2000 (fórmula=False), H=BFPD, caché G=2000.
- Fila 56: E=`Cono de eficiencia`, G=6000 (fórmula=False), H=BFPD, caché G=6000.
- Fila 57: E=`Limite maximo`, G=8000 (fórmula=False), H=BFPD, caché G=8000.

Textos de la columna A que aparecen más de una vez en la misma hoja (etiqueta repetida, no una columna duplicada de una tabla):

- `Caudal`: 4 veces (filas 68, 81, 181, 227).
- `Promedio`: 4 veces (filas 251, 255, 265, 269).
- `Velocidad`: 3 veces (filas 66, 80, 223).
- `Potencia`: 3 veces (filas 191, 198, 205).
- `I Promedio`: 3 veces (filas 245, 259, 273).
- `Potencia KVA`: 3 veces (filas 246, 260, 274).
- `THP`: 2 veces (filas 72, 230).
- `Voltaje entrada`: 2 veces (filas 189, 196).
- `U-V`: 2 veces (filas 248, 262).
- `V-W`: 2 veces (filas 249, 263).
- `U-W`: 2 veces (filas 250, 264).
- `U-N`: 2 veces (filas 252, 266).
- `V-N`: 2 veces (filas 253, 267).
- `W-N`: 2 veces (filas 254, 268).
- `I(U)`: 2 veces (filas 256, 270).
- `I(V)`: 2 veces (filas 257, 271).
- `I(W)`: 2 veces (filas 258, 272).

Rangos combinados:

`E129:F129`, `E23:F23`, `E131:F131`, `A91:C91`, `E99:F99`, `E8:H8`, `B221:G221`, `E27:F27`, `I65:K65`, `B217:H218`, `E10:H10`, `E93:F93`, `B41:C41`, `B35:C35`, `E45:H45`, `E101:H101`, `E55:F55`, `E91:H91`, `E127:F127`, `E185:F185`, `E133:G133`, `A261:G261`, `F149:H149`, `A29:C29`, `B64:G64`, `E125:G125`, `A13:C13`, `A233:G233`, `E25:F25`, `B113:H114`, `E66:F66`, `B77:G77`, `A247:G247`, `B125:C125`, `E68:F68`, `A101:C101`, `E135:F135`, `E39:F39`, `B43:C43`, `E29:F29`, `B283:B284`, `E31:F31`, `E46:F46`, `E15:F15`, `B123:D123`, `E95:F95`, `E70:F70`, `E13:H13`, `E57:F57`, `E72:F72`, `A79:C79`, `E41:F41`, `C283:C284`, `F222:G222`, `B149:D149`, `E6:H6`, `E56:F56`, `E43:F43`, `D222:E222`, `E33:F33`, `B119:D119`, `G107:H107`, `B2:H3`, `E17:F17`, `B117:F117`, `E19:F19`, `B60:H61`, `E74:F74`, `B279:H280`, `E35:H35`, `A39:C39`, `B173:H174`, `E179:F179`, `B121:D121`, `B222:C222`, `B177:F177`, `E37:F37`, `E97:F97`, `E21:F21`

Filas vacías:

1, 3, 4, 5, 7, 9, 11, 12, 14, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 40, 42, 44, 58, 59, 61, 62, 63, 75, 76, 78, 89, 90, 96, 98, 100, 106, 108, 110, 111, 112, 114, 115, 116, 118, 120, 122, 124, 126, 128, 130, 132, 134, 147, 152, 154, 156, 158, 160, 162, 164, 166, 168, 170, 171, 172, 174, 175, 176, 178, 180, 182, 184, 186, 188, 190, 192, 195, 197, 199, 202, 204, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 218, 219, 220, 275, 277, 278, 280, 281, 282

## Unidades escritas en columnas C o H

Se listan textos de longitud ≤ 16 en las columnas C y H, que en este formulario suelen estar al lado de un número. La cuenta es de celdas, sumando las cinco hojas. Que un texto parezca una unidad no añade una definición: significado pendiente de documentación salvo el propio texto.

| Texto | Celdas | Ejemplos de dirección |
|---|---:|---|
| `BFPD` | 40 | QF-554H!H24, QF-554H!H56, QF-554H!H57 |
| `psi` | 35 | QF-554H!H18, QF-554H!H20, QF-554H!H22 |
| `ºF` | 25 | QF-554H!H28, QF-554H!H44, QF-554H!H77 |
| `V` | 25 | QF-554H!H69, QF-554H!H159, QF-554H!C248 |
| `A` | 25 | QF-554H!H71, QF-554H!H161, QF-554H!C256 |
| `KVA` | 25 | QF-554H!H157, QF-554H!H165, QF-554H!H169 |
| `Hz` | 20 | QF-554H!H47, QF-554H!C69, QF-554H!C83 |
| `HP` | 20 | QF-554H!C85, QF-554H!C108, QF-554H!C110 |
| `ft` | 20 | QF-554H!H96, QF-554H!H98, QF-554H!H100 |
| `%` | 15 | QF-554H!H26, QF-554H!H49, QF-554H!H75 |
| `inch` | 10 | QF-554H!C32, QF-554H!C38, QF-545H!C31 |
| `TVD (ft)` | 5 | QF-554H!C16, QF-545H!C15, QF-500H!C15 |
| `Unidad` | 5 | QF-554H!H16, QF-545H!H15, QF-500H!H15 |
| `Calculada` | 5 | QF-554H!C17, QF-545H!C16, QF-500H!C16 |
| `ºC` | 5 | QF-554H!H30, QF-545H!H29, QF-500H!H29 |
| `ºAPI` | 5 | QF-554H!H32, QF-545H!H31, QF-500H!H31 |
| `LB/ft` | 5 | QF-554H!C34, QF-545H!C33, QF-500H!C33 |
| `AWG` | 5 | QF-554H!H38, QF-545H!H37, QF-500H!H37 |
| `KV` | 5 | QF-554H!H42, QF-545H!H41, QF-500H!H41 |
| `Nº` | 5 | QF-554H!C46, QF-545H!C45, QF-500H!C45 |
| `EFF` | 5 | QF-554H!H48, QF-545H!H47, QF-500H!H47 |
| `G` | 5 | QF-554H!C77, QF-545H!C75, QF-500H!C76 |
| `Brake` | 5 | QF-554H!C84, QF-545H!C82, QF-500H!C83 |
| `psi*ft` | 5 | QF-554H!C102, QF-545H!C100, QF-500H!C101 |
| `BOPD` | 5 | QF-554H!H108, QF-545H!H106, QF-500H!H107 |
| `Rx` | 5 | QF-554H!C237, QF-545H!C231, QF-500H!C228 |
| `Kg/Lt` | 5 | QF-554H!C240, QF-545H!C234, QF-500H!C231 |
| `Azim. (deg)` | 5 | QF-554H!C327, QF-545H!C313, QF-500H!C285 |
| `Lb/gln` | 4 | QF-554H!H34, QF-500H!H33, QF-378HST!H33 |
| `Lb/Gln` | 4 | QF-554H!C100, QF-545H!C98, QF-500H!C99 |
| `Responsable:` | 2 | QF-554H!C6, QF-500H!C6 |
| `Página 1` | 2 | QF-554H!H61, QF-545H!H59 |
| `Página 2` | 2 | QF-554H!H117, QF-545H!H113 |
| `Página 3` | 2 | QF-554H!H181, QF-545H!H175 |
| `Página 4` | 2 | QF-554H!H227, QF-545H!H220 |
| `Página 5` | 2 | QF-554H!H278, QF-545H!H268 |
| `Página 6` | 2 | QF-554H!H321, QF-545H!H307 |
| `Página 7` | 1 | QF-554H!H388 |
| `Lb/galn` | 1 | QF-545H!H33 |
| `Lb/Galn` | 1 | QF-549HST!C97 |

Variantes de grafía observadas para textos vecinos a `Densidad del Agua` o `Densidad de Fluido`: se documentan en `calidad.md` a partir de la celda de cada hoja, no como equivalencia.

## Valores capturados junto a etiquetas de la zona mecánica

Primera aparición de la etiqueta en la columna A, por encima del título `Condiciones de Operación Actuales`. Se muestra el valor cacheado de B. Si B es fórmula, se indica. La unidad es el texto de C cuando es texto.

| Etiqueta | QF-554H | QF-545H | QF-500H | QF-378HST | QF-549HST |
|---|---|---|---|---|---|
| `Descarga` | 2841.51 [=+H361] (constante) | 2978.66 [=+H347] (constante) | 2801.9 [=+H319] (constante) | 3018.77 [=+H317] (constante) | 2787.17 [=+H317] (constante) |
| `Intake` | 2856.1 [=H365] (constante) | 2994.87 [=H351] (constante) | 2813.57 [=H323] (constante) | 3028.46 [=H321] (constante) | 2796.27 [=H321] (constante) |
| `Motor` | 2873.71 [=H369] (constante) | 3011.25 [=H355] (constante) | 2857.43 [=H327] (constante) | 3046.09 [=H325] (constante) | 2805.98 [=H325] (constante) |
| `Sensor` | 2900.58 [=H373] (constante) | 3038.12 [=H359] (constante) | 2859.3 [=H331] (constante) | 3061.68 [=H329] (constante) | 2829.66 [=H329] (constante) |
| `Perforados` | 3780 [=H377] (constante) | 3933 [=H363] (constante) | 3977 [=H335] (constante) | 4166 [=H333] (constante) | 3712 [=H333] (constante) |
| `OD` | 3.5 [inch] (constante) | 3.5 [inch] (constante) | 3.5 [inch] (constante) | 3.5 [inch] (constante) | 3.5 [inch] (constante) |
| `Peso` | 9.3 [LB/ft] (constante) | 9.3 [LB/ft] (constante) | 9.3 [LB/ft] (constante) | 9.3 [LB/ft] (constante) | 9.3 [LB/ft] (constante) |
| `Grado` | N80 (constante) | N80 (constante) | N80 (constante) | N80 (constante) | N80 (constante) |
| `ID` | 2.996 [inch] (constante) | 2.996 [inch] (constante) | 2.996 [inch] (constante) | 2.996 [inch] (constante) | 2.996 [inch] (constante) |
| `Fabricante` | Schlumberger (constante) | Schlumberger (constante) | Schlumberger (constante) | Schlumberger (constante) | Schlumberger (constante) |
| `Referencia` | S 8000N (constante) | S 8000N (constante) | S 8000N (constante) | S6000N (constante) | S6000N (constante) |
| `Etapas` | 53 [Nº] (constante) | 50 [Nº] (constante) | 36 [Nº] (constante) | 31 [Nº] (constante) | 31 [Nº] (constante) |

Etiquetas de la columna E en la misma zona (valor en G, texto de H entre corchetes). `Temperatura de fondo` aparece dos veces por hoja; se listan todas las apariciones de esa zona.

| Etiqueta | QF-554H | QF-545H | QF-500H | QF-378HST | QF-549HST |
|---|---|---|---|---|---|
| `Presión de Yacimiento` | fila 18: 1100 [psi] (constante) | fila 17: 1100 [psi] (constante) | fila 17: 1100 [psi] (constante) | fila 17: 1100 [psi] (constante) | fila 17: 1100 [psi] (constante) |
| `Presión de Burbuja` | fila 20: 130 [psi] (constante) | fila 19: 130 [psi] (constante) | fila 19: 130 [psi] (constante) | fila 19: 130 [psi] (constante) | fila 19: 130 [psi] (constante) |
| `Presión de Prueba` | fila 22: 732 [psi] (constante) | fila 21: 654 [psi] (constante) | fila 21: 821 [psi] (constante) | fila 21: 810 [psi] (constante) | fila 21: 607 [psi] (constante) |
| `Caudal de Prueba` | fila 24: 10301 [BFPD] (constante) | fila 23: 8767 [BFPD] (constante) | fila 23: 7728 [BFPD] (constante) | fila 23: 7094.4 [BFPD] (fórmula) | fila 23: 5419 [BFPD] (constante) |
| `BS&W` | fila 26: 0.9755 [%] (constante) | fila 25: 0.9766 [%] (constante) | fila 25: 0.9644 [%] (constante) | fila 25: 0.9557 [%] (constante) | fila 25: 0.9557 [%] (constante) |
| `Temperatura de fondo` | fila 28: 150 [ºF] (constante)<br>fila 30: 65.5556 [ºC] (fórmula) | fila 27: 144 [ºF] (constante)<br>fila 29: 62.2222 [ºC] (fórmula) | fila 27: 150 [ºF] (constante)<br>fila 29: 65.5556 [ºC] (fórmula) | fila 27: 150 [ºF] (constante)<br>fila 29: 65.5556 [ºC] (fórmula) | fila 27: 150 [ºF] (constante)<br>fila 29: 65.5556 [ºC] (fórmula) |
| `API` | fila 32: 12 [ºAPI] (constante) | fila 31: 12 [ºAPI] (constante) | fila 31: 12 [ºAPI] (constante) | fila 31: 12 [ºAPI] (constante) | fila 31: 12 [ºAPI] (constante) |
| `Densidad del Agua` | fila 34: 8.345 [Lb/gln] (constante) | fila 33: 8.345 [Lb/galn] (constante) | fila 33: 8.345 [Lb/gln] (constante) | fila 33: 8.345 [Lb/gln] (constante) | fila 33: 8.345 [Lb/gln] (constante) |
| `Calibre` | fila 38: 2 [AWG] (constante) | fila 37: 2 [AWG] (constante) | fila 37: 2 [AWG] (constante) | fila 37: 2 [AWG] (constante) | fila 37: 2 [AWG] (constante) |
| `Tipo` | fila 40: Plano (constante) | fila 39: Plano (constante) | fila 39: Plano (constante) | fila 39: Plano (constante) | fila 39: Plano (constante) |
| `Voltaje` | fila 42: 5 [KV] (constante) | fila 41: 5 [KV] (constante) | fila 41: 5 [KV] (constante) | fila 41: 5 [KV] (constante) | fila 41: 5 [KV] (constante) |
| `Temperatura` | fila 44: 450 [ºF] (constante) | fila 43: 450 [ºF] (constante) | fila 43: 450 [ºF] (constante) | fila 43: 450 [ºF] (constante) | fila 43: 450 [ºF] (constante) |

## Condiciones de operación (bloque bajo ese título)

Etiquetas tomadas de las 20 filas siguientes al título `Condiciones de Operación Actuales`. Valor cacheado. Significado pendiente de documentación.

### QF-554H

| Fila | Lado | Etiqueta | Valor en la celda | Caché | Texto de unidad vecina |
|---|---|---|---|---|---|
| 69 | A-B | `Velocidad` | `63` | 63 | Hz |
| 69 | E-G | `Voltaje de motor` | `3174` | 3174 | V |
| 71 | A-B | `Caudal` | `10301` | 10301 | BFPD |
| 71 | E-G | `Corriente de Motor` | `38.3` | 38.3 | A |
| 73 | A-B | `Presión de Sensor` | `732` | 732 | psi |
| 73 | E-G | `Factor de Potencia` | `0.99` | 0.99 | — |
| 75 | A-B | `THP` | `183` | 183 | psi |
| 75 | E-G | `Eficiencia del motor` | `0.91` | 0.91 | % |
| 77 | A-B | `Vibración del Motor` | `0` | 0 | G |
| 77 | E-G | `Temperatura de Motor` | `155` | 155 | ºF |
| 83 | A-B | `Velocidad` | `=B69` | 63 | Hz |
| 84 | A-B | `Caudal` | `Head` | Head | Brake |

### QF-545H

| Fila | Lado | Etiqueta | Valor en la celda | Caché | Texto de unidad vecina |
|---|---|---|---|---|---|
| 67 | A-B | `Velocidad` | `57` | 57 | Hz |
| 67 | E-G | `Voltaje de motor` | `2829` | 2829 | V |
| 69 | A-B | `Caudal` | `8767` | 8767 | BFPD |
| 69 | E-G | `Corriente de Motor` | `30.3` | 30.3 | A |
| 71 | A-B | `Presión de Sensor` | `667` | 667 | psi |
| 71 | E-G | `Factor de Potencia` | `0.99` | 0.99 | — |
| 73 | A-B | `THP` | `210` | 210 | psi |
| 73 | E-G | `Eficiencia del motor` | `0.91` | 0.91 | % |
| 75 | A-B | `Vibración del Motor` | `0` | 0 | G |
| 75 | E-G | `Temperatura de Motor` | `145` | 145 | ºF |
| 81 | A-B | `Velocidad` | `=B67` | 57 | Hz |
| 82 | A-B | `Caudal` | `Head` | Head | Brake |

### QF-500H

| Fila | Lado | Etiqueta | Valor en la celda | Caché | Texto de unidad vecina |
|---|---|---|---|---|---|
| 68 | A-B | `Velocidad` | `56` | 56 | Hz |
| 68 | E-G | `Voltaje de motor` | `2704` | 2704 | V |
| 70 | A-B | `Caudal` | `=322*24` | 7728 | BFPD |
| 70 | E-G | `Corriente de Motor` | `22.6` | 22.6 | A |
| 72 | A-B | `Presión de Sensor` | `821` | 821 | psi |
| 72 | E-G | `Factor de Potencia` | `0.99` | 0.99 | — |
| 74 | A-B | `THP` | `194` | 194 | psi |
| 74 | E-G | `Eficiencia del motor` | `0.91` | 0.91 | % |
| 76 | A-B | `Vibración del Motor` | `0` | 0 | G |
| 76 | E-G | `Temperatura de Motor` | `144` | 144 | ºF |
| 82 | A-B | `Velocidad` | `=B68` | 56 | Hz |
| 83 | A-B | `Caudal` | `Head` | Head | Brake |

### QF-378HST

| Fila | Lado | Etiqueta | Valor en la celda | Caché | Texto de unidad vecina |
|---|---|---|---|---|---|
| 66 | A-B | `Velocidad` | `67` | 67 | Hz |
| 66 | E-G | `Voltaje de motor` | `2854` | 2854 | V |
| 68 | A-B | `Caudal` | `=296.5*24` | 7116 | BFPD |
| 68 | E-G | `Corriente de Motor` | `24` | 24 | A |
| 70 | A-B | `Presión de Sensor` | `810` | 810 | psi |
| 70 | E-G | `Factor de Potencia` | `0.99` | 0.99 | — |
| 72 | A-B | `THP` | `145` | 145 | psi |
| 72 | E-G | `Eficiencia del motor` | `0.85` | 0.85 | % |
| 74 | A-B | `Vibración del Motor` | `0` | 0 | G |
| 74 | E-G | `Temperatura de Motor` | `150` | 150 | ºF |
| 80 | A-B | `Velocidad` | `=B66` | 67 | Hz |
| 81 | A-B | `Caudal` | `Head` | Head | Brake |

### QF-549HST

| Fila | Lado | Etiqueta | Valor en la celda | Caché | Texto de unidad vecina |
|---|---|---|---|---|---|
| 66 | A-B | `Velocidad` | `62` | 62 | Hz |
| 66 | E-G | `Voltaje de motor` | `2672` | 2672 | V |
| 68 | A-B | `Caudal` | `5419` | 5419 | BFPD |
| 68 | E-G | `Corriente de Motor` | `22` | 22 | A |
| 70 | A-B | `Presión de Sensor` | `607` | 607 | psi |
| 70 | E-G | `Factor de Potencia` | `0.99` | 0.99 | — |
| 72 | A-B | `THP` | `177` | 177 | psi |
| 72 | E-G | `Eficiencia del motor` | `0.91` | 0.91 | % |
| 74 | A-B | `Vibración del Motor` | `0` | 0 | G |
| 74 | E-G | `Temperatura de Motor` | `162` | 162 | ºF |
| 80 | A-B | `Velocidad` | `=B66` | 62 | Hz |
| 81 | A-B | `Caudal` | `Head` | Head | Brake |

## Fórmulas y constantes

Hay fórmulas en las cinco hojas. Total de celdas con fórmula: 1270.

| Hoja | Fórmulas | Constantes no vacías | Caché presente en todas las fórmulas |
|---|---:|---:|---|
| `QF-554H` | 261 | 973 | sí |
| `QF-545H` | 240 | 979 | sí |
| `QF-500H` | 260 | 1031 | sí |
| `QF-378HST` | 263 | 967 | sí |
| `QF-549HST` | 246 | 935 | sí |

El detalle de patrones está en `formulas_muestra.md`. El detalle de duplicados, ceros, fechas y rangos está en `calidad.md`. El resumen por columna de Excel (A–S), que mezcla etiquetas y números porque el diseño es un formulario, está en `resumen_columnas.csv`.

## Limitaciones de lectura

- openpyxl lee el valor guardado. Con `data_only=True` entrega la caché de Excel; no recalcula el libro. `fullCalcOnLoad` está en verdadero, así que un Excel que abra el archivo puede volver a calcular `TODAY()`.
- No se ejecutaron macros. El archivo es xlsx; esta lectura usó `keep_vba=False`.
- Las celdas combinadas solo tienen valor en la esquina superior izquierda.
- Los gráficos no tienen título legible por esta vía. Las series se documentan por la referencia que expone openpyxl. La imagen embebida no se interpretó.
- No hay diccionario de datos dentro del libro. Una etiqueta no se tradujo a una definición.
- El rectángulo `dimensions` incluye celdas vacías de maquetación. El porcentaje de faltantes del CSV usa como universo `max_row` de cada hoja, así que cuenta huecos de formulario además de huecos de un dato.
- Min y max del CSV, cuando existen, salen del subconjunto numérico cacheado de esa columna. En un formulario ese subconjunto mezcla cantidades distintas que comparten columna.
- La comprobación aritmética local solo cubre fórmulas sin nombres de función (sumas, restas, multiplicaciones, divisiones y referencias). INDEX, MATCH, IF, AVERAGE, SQRT y TODAY no se recalcularon.
- Cuatro hojas cachean `TODAY()` como 2026-10-17. Esa fecha coincide con la fecha de `modified` del libro y con la fecha de esta lectura. No es una fecha escrita como constante de medición, salvo en `QF-549HST`, donde B6 es la constante 2017-09-06.

