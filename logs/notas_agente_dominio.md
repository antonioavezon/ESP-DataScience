# Notas del agente de dominio y fuentes

Estado: **borrador para revisión del coordinador**. Ninguna ecuación queda aprobada. No se combinan fuentes. No se atribuyen a este proyecto las métricas del paper ni el ejemplo del PDF.

Trabajo solo local. No se ejecutaron macros. No se instalaron paquetes. No se leyeron libros de datos de pozos. No se modificó ninguna fuente.

Herramientas de lectura: `sha256sum` y `cmp` del sistema; Python 3.14.8 (`zipfile` + `xml.etree`) para DOCX y XLSM; `.venv/bin/python` con PyMuPDF para el PDF (PyMuPDF y pypdf estaban disponibles; se usó PyMuPDF). Fedora 43, según el encargo.

---

## 1. Alcance y archivos leídos

Encargo: inventario fiel para que el coordinador redacte `docs/trazabilidad_ecuaciones.md`. Se leyeron los archivos de la raíz del proyecto. Existen copias en `fuentes/originales/`; no se usaron como fuente de extracción.

| Archivo | Bytes | SHA-256 | Qué se leyó |
|---|---:|---|---|
| `Modelo_Sensorless_PIP_ESP_Set_Ecuaciones.docx` | 43143 | `4ef527d9b2cafdb1ee689093af6883763c4c864d5dc863b3d1b7aaf51fbb5ccc` | `word/document.xml`, `docProps/core.xml`, `docProps/app.xml`. Sin OMML (`oMath` = 0). |
| `Modelo_Sensorless_PIP_ESP_Set_Ecuaciones (1).docx` | 43143 | igual al anterior | Solo hash y comparación byte a byte. |
| `Modelo_Sensorless_PIP_ESP_Set_Ecuaciones (2).docx` | 43143 | igual al anterior | Solo hash y comparación byte a byte. |
| `Modelo_Sensorless_PIP_ESP_Set_Ecuaciones (3).docx` | 43143 | igual al anterior | Solo hash y comparación byte a byte. |
| `Copia de Copia de Ecuaciones  _.xlsm` | 142127 | `1e9eb80131a48abd5054ad4f39df25c0c3917c8734b7094f21075c3539413941` | `xl/workbook.xml`, rels, cinco hojas, `sharedStrings.xml`, dibujos, presencia de `xl/vbaProject.bin`. |
| `004-ESPdesign.pdf` | 320563 | `9d14c9db228f33653d0cc408b205b65818772f357bf7dd9253f905e9573991ec` | 6 páginas. Texto extraído. La ecuación de Hazen-Williams no se linealiza de forma unívoca. |
| `paper_sensorless - v2.docx` | 34831 | `9eeddb2f155972183b55c19487c3afbe464623f68ad410305cd9c64542e86e69` | Texto y tablas de nomenclatura. Sin OMML. |
| `trabajo.md` | 27313 | `57d97df970ce6ebe1b901822de101d0379c13e82b5a19e8ab4b629965c7e8dbe` | Plan de alcance. No es fuente de ecuaciones físicas, salvo la definición de BEP que el propio plan declara. |

Metadatos DOCX de ecuaciones (`docProps`): creador `python-docx`; última modificación `Alexander zambrano`; revisión 42; `app.xml` declara 9 páginas y aplicación Microsoft Office Word 16. Fecha de modificación del paquete: 2026-10-17. Título Dublin Core vacío.

Metadatos XLSM: creador `Usuario`; última modificación `Alexander Zambrano`; creado 2016-05-18; modificado 2023-09-21; Excel 16.03. `workbook.xml` guarda `absPath` `E:\BES\`. `calcMode` = `autoNoTable`.

Metadatos PDF: título `Basic ESP design`; autor `Eng. Marcelo Hirschfeldt`; asunto `Oilproduction.net`; 6 páginas; fechas de creación/modificación del PDF en 2002-06-21. El metadato de cifrado indica RC4 de 40 bits; el texto se pudo leer.

Metadatos del paper: creador `Mario Sánchez Medina`; última modificación `Alexander Zambrano`; creado y modificado 2026-03-19; `app.xml` declara 5 páginas.

---

## 2. Comparación de duplicados DOCX

Los cuatro archivos `Modelo_Sensorless_PIP_ESP_Set_Ecuaciones*.docx` tienen el mismo SHA-256:

`4ef527d9b2cafdb1ee689093af6883763c4c864d5dc863b3d1b7aaf51fbb5ccc`

`cmp` entre el archivo sin sufijo y las copias `(1)`, `(2)` y `(3)` no encontró ninguna diferencia de bytes. Tamaño común: 43143 bytes.

Por tanto el XML interno es el mismo y el texto extraído es idéntico. En el catálogo se cita una sola vez, como `Modelo_Sensorless_PIP_ESP_Set_Ecuaciones.docx`. Las otras tres copias no aportan ecuaciones distintas.

---

## 3. Mapa del XLSM

Archivo: `Copia de Copia de Ecuaciones  _.xlsm`.

No hay elemento `definedNames` en `workbook.xml`. Nombres definidos: ninguno.

Visibilidad: ningún `<sheet>` trae atributo `state`. En OOXML la ausencia de `state` corresponde a hoja visible. No aparece la cadena `state=` en `workbook.xml`. No se afirma que una interfaz de Excel no pudiera ocultar algo por otro mecanismo; en el XML leído las cinco hojas no están marcadas como ocultas.

`sheetId` no es continuo: 1, 2, 4, 5, 7. Los id 3 y 6 no están en el paquete. No hay hojas extra dentro del ZIP. No se inventa qué contenían esos id.

| Orden | Nombre visible | Parte | codeName | Dimensión | Celdas con contenido | Fórmulas | Dibujo |
|---|---|---|---|---|---:|---:|---|
| 1 | Hoja1 | `xl/worksheets/sheet1.xml` | Hoja1 | `B2:L45` | 223 | 19 | `drawing1.xml` |
| 2 | METODO | `sheet2.xml` | Hoja2 | `B2:R47` | 290 | 25 | `drawing2.xml` |
| 3 | Metodo Ordenado | `sheet3.xml` | Hoja3 | `B2:Q54` | 338 | 31 | `drawing3.xml` |
| 4 | Hoja2 | `sheet4.xml` | Hoja4 | `A1:G13` | 31 | 8 | `drawing4.xml` |
| 5 | Prueba Sesnorless | `sheet5.xml` | Hoja5 | `B1:R82` | 444 | 49 | `drawing5.xml` |

El nombre visible de la quinta hoja está escrito **Sesnorless** en el XML.

VBA: existe `xl/vbaProject.bin`, 26112 bytes. Los primeros octetos son `d0cf11e0a1b11ae1` (contenedor OLE). Relación `vbaProject` en `workbook.xml.rels`. **No se ejecutó y no se descompiló.**

ActiveX: `xl/activeX/activeX1.bin` (68 bytes) y `activeX1.xml`, enlazados desde `sheet5.xml.rels` como control de la hoja Prueba Sesnorless. No se ejecutó.

También hay `xl/calcChain.xml`, impresoras, imágenes PNG/EMF y un `vmlDrawing` sin texto. Los dibujos contienen el texto de las ecuaciones escritas como leyenda; ese texto no siempre coincide con la fórmula de la celda. Se cita en las secciones 4 y 5.

Los valores numéricos de celdas con fórmula son el elemento `<v>` cacheado en el XML. Este agente no abrió Excel ni recalculó el libro. En la cadena de Prueba Sesnorless se contrastó, con aritmética de Python sobre esos `<v>` y las fórmulas, que el cache coincide con la fórmula almacenada. Eso no valida física ni unidades.

### 3.1 Hoja1 — entradas, cadena y salidas

Etiqueta de bloque: `DATA  232HST`.

Entradas escritas (sin fórmula), columna C, con la unidad que está en la columna D:

| Celda | Rótulo (col. B, texto original) | Valor cacheado | Unidad escrita en D |
|---|---|---|---|
| C3 | API | 16 | ° |
| C4 | Viscosidad Crudo  µo | 5 | cps |
| C5 | Constante de conversion | 62.4 | unidad no declarada en D5 |
| C6 | Gradiente del agua | 0.433 | psi/pie³ |
| C7 | Factor conversion de  µo | 6.7197e-4 | lbm/pie-seg |
| C8 | Presion del Reservorio Pr | 2000 | psi |
| C9 | IP | 1.5 | BPD/psi |
| C10 | BSW | 0 | % |
| C11 | Profundidad de los perforados | 7000 | pies |
| C12 | Sumergencia | 1000 | pies |
| C13 | Profundidad ESP | 6000 | pies |
| C14 | Tubing | 3.5 | Pulgadas |
| C15 | Diametro Interno Tubing di | 3 | Pulgadas |
| C16 | Rugosidad  ɛ | 0.001 | Pulgadas |
| C17 | Casing | 7 | Pulgadas |
| C18 | Profundidad del Casing | 7200 | pies |
| C19 | Factor Conversion Velocid | 5.615 | pc/B |
| C20 | Diametro tubing en ft | 0.25 | pies |
| C21 | Factor conversion de(ΔP/ΔL)friccion | 144 | lb/ft² |
| C22 | Pwh     THP | 200 | psi |
| J39 | Pies por etapa | 54 | pies |
| J40 | Eficiencia | 62 | % |
| J41 | Potencia por etapa | 1.4 | HP |

C10, C14, C15, C16, C17, C18, C19 no aparecen referenciados en las fórmulas de esta hoja. C15 = 3 pulgadas y C20 = 0.25 pies son coherentes entre sí (3/12 = 0.25), pero la velocidad usa C20, no C15. C5 y C7 están duplicados como literales dentro de fórmulas (62.4 y 0.00067197) y esas fórmulas no citan C5 ni C7.

Salidas con rótulo: J13 `Pwf=`, J15 `Caudal  Q=`, J33 `PIP=`, J35 `ΔP Bomba =`, J37 `Head=`, J43 `Numero de Etapas=`, J45 `Potencia de la bomba=`.

J33 (PIP) depende solo de sumergencia y gradiente. No depende del caudal ni de la potencia. El caudal J15 sale de IP y de Pwf; Pwf sale de PIP. No hay búsqueda de Q.

### 3.2 METODO

Misma retícula que Hoja1, más un bloque a la derecha (columnas O–R) y datos distintos. Etiqueta `DATA`. Pasos numerados 1) a 12) en celdas de texto, sin fórmula propia.

Entradas que cambian respecto de Hoja1 (valores cacheados): API 13.8 °; µo 367 cps; Pr 1119.94 psi; IP escrito 15.8 BPD/psi; BSW 96.6 %; perforados 2601.7453 pies; sumergencia 1574 pies; profundidad intake 2619.58 pies; DI tubing 2.992 pulgadas; THP 175 psi; Q Prueba C23 = 5215.67 BPD; Pwf Prueba C24 = 774.09 psi.

Bomba escrita a la derecha: modelo `GN4000`; `# etapas` P40 = 52; `Head/etapa` P41 = 63. Curva central sigue en 54 pies/etapa, eficiencia 62 %, 1.4 HP (J39–J41), igual que Hoja1.

C16 es fórmula `=0.0005*0.25`. D16 no declara unidad. Ninguna fórmula de fricción cita C16.

Hay **dos PIP**:

- J33 `PIP=` = `C12*J9` (sumergencia × gradiente).
- Q33 `PIP=` = `J31-Q37` (presión de descarga − ΔP ESP).

Q17 de velocidad usa **C23 (Q prueba)**, no el Q calculado J15. En Hoja1 la velocidad usa J15.

Tabla de régimen escrita, sin que ninguna fórmula la consulte: `<2000` Flujo Laminar; `2000-4000` Flujo transitorio; `>4000` Flujo turbulento. La fórmula de `f` sigue siendo `64/J19`. El Re cacheado de esta hoja es 425.377..., así que cae en el rótulo «laminar», pero la elección no está programada.

C20 sigue en 0.25 pies mientras C15 es 2.992 pulgadas. 2.992/12 no es 0.25. PENDIENTE.

### 3.3 Metodo Ordenado

Etiqueta `DATA  232HST     GN4000`.

Entradas distintas de METODO: IP escrito 12.04 BPD/psi; sumergencia 1553 pies; Q Prueba 4272 BPD; Pwf Prueba 765 psi.

Bomba: `HEAD` J13 = 3276 (sin unidad en la celda); `# etapas` H14 = 63; `Head/etapa` H15 = 52. El producto 63×52 = 3276 coincide con J13, pero **los rótulos de etapas y head/etapa están intercambiados respecto de METODO** (allí etapas = 52 y head/etapa = 63). PENDIENTE cuál rótulo corresponde al dato.

K13 = `J13*0.803` (cache 2630.628). M13 = 2631 escrito. El 0.803 no tiene celda ni rótulo. PENDIENTE.

L36 = 672, L38 = 1574, L40 = 1046, sin rótulo. Los mismos tres números reaparecen en Prueba Sesnorless (L23, L25, L27) al lado de PIP, sumergencia y nivel. PENDIENTE qué son.

C26 `Q Nueva` está vacía.

Dos expresiones etiquetadas eficiencia, con resultados cacheados que no son una fracción ni un porcentaje declarado:

- D32 `Eff Bomba=` = `((D40*C23*J7)/(1360*D42))`, cache 1960.832...
- C51 `Eff Bomba` = `(C50*C48*C49*J4)/D42`, cache 63.495...

C50 `densidad kg/m³` = 973.44, escrito, no enlazado a J7.

L47 es otro `IP=` con la fórmula larga de la sección 4. L54 `Qmax=`.

### 3.4 Hoja2

Solo coeficientes `a`, `b`, `c` y la fórmula cuadrática en B6 y B7. Literales 950, 4268, 4272, 0.8 y 0.2. El dibujo `drawing4.xml` no describe esa cuadrática: describe una potencia eléctrica y `Q/Qmax` con denominador 950. PENDIENTE el significado de a, b, c.

Celdas D9:G13 vacías.

### 3.5 Prueba Sesnorless — entradas, intermediarios y salidas

Etiquetas `DATA  232HST     GN4000`, `ECUACIONES DE LA BES`, `VARIABLES`.

**Entradas escritas usadas por alguna fórmula**

| Celda | Rótulo | Valor | Unidad escrita |
|---|---|---|---|
| C3 | API | 13.8 | ° |
| C4 | Viscosidad Crudo µo | 367 | cps |
| C6 | Gradiente del agua | 0.433 | psi/pie³ |
| C8 | Presion del Reservorio Py | 1119.94 | psi |
| C11 | Profundidad de los perforados | 2862.6 | pies |
| C13 | Profundidad Intake. ESP | 2619.58 | pies |
| C20 | Diametro tubing en ft | 0.25 | pies |
| C21 | Factor conversion de(ΔP/ΔL)friccion | 144 | lb/ft² |
| C22 | THP | 175 | psi |
| C23 | Q Prueba | 4272 | BPD |
| C24 | Pwf Prueba | 765 | psi |
| C25 | Frecuencia | 65 | Hz |
| C29 | Profundidad Sensor | 2657.6 | ft |
| C30 | Presion Casing | 0.1 | psi |
| C31 | Corriente motor | 31.95 | Amperios |
| C32 | voltaje motor | 2705 | Voltios |
| C33 | Eff Motor | 0.75 | unidad no declarada |
| C34 | Numero de Sellos | 2 | unidad no declarada |
| C35 | Eff Bomba | 0.62 | unidad no declarada |
| J21 | Pwf= | 735.42166666666662 | psi |

J21 **no es fórmula**. Es un número escrito. C28 `Pwf Actual` solo apunta a J21.

**Presentes y no citados por fórmulas** (PENDIENTE si sobran o si el cálculo está incompleto): C5 = 62.4; C7 = 6.7197e-4; C9 IP = 12.04 BPD/psi; C10 BSW = 96.6 %; C12 sumergencia = 1553 pies; C14 tubing 3.5 pulgadas; C15 DI 2.992 pulgadas; C17 casing 7 pulgadas; C18 profundidad casing 3779 pies; C19 = 5.615 pc/B; C27 Presion Burbuja = 130 psi; C36 Hz 2 = 65 Hz; C37 Hz 1 = 60 Hz; E1 = 15 sin rótulo.

Números escritos sin fórmula, con rótulo al lado: N19 = 12.035837042880486 rótulo `IP`; N20 = 11914.756522229109 rótulo `Qburbuja`; N21 = 12784.011419770477 rótulo `Qmax`; L23 = 672; O23 = 774 `Psi`; L25 = 1574; L27 = 1046. No alimentan las fórmulas leídas.

**Intermediarios con fórmula:** J4, J7, J9, Q11, J12, C16, C26, J17, J23, J25, J27, J29, J31, J33, J35, J37, J39, J41, L41, N41, L45, J45, L47, N47, P47, J47, P49, J49, P51, J51, P53, J53, J55, L55, M55, N55, N58, y el bloque inferior D69–D82.

**Salidas con rótulo de resultado**

| Celda | Rótulo | Fórmula original | `<v>` cacheado | Unidad del rótulo K o D |
|---|---|---|---|---|
| J12 | Caudal Actual= | `=C23*(C25/60)` | 4628 | bbl/dia |
| J17 | Qmax= | `=C23/(1-(0.2*(C24/C8))-(0.8*((C24/C8)^2)))` | 8716.3160464102293 | bbl/dia |
| J23 | PIP= | `=J21-((C11-C29)*J9)` | 648.97811883459508 | psi |
| J25 | Sumergencia= | `=(J23-C30)/J9` | 1538.8079006139542 | ft |
| J27 | Nivel de Fluido Dimanico= | `=C13-J25` | 1080.7720993860457 | pies |
| J55 | Potencia Real= | `=J45-(J47+J49+J51+J53)` | 69.053837905371324 | hp |
| J58 | PIP inferido= | `=+(L41-L55)*0.433` | 670.78075548892048 | psi |
| J60 | Sumergencia inferida= | `=((J58-1)/J9)` | 1588.3782921770237 | ft |
| J62 | Nivel de fluido dinamico inferido= | `=C13-J60` | 1031.2017078229762 | ft |
| J64 | Pwf inferido= | `=J58+((C11-C29)*J9)` | 757.22430332099202 | psi |

N58 no tiene rótulo. Fórmula `=J41-(((J55*13600*J9)/J12))`, cache 1423.351245356323. No es la misma expresión que J58.

Identidad algebraica de las fórmulas de potencia, confirmada también por los `<v>`: `J55` es igual a `P53`. Las «pérdidas» J47, J49, J51 y J53 son diferencias sucesivas que, restadas de J45, devuelven P53. La fuente no lo dice en un texto; sale de las fórmulas escritas.

La velocidad y la fricción (J29 en adelante) usan **C23 Q Prueba**, no J12 caudal actual. El PIP inferido usa J12 dentro de L55. Hay dos caudales en la misma cadena.

El caso numérico no es el mismo en todas las hojas que dicen 232HST o GN4000. Perforados: Metodo Ordenado 2601.7453 pies, Prueba Sesnorless 2862.6 pies. Q prueba: METODO 5215.67 BPD, Ordenado y Prueba 4272 BPD. Pwf prueba: 774.09 psi frente a 765 psi. Sumergencia escrita: 1574 pies frente a 1553 pies. IP escrito: 15.8 frente a 12.04. Reservorio: rótulo `Pr` en Hoja1, METODO y Metodo Ordenado; rótulo `Py` en Prueba Sesnorless.

---

## 4. Catálogo de ecuaciones

Leyenda común: si la fuente no define una variable, el significado es «significado no definido en la fuente». Si no declara unidad, «unidad no declarada». Si no hay dominio, «no declarado». Si no hay número de prueba, «no hay ejemplo numérico en la fuente». Implementable significa que la expresión, tal como está escrita, puede codificarse cuando existan los datos que la propia expresión nombra. No se afirma que algún Excel de pozos los contenga.

### 4.1 DOCX — nomenclatura escrita (sección 3)

Tabla única del documento. Texto original de las celdas:

| Símbolo | Descripción | Unidad SI | Comentario |
|---|---|---|---|
| P_in | Potencia real de entrada (VFD) | W | Convertir de kW a W |
| N | Velocidad | rpm | Si solo hay Hz: N = 120·f/p |
| f | Frecuencia | Hz | Usar si no hay rpm |
| Q | Caudal | m³/s | Estado a resolver |
| H | Head efectivo | m | Incluye correcciones |
| ΔP_pump | Diferencial de presión bomba | Pa | ΔP = ρ·g·H |
| THP | Presión de cabeza de tubing | Pa | Ancla de superficie |
| PIP | Presión de admisión de bomba | Pa | Salida principal |
| Δz | Elevación entre bomba y superficie | m | Signo positivo hacia arriba |
| η_p | Eficiencia hidráulica (bomba) | - | Dependiente de Q y N |
| η_em | Eficiencia eléctrica total | - | Motor + drive |
| k_f | Coef. fricción lumped | Pa·s²/m⁶ | En ΔP_tub = k_f·Q² |
| k_g | Interferencia de gas (0–0.4) | - | Reduce H y η |

Símbolos que las ecuaciones usan y **esta tabla no define**: p, No, N₀, λ, Q*, Ho, H₀, ηo, η₀, C_H, C_η, β, η_shift, ρ, g, a0, a1, a2, P_hyd, P_loss, ΔP_tub, Q_min, Q_max, w_k, FFT. g sí está en el texto de la sección 2.2: «fixed at the standard value of 9.80665 m/s²».

La sección 2.1 declara otras unidades para las mismas magnitudes, antes de la tabla SI:

- P_in en kilowatts (kW); la tabla pide W y comenta «Convertir de kW a W».
- N en rpm o f en Hz.
- I en amperes (A), V en volts (V), PF sin unidad declarada más allá del nombre power factor. El texto los marca optional.
- THP o CHP en psia o kPa; la tabla fija THP en Pa y no incluye el símbolo CHP.
- Δz en m.
- D, L en m; A en m².
- ρ en kg/m³.

No hay ejemplo numérico en ninguna sección del DOCX.

### 4.2 DOCX — modelo algebraico (sección 4)

El párrafo de apertura de la sección 4 dice: el modelo resuelve Q a partir de P_in y N, luego calcula PIP con balance hacia THP, con búsqueda 1D (bisección/Newton).

#### EQ-DOCX-01

- Fuente: sección 4.1, y también el comentario de la tabla para N. Texto: `N = 120·f / p`.
- Variables: N velocidad, rpm en la tabla; f frecuencia, Hz; p significado no definido en la fuente.
- Unidades: N y f como la tabla; p unidad no declarada.
- Entradas: f y p, solo si no hay rpm.
- Supuesto explícito: «si aplica».
- Dominio: no declarado.
- Implementable si se reciben f y p, o si N llega ya en rpm y esta ecuación no se usa.
- Ejemplo: no hay ejemplo numérico en la fuente.
- Diferencia: el XLSM no usa esta relación. Escala caudal con Hz/60 (EQ-XLSM-Prueba-J12) y no calcula rpm.

#### EQ-DOCX-02

- Fuente: sección 4.2. Texto de definición: `λ = N / No`. El párrafo previo escribe `λ = N / No` y `Q* = Q / λ`. La sección 2.2 escribe la referencia como `N₀`.
- No y N₀: la sección 2.2 los llama reference rotational speed. La sección 4 no vuelve a definir No. Unidad de No: no declarada en la sección 4; la tabla da N en rpm.
- λ: significado no definido con palabras; la ecuación es el cociente. Unidad no declarada.
- Supuesto: hay una velocidad de referencia de las curvas de fabricante.
- Dominio: no declarado. No se dice qué ocurre si No = 0.
- Implementable solo con N y No numéricos.
- Ejemplo: no hay.

#### EQ-DOCX-03

- Fuente: sección 4.2. `Q* = Q / λ`.
- Q caudal, m³/s en la tabla. Q* llamado «caudal equivalente». Unidad de Q* no declarada aparte de la de Q.
- Depende de EQ-DOCX-02.
- Dominio: no declarado.
- Ejemplo: no hay.

#### EQ-DOCX-04

- Fuente: sección 4.2. `H_ideal(Q,N) = λ² · Ho(Q*)`.
- Ho: en la sección 2.2, hydraulic head characteristic curve H₀(Q) del fabricante, función de Q a N₀, a convertir en polinomio. Coeficientes del polinomio: no están en el DOCX.
- H_ideal unidad no declarada en la ecuación; la tabla da H en m.
- Supuesto explícito de la sección 4.2: escalamiento de curvas por afinidad.
- Dominio de Q respecto de la curva: no declarado.
- Implementable solo con la curva o el polinomio Ho. **PENDIENTE: la curva no está en el DOCX ni en el XLSM.**
- Ejemplo: no hay.

#### EQ-DOCX-05

- Fuente: sección 4.2. `η_p,base(Q,N) = ηo(Q*)`.
- ηo: sección 2.2, operational efficiency characteristic curve η₀(Q). Coeficientes no están.
- Unidad: la tabla marca η_p como `-`.
- Mismo bloqueo de curva que EQ-DOCX-04.
- Ejemplo: no hay.

#### EQ-DOCX-06

- Fuente: sección 4.3. `H(Q,N)    = H_ideal(Q,N) · C_H(k_g)`.
- C_H significado no definido salvo por EQ-DOCX-08, que el texto llama «Ejemplo mínimo».
- k_g: tabla, interferencia de gas, rango escrito 0–0.4, unidad `-`, «Reduce H y η».
- Supuesto de la sección 4.3: correcciones multiplicativas simples, calibrables por pozo; pocas perillas.
- Dominio de k_g en esta línea: no declarado; sí en el ejemplo EQ-DOCX-08.
- Ejemplo: no hay valor numérico de H.

#### EQ-DOCX-07

- Fuente: sección 4.3. `η_p(Q,N) = η_p,base(Q,N) · C_η(k_g) · η_shift`.
- η_shift: significado no definido en la fuente. Aparece otra vez como componente del estado en la sección 5.1. Unidad no declarada.
- C_η: solo el ejemplo EQ-DOCX-09.
- Las reivindicaciones **omiten** η_shift. Ver sección 5 de estas notas.

#### EQ-DOCX-08

- Fuente: sección 4.3, «Ejemplo mínimo». `C_H(k_g) = 1 - k_g   (0 ≤ k_g ≤ 0.4)`.
- Dominio escrito: 0 ≤ k_g ≤ 0.4. Coincide con el rango de la tabla.
- El texto lo presenta como ejemplo mínimo, no como única forma permitida.
- Ejemplo numérico de un pozo: no hay.

#### EQ-DOCX-09

- Fuente: sección 4.3, ejemplo mínimo. `C_η(k_g)  = 1 - β·k_g   (β ≈ 1)`.
- β: significado no definido. El símbolo `≈` es del texto. Unidad no declarada.
- Dominio de β: no declarado. El de k_g no se repite en esta línea.

#### EQ-DOCX-10

- Fuente: sección 4.4. `ΔP_pump = ρ·g·H(Q,N)`.
- La tabla ya escribe `ΔP = ρ·g·H` y unidad Pa.
- ρ: sección 2.2, effective mixture density, kg/m³, promedio ponderado de crudo, agua de formación y gas libre. No hay valor.
- g: 9.80665 m/s² en la sección 2.2.
- H sale de EQ-DOCX-06, en m según la tabla.
- Supuesto: el texto de 4.4 no añade otro; el de 2.2 fija g.
- Implementable si ρ, g y H están en esas unidades. **PENDIENTE ρ numérico.**
- Ejemplo: no hay.

#### EQ-DOCX-11

- Fuente: sección 4.4. `P_hyd      = ρ·g·Q·H(Q,N)`.
- P_hyd: significado no definido con palabras en una fila de la tabla. La sección 4.5 lo usa como potencia hidráulica. Unidad no declarada en la ecuación. Con las unidades de la tabla (kg/m³, m/s², m³/s, m) la fuente no escribe el nombre del resultado.
- Ejemplo: no hay.

#### EQ-DOCX-12

- Fuente: sección 4.5, llamada «ecuación clave» en el título. `P_in,pred(Q,N) = P_hyd / (η_p(Q,N)·η_em) + P_loss(N)`.
- Texto previo: la potencia de entrada se modela como potencia hidráulica ajustada por eficiencias, más pérdidas no hidráulicas.
- η_em: tabla, eficiencia eléctrica total, motor + drive, unidad `-`. Sección 2.3: convierte P_in de superficie en potencia mecánica neta al impulsor; incluye pérdidas resistivas, fricción de rodamientos y distorsión del VFD. Valor numérico: no está.
- P_loss(N): sección 2.3, polinomio calibrable de pérdidas no hidráulicas (rodamientos, sello, residuales eléctricas no cubiertas por η_em). Forma en EQ-DOCX-13.
- P_in en la tabla está en W. La sección 2.1 habla de kW medidos, con preferencia del valor medido sobre el setpoint.
- Dominio: no se dice qué hacer si la eficiencia es cero.
- Implementable como función de Q solo con curva, η_em, P_loss y ρ. Varios de esos datos no están. **PENDIENTE.**
- Ejemplo: no hay.

#### EQ-DOCX-13

- Fuente: sección 4.5. `P_loss(N) = a0 + a1·N + a2·N²`. El texto dice «Forma típica».
- a0, a1, a2: significado no definido más allá de coeficientes de esa forma. Unidades no declaradas.
- Reivindicaciones: `Ploss(N)=a0+a1 .N+a2. N^2 o por Darcy-Weisback`. La nota de la sección 8 escribe `Darcy–Weisbach` para sustituir `k_f·Q²`, no para P_loss. Hay dos grafías y dos sitios distintos. PENDIENTE.
- Ejemplo: no hay coeficientes.

#### EQ-DOCX-14

- Fuente: sección 4.6. `ΔP_tub(Q) = k_f · Q²`.
- Texto: «Para MVP, se usa un modelo cuadrático en caudal».
- k_f unidad en tabla: Pa·s²/m⁶. Sección 2.3 lo llama lumped tubing friction loss coefficient y nombra la pérdida total como FFT, asociada a `k_f·Q²`. FFT no vuelve a aparecer en las ecuaciones numeradas.
- Supuesto: modelo lumped, no perfil distribuido (sección 2.3). La sección 8 dice que, si se requiere más fidelidad, se puede reemplazar `k_f·Q²` por Darcy–Weisbach.
- Dominio: no declarado.
- **PENDIENTE valor de k_f.** El XLSM no usa k_f; usa Darcy escrito con `f = 64/Re`.
- Ejemplo: no hay.

#### EQ-DOCX-15

- Fuente: sección 4.7 y resumen sección 8, punto 5. `PIP = THP + ρ·g·Δz + ΔP_tub(Q) - ΔP_pump(Q,N)`.
- Texto: balance desde la bomba hasta superficie, con THP medido.
- Δz: elevación bomba–superficie, m, signo positivo hacia arriba (tabla y sección 2.2).
- THP: ancla de superficie. Sección 2.1 admite THP o CHP; la ecuación solo escribe THP.
- Salida principal según la tabla.
- Guardrail de la sección 7, no como dominio de la ecuación: «PIP ≥ 0» en las reivindicaciones; la sección 6 dice «PIP no debe ser negativa».
- Implementable cuando existan THP, ρ, Δz, Q, H, k_f. **PENDIENTE esos datos en esta fuente.**
- Ejemplo: no hay.
- Reivindicación, grafía distinta y sin símbolos griegos: `PIP=THP+ rho . g .Delta z + Delta Ptub.(Q) - Delta Ppump.(Q,N)`.

#### EQ-DOCX-16

- Fuente: sección 4.8. `F(Q) = P_in - P_in,pred(Q,N) = 0`.
- Método escrito: bisección en `[Q_min, Q_max]`. Newton se menciona como alternativa en las reivindicaciones. Q_min y Q_max: significado no definido con números. Dominio: «rango físico», sin cifras.
- Después de obtener Q, PIP con la ecuación 4.7.
- No es una fórmula del XLSM. El XLSM no iguala una potencia predicha a una potencia medida mediante búsqueda de Q.
- Ejemplo: no hay.

### 4.3 DOCX — observador (sección 5)

El texto lo recomienda para transitorios y adaptación. No sustituye, en el propio documento, al MVP de la sección 4: lo presenta como versión robusta.

#### EQ-DOCX-17

- `x = [ Q, PIP, k_f, k_g, η_shift ]ᵀ`
- Estados. Unidades: las de cada símbolo cuando la tabla las tiene; η_shift unidad no declarada.
- No hay valores iniciales.

#### EQ-DOCX-18

- `x_{k+1} = x_k + w_k`
- w_k: «variaciones lentas (cambios de fluido, desgaste, etc.)». Covarianza, distribución y magnitud: no declaradas.
- Dinámica llamada random-walk en el título 5.2.

#### EQ-DOCX-19

- `y = [ P_in, THP ]ᵀ`
- «Vector de mediciones mínimo recomendado».

#### EQ-DOCX-20

- `P_in,hat = (ρ·g·Q·H(Q,N,k_g)) / (η_p(Q,N,k_g)·η_em) + P_loss(N)`
- Misma estructura que EQ-DOCX-12, con H y η_p escritos como funciones también de k_g, y notación hat en lugar de pred.
- Ejemplo: no hay.

#### EQ-DOCX-21

- `THP_hat = (PIP + ρ·g·H(Q,N,k_g)) - ρ·g·Δz - k_f·Q²`
- Si se despeja PIP, la expresión escrita coincide con EQ-DOCX-15 cuando ΔP_pump = ρ·g·H y ΔP_tub = k_f·Q². Es una lectura algebraica de los dos textos, no una frase del DOCX.
- Ejemplo: no hay.

La sección 6 recomienda calibrar con pozos que tengan PIP gauge, ajustar k_f para que THP_hat siga a THP, y ajustar k_g con eventos de gas. No da algoritmo ni cifras.

Sección 7, guardrails escritos, sin umbral numérico de confianza: unidades internas SI; filtro de media móvil o exponencial sobre P_in; histéresis de setpoints; confidence score si P_in y P_in,pred se separan; límites a Q, k_g y η_shift. El score no tiene fórmula. PENDIENTE.

### 4.4 XLSM — fórmulas, celda por celda

Los dibujos se citan cuando aportan una frase que la celda no tiene. La fórmula que manda para «qué calcula el libro» es la de la celda. Donde dibujo y celda discrepan, queda PENDIENTE.

Constantes que entran en fórmulas y **no tienen celda de nombre ni unidad**: 3.1416, 32.2, 24, 3600, 0.00067197 (además de C7), 62.4 (además de C5), 0.0005, 0.25 dentro de C16, 0.803, 2.31, 1000, 1.91, 63, 1360, 2895, 0.04, 0.96, 1.8, 0.2, 0.8, 0.00000184, 0.3048, 950, 4268, 60, 0.746, 745.69, 2400, 10, 4, 136000, 13600, 84, 1 (en J60). Significado no definido en la fuente, salvo cuando un dibujo nombra el conjunto de la expresión.

#### Cadena común de fluido (Hoja1, METODO, Metodo Ordenado, Prueba Sesnorless)

**EQ-XLSM-Hoja1-J4** `=141.5/(131.5+C3)`. Rótulo `Gavedad Especifica Crudo =` (grafía de la fuente). Dibujo 1: `γ_O=141.5/(131.5+°API)`. C3 es API en °. Unidad del resultado: no declarada. Cache Hoja1: 0.95932203389830506. La misma fórmula está en METODO J4, Metodo Ordenado J4 y Prueba J4, con API 13.8 y cache 0.97384721266345486. Implementable con API. El DOCX no trae esta ecuación.

**EQ-XLSM-Hoja1-J7** `=J4*62.4`. Rótulo `Densidad Crudo=`. Unidad escrita al lado: `lb/pie³`. El 62.4 es literal; C5 también vale 62.4 y no se cita. Dibujo: `ρ_o=γ_o*62.4`. Cache Hoja1: 59.861694915254233. Misma fórmula en las cuatro hojas de cálculo de fluido. Prueba y METODO cache: 60.768066070199581.

**EQ-XLSM-Hoja1-J9** `=J4*C6`. Rótulo en Hoja1: `Gradiente Crudo=`. En las otras tres hojas de fluido: `Gradiente Fluido=`. Unidad escrita del resultado: `psi/pie`. C6 está rotulado `Gradiente del agua` con unidad **psi/pie³**. El dibujo escribe `Gradiente del fluido=γ_o*0.433 psi/pie`. PENDIENTE: la unidad de C6 y la del resultado no son la misma cadena de texto. Cache Hoja1: 0.4153864406779661. Cache de las otras: 0.42167584308327594.

**EQ-XLSM-Hoja1-J11** `=C4*0.00067197`. Rótulo `µo en lbm/pie-seg=`. Unidad escrita: `lbm/pie-seg`. C4 en cps. C7 tiene el factor 6.7197e-4 y no se cita. En Prueba Sesnorless la celda es **Q11**, misma fórmula. Dibujo: conversión de µo de cps a lbm/pie-seg, sin escribir el número 0.00067197 en el texto recuperado. Cache Hoja1: 3.35985e-3. Cache METODO / Ordenado / Prueba: 0.24661299.

**EQ-XLSM-Hoja1-J33** `=C12*J9`. Rótulo `PIP=`. Unidad `psi`. Dibujo 1: `PIP=Sumergencia*Gradiente Fluido`. Entradas: sumergencia C12 y gradiente J9. No usa THP ni potencia. Cache Hoja1: 415.38644067796611. METODO J33 cache: 663.71777701307633. **Metodo Ordenado y Prueba Sesnorless no usan esta fórmula para su PIP principal.** Diferencia con EQ-DOCX-15: aquí PIP no resta el ΔP de la bomba ni suma fricción y columna desde THP.

**EQ-XLSM-Hoja1-J13** `=J33+((C11-C13)*J9)`. Rótulo `Pwf=`, unidad psi. Dibujo: `Pwf=PIP+((PMP−Prof_Intake)*Gradiente del fluido)`. La celda usa C11, rotulada `Profundidad de los perforados`, no un símbolo PMP. PMP: significado no definido en la fuente. PENDIENTE si PMP y C11 son el mismo dato. METODO J13 es la misma fórmula (cache 656.19731485443913). En Prueba Sesnorless el despeje está invertido en J23 y el Pwf de partida es el número escrito J21, no esta suma. El paper define PWF como presión de fondo fluyente; el XLSM no desarrolla la sigla.

**EQ-XLSM-Hoja1-J15** `=C9*(C8-J13)`. Rótulo `Caudal  Q=`, unidad BPD. Dibujo: `Q=IP*(Pr-Pwf)`. IP unidad escrita BPD/psi. Pr en psi. Cache Hoja1: 1753.8406779661018. METODO J15 cache: 7327.1344252998633, pero la velocidad de METODO **no** usa J15. El DOCX trata Q como incógnita de la potencia, no como IP*(Pr−Pwf).

**EQ-XLSM-METODO-J2** `=C23/(C8-C24)`. Rótulo `IP=`. C23 Q prueba, C8 Pr, C24 Pwf prueba. Dibujo 3: `IP=Q/(P_r−Pwf)`. Cache METODO: 15.080728639583633, mientras C9 escrito es 15.8. Cache Metodo Ordenado J2: 12.035837042880486, y C9 escrito es 12.04. Prueba Sesnorless no calcula este IP; lo escribe en C9 y deja otro número en N19. PENDIENTE cuál IP entra en un cálculo posterior: en estas hojas el Q de la prueba es dato, y este IP es resultado, no entrada de la cadena de PIP.

**EQ-XLSM-Hoja1-J17** `=(J15*5.615*(1/(24*3600)))/((3.1416*(C20^2))/4)`. Rótulo `Velocidad=`, unidad `pie/seg`. Dibujo: `V=Q/A` y `A=π(D^2)/4`. El 5.615 también está en C19 (`pc/B`) y la fórmula no cita C19. π escrito como 3.1416. Diámetro: C20, no C15. Cache Hoja1: 2.3219627193455707.

**EQ-XLSM-METODO-J17** misma estructura con **C23** en lugar de J15. Cache 6.9051832635411072. Metodo Ordenado: **J20** `=(C23*5.615*(1/(24*3600)))/((3.1416*(C20^2))/4)`, cache 5.6558300087711855. Prueba: **J29** igual que Ordenado, mismo cache, aunque ya existe un caudal actual J12 distinto de C23. PENDIENTE: la fricción no ve el caudal escalado por frecuencia.

**EQ-XLSM-Hoja1-J19** `=(C20*J17*J7)/J11`. Rótulo `Numero de Reynolds=`. Dibujo: `N_Re=dVρ_o/µ_o`. Unidad del resultado: no declarada. Cache Hoja1: 10342.472425112626. METODO J19 cache 425.37766642554226. Ordenado J22 cache 348.41418091442068. Prueba J31 igual que Ordenado, usando Q11.

**EQ-XLSM-Hoja1-J21** `=64/J19`. Rótulo `factor de friccion=`. Dibujo: `f=64/N_Re`. Unidad no declarada. No usa la rugosidad. No cambia de expresión si Re > 2000. En Hoja1 el Re cacheado es 10342 y la misma hoja no escribe la tabla de régimen; las otras sí la escriben y aun así dejan `f=64/Re`. Cache Hoja1: 6.1880754784127993e-3. METODO J21 cache 0.15045453734746675. Ordenado J24 y Prueba J33 cache 0.18368942340989278. **PENDIENTE:** régimen y rugosidad no entran en la fórmula. El DOCX no usa Reynolds; usa k_f·Q².

**EQ-XLSM-Hoja1-C16** solo en METODO, Ordenado y Prueba: `=0.0005*0.25`. Rótulo `Rugosidad ɛ`. Unidad no declarada en esas hojas (en Hoja1 la rugosidad es el valor escrito 0.001 pulgadas, sin esta fórmula). El resultado no alimenta `f`. PENDIENTE.

**EQ-XLSM-Hoja1-J23** `=((J21*J7*(J17^2))/(2*32.2*C20))/144`. Rótulo `(ΔP/ΔL)friccion=`, unidad `psi/pie`. Dibujo: `friccion=(f*ρ*V^2/(2*g*d))/144`, fragmentado en el XML; el 32.2 no aparece nombrado como g. C21 vale 144 y esta fórmula no lo cita: el 144 es literal. Cache Hoja1: 8.6144336150097622e-4. METODO J23 cache 0.18803675816368037. Ordenado J26 y Prueba J35 cache 0.15401530980204703.

**EQ-XLSM-Hoja1-J25** `=J7/C21`. Rótulo `(ΔP/ΔL)gravedad=`, unidad psi/pie. C21 = 144, unidad escrita lb/ft². Cache Hoja1: 0.4157062146892655. Las otras hojas cachean 0.42200045882083043. En Prueba la celda es J37.

**EQ-XLSM-Hoja1-J27** `=J25+J23`. Rótulo `(ΔP/ΔL)Total=`, psi/pie. Cache Hoja1: 0.41656765805076645. METODO J27 cache 0.61003721698451074. Ordenado J30 y Prueba J39 cache 0.57601576862287751.

**EQ-XLSM-Hoja1-J29** `=J27*C13`. Rótulo `ΔP Total=`, psi. Dibujo: el gradiente total por la profundidad de la bomba. C13 es profundidad ESP o intake, en pies. Cache Hoja1: 2499.4059483045985. METODO J29 cache 1598.0412928682847. Ordenado: la celda es **J32**, cache 1508.9193871691175. Prueba: la celda es **J41**, rótulo `TDH`, unidad escrita **psi**, misma fórmula `=J39*C13`, mismo cache 1508.9193871691175. PENDIENTE: el mismo producto se llama ΔP Total y también TDH, y la unidad escrita en Prueba es psi, mientras el PDF define TDH como altura.

**EQ-XLSM-Hoja1-J31** `=C22+J29`. Rótulo `Presion de Descarga=`, psi. C22 es THP. Dibujo: `P_d=THP+…`. Cache Hoja1: 2699.4059483045985. METODO J31 cache 1773.0412928682847. Ordenado J34 cache 1683.9193871691175. Prueba Sesnorless **no** suma THP a ese ΔP dentro de J41.

**EQ-XLSM-Hoja1-J35** `=J31-J33`. Rótulo `ΔP Bomba =`, psi. Cache Hoja1: 2284.0195076266323. METODO J35 cache 1109.3235158552084. No está en Ordenado ni en Prueba con esta forma. Diferencia con EQ-DOCX-10: aquí ΔP es descarga menos PIP, y PIP vino de la sumergencia; en el DOCX ΔP_pump = ρ·g·H y PIP se despeja del balance.

**EQ-XLSM-Hoja1-J37** `=J35/J9`. Rótulo `Head=`, unidad pies. Cache Hoja1: 5498.5413194971115. METODO cache 2630.7495059329976. Dibujo 3, otra expresión: `HEAD=P/(0.434*SG)`. El 0.434 no está en las celdas. PENDIENTE relación entre `/J9` y `/(0.434*SG)`.

**EQ-XLSM-Hoja1-J43** `=J37/J39`. Rótulo `Numero de Etapas=`. J39 = 54 pies, escrito, «de la curva de la bomba» según el texto de E39. Cache 101.82483924994651. METODO J43 cache 48.717583443203658. Unidad del resultado: no declarada. Dibujo: `# de etapas = HEAD / pies por etapa`.

**EQ-XLSM-Hoja1-J45** `=J41*J43*J4`. Rótulo `Potencia de la bomba=`, unidad HP. J41 = 1.4 HP escrito. Multiplica por la gravedad específica J4. Cache Hoja1: 136.7559366468773. METODO cache 66.420875981408415. El DOCX no calcula potencia de bomba como HP/etapa × etapas × SG.

**EQ-XLSM-METODO-Q37** `=(P41*P40)*J9`. Rótulo `ΔP ESP=`, psi. P41 head/etapa = 63, P40 etapas = 52, ambos escritos. Cache 1381.4100619408121. Dibujo 2: `ΔP_ESP=HEAD*Gradiente del fluido`.

**EQ-XLSM-METODO-Q33** `=J31-Q37`. Segundo `PIP=`, psi. Cache 391.63123092747264. Distinto del PIP J33 (663.717...). Dibujo: `PIP=P_(d ESP)−ΔP_ESP`, texto fragmentado. PENDIENTE cuál de los dos PIP es el de trabajo.

**EQ-XLSM-METODO-Q43** `=Q33/J9`. Rótulo `Sumergencia=`, pies. Cache 928.74950593299729. Dibujo: `Sumergencia=PIP/Gradiente de presion del fluido`. No resta presión de casing. En Prueba, la sumergencia no inferida sí resta C30.

**EQ-XLSM-METODO-Q45** `=C13-Q43`. Rótulo `Nivel de Fluido Dimanico=`, pies. Cache 1690.8304940670027. Dibujo: `NFD=Prof. Intake−Sumergencia`.

**EQ-XLSM-Ordenado-K13** `=J13*0.803`. J13 HEAD = 3276 escrito. Cache 2630.628. Sin unidad. PENDIENTE 0.803.

**EQ-XLSM-Ordenado-J17** `=+J13*J9`. Rótulo `ΔP ESP=`, psi. Usa el HEAD 3276, no el producto etapas×head/etapa por referencia de celdas. Cache 1381.4100619408121, igual al Q37 de METODO. 3276×J9 da ese cache; 63×52×J9 también, porque 63×52 = 3276.

**EQ-XLSM-Ordenado-J36** `=J34-J17`. Rótulo `PIP=`, psi. Cache 302.50932522830544. Es descarga menos ΔP ESP. No es el PIP de sumergencia.

**EQ-XLSM-Ordenado-J38** `=J36/J9`. `Sumergencia=`, pies. Cache 717.39780732130646.

**EQ-XLSM-Ordenado-J40** `=C13-J38`. `Nivel de Fluido Dimanico=`, pies. Cache 1902.1821926786934.

**EQ-XLSM-Ordenado-D34** `=(C22*2.31)/J4`. Rótulo `Altura Dinamica=`. Dibujo 3: `Altura Din=(THP*2.31)/SG_m`. Unidad del resultado: no declarada en la celda. 2.31: significado no definido; el dibujo no le pone unidad. Cache 415.10618374558305. La misma fórmula está en Prueba **D71**. THP entra aquí convertido a altura, no en el PIP de la columna J.

**EQ-XLSM-Ordenado-D36** `=J32/1000`. Rótulo `Pedida por friccion=` (grafía de la fuente). Dibujo: `Perd tot fricc=(perd ficc*Prof)/1000ft`. La celda divide el **ΔP total ya integrado en psi** entre 1000, no un gradiente por profundidad otra vez. Cache 1.5089193871691176. Unidad no declarada. Prueba **D73** `=J41/1000`, mismo cache. PENDIENTE: el dibujo y la celda no operan sobre la misma magnitud, y el resultado se suma después con alturas.

**EQ-XLSM-Ordenado-D38** `=C11-((C24*2.31)/J4)`. Rótulo `Lev Dinamico=`. Dibujo: `Lev Din=prof datum−(Pwf*2.31)/SG_m`. C11 es perforados; el dibujo dice prof datum. C24 es Pwf prueba. Cache 787.1382681978796. Prueba **D75** usa el C11 de esa hoja (2862.6) y cachea 1047.9929681978795.

**EQ-XLSM-Ordenado-D40** `=D38+D36+D34`. Rótulo `TDH=`. Dibujo: `TDH=Lev Din+Perd tot fricc+Altura Din`. Cache 1203.7533713306318. Unidad no declarada. Suma un término que salió de dividir psi entre 1000 con dos términos que el dibujo trata como alturas. PENDIENTE de unidades. Prueba **D77** cache 1464.6080713306314.

**EQ-XLSM-Ordenado-D42** `=1.91*63*J4`. Rótulo `HP=`. Cache 117.18303509979353. El 1.91 y el 63 son literales. H14 de esa hoja vale 63 (`# etapas`) y no está citado. Dibujo: `BHP=BHP∕〖Etapa(curva)*Etapas*SG_m〗`. La barra del dibujo no es un producto `1.91*63*SG`. PENDIENTE. Prueba **D79** es la misma fórmula y el mismo cache.

**EQ-XLSM-Ordenado-D32** `=((D40*C23*J7)/(1360*D42))`. Rótulo `Eff Bomba=`. Dibujo: `n=(TDH*Q_L*ρ_L)/(1360*BHP)`. Cache **1960.8326288066046**. El rótulo dice eficiencia y el número cacheado no viene acompañado de `%` ni de declaración de fracción. PENDIENTE. Prueba **D69** usa D77 en lugar de D40 y cachea 2385.7472494586341. El DOCX usa η entre 0 y 1 en el cociente de potencia, sin el 1360.

**EQ-XLSM-Ordenado-D46** `=(2895*C23*J7)/(1360*D42)`. Sin rótulo. Cache 4715.7587223371029. 2895 significado no definido. Prueba **D82** igual. PENDIENTE.

**EQ-XLSM-Ordenado-C48** `=C23*0.00000184`. Rótulo `Qprueba m³/s`. Cache 7.8604799999999996e-3. El factor no está justificado en una celda. Implementable como conversión escrita, con unidad del rótulo m³/s.

**EQ-XLSM-Ordenado-C49** `=J13*0.3048`. Rótulo `HEAD m`. Cache 998.52480000000003. 0.3048 significado no definido en la fuente. J13 no tiene unidad escrita.

**EQ-XLSM-Ordenado-C51** `=(C50*C48*C49*J4)/D42`. Rótulo `Eff Bomba`. C50 = 973.44 `densidad kg/m³`, escrito y no ligado a J7. Incluye otra vez J4 (gravedad específica). Cache 63.49553606767514. Unidad no declarada. Distinta de D32. PENDIENTE.

**EQ-XLSM-Ordenado-L54** `=C23/(1-(0.2*(C24/C8))-(0.8*((C24/C8)^2)))`. Rótulo `Qmax=`. Cache 8716.3160464102293. Unidad no declarada en L54. Prueba **J17** es la misma fórmula, unidad escrita `bbl/dia`, mismo cache. Dibujo 5: `Q_max=Q_prueba/(1−0.2*(Pwf_prueba/Py)−0.8*(Pwf_prueba/Py)^2)`. En Ordenado el reservorio está rotulado Pr, no Py. Los coeficientes 0.2 y 0.8 no tienen celda. La fuente **no** nombra una correlación. Dominio: no declarado; no se dice qué hacer si el denominador es cero o negativo.

**EQ-XLSM-Ordenado-L47** `=C23/(((0.04*((C8*((1-(0.2*(C24/C8)))-(0.8*((C24/C8)^2))))/1.8)))+(0.96*(C8-C24)))`. Rótulo `IP=`. Cache 12.104034442104341. Distinto del IP J2 (12.0358...) y del IP escrito C9 (12.04). Los factores 0.04, 0.96 y 1.8 no citan el BSW de C10 (96.6 %). PENDIENTE. No está en el DOCX.

#### Hoja2 — cuadrática

**EQ-XLSM-Hoja2-B2** `=1/950`. Rótulo de columna `b`. Cache 1.0526315789473684e-3.

**EQ-XLSM-Hoja2-A2** `=B2^2`. Rótulo `a`. Cache 1.1080332409972298e-6.

**EQ-XLSM-Hoja2-C2** `=4268/4272`. Rótulo `c`. Cache 0.99906367041198507. 4272 coincide con el Q prueba de Metodo Ordenado y de Prueba; 4268 no aparece rotulado en otra hoja.

**EQ-XLSM-Hoja2-A3** `=-0.8*A2`. **EQ-XLSM-Hoja2-B3** `=-0.2*B2`. **EQ-XLSM-Hoja2-C3** `=1-C2`.

**EQ-XLSM-Hoja2-B6** `=((-B3)+(((B3^2)-(4*A3*C3))^(1/2)))/(2*A3)`. Cache −241.86725840222132.

**EQ-XLSM-Hoja2-B7** `=((-B3)-(((B3^2)-(4*A3*C3))^(1/2)))/(2*A3)`. Cache 4.367258402221327.

Sin rótulo de incógnita ni unidad. Dibujo 4, texto distinto: `Potencia=(Voltaje_motor*Corriente_motor)/10000*Eff_motor*factor potencia_motor` y `Q_2/Q_max=1−0.2*(Pwf/950)−0.8*(Pwf/950)^2`. El 950 del dibujo es el denominador de esa expresión de Q; en la hoja es `1/950`. PENDIENTE. Esta potencia del dibujo 4 **no** es la fórmula de Prueba Sesnorless (allí hay √3, 0.8 y /1000, no /10000).

#### Prueba Sesnorless — cadena eléctrica y PIP inferido

**EQ-XLSM-Prueba-J12** `=C23*(C25/60)`. `Caudal Actual=`, bbl/dia. Cache 4628. Dibujo: `Q_2=Q_1*Hz_2/Hz_1`. C37 (`Hz 1` = 60) y C36 (`Hz 2` = 65) no se citan; el 60 es literal y la frecuencia usada es C25. C26 `=J12` repite el valor con rótulo `Qactual` y unidad BPD. El DOCX escala la curva con λ = N/No, no el caudal de prueba con Hz/60.

**EQ-XLSM-Prueba-J23** `=J21-((C11-C29)*J9)`. `PIP=`, psi. Cache 648.97811883459508. J21 es Pwf escrito. C29 profundidad del sensor. Dibujo: `PIP=Pwf−(PMP−P_Sensor)*Gradiente del fluido`. Coincide en el signo con la celda si PMP es C11. Este PIP no es el inferido.

**EQ-XLSM-Prueba-J25** `=(J23-C30)/J9`. `Sumergencia=`, ft. Resta presión de casing C30. Cache 1538.8079006139542. Dibujo de la sumergencia no inferida: `((PIP−Presion Casing))/Gradiente del fluido`.

**EQ-XLSM-Prueba-J27** `=C13-J25`. `Nivel de Fluido Dimanico=`, pies. Cache 1080.7720993860457.

**EQ-XLSM-Prueba-L41** `=J41/J9`. Sin rótulo propio; J41 está rotulado TDH en psi. Cache 3578.3870760439172. Unidad escrita en M41: `ft`.

**EQ-XLSM-Prueba-N41** `=L41/64`. Sin rótulo. Cache 55.912298063186206. 64 significado no definido. PENDIENTE.

**EQ-XLSM-Prueba-L45** `=(C32*C31*SQRT(3)*0.8)/1000`. Sin rótulo en L45. Unidad escrita en M45: `vatio`. Cache 119.75364642515066. El 0.8 no tiene celda; el dibujo lo llama en la expresión vecina «Factor de potencia», sin escribir 0.8. SQRT(3) no está nombrado. PENDIENTE la unidad: el rótulo dice vatio y la fórmula divide entre 1000. El DOCX pide P_in en W, medido, no V·I·√3·0.8/1000.

**EQ-XLSM-Prueba-J45** `=L45/0.746`. `Potencia variador=`, unidad escrita hp. Cache 160.52767617312421. 0.746 significado no definido. Dibujo: `Potencia Variador=Voltaje*Corriente*√3*Factor de potencia`, sin el /1000 ni el /0.746.

**EQ-XLSM-Prueba-L47** `=2400*(10/1000)`. Unidad escrita en M47: `Votios` (grafía de la fuente). Cache 24. 2400 y 10 no tienen rótulo de celda. Dibujo: `(10 voltios/1000 ft)*#ft cable`. El dibujo declara esas unidades; la celda no identifica 2400 con ninguna profundidad de la hoja (intake 2619.58, sensor 2657.6, perforados 2862.6, casing 3779). PENDIENTE la longitud de cable.

**EQ-XLSM-Prueba-N47** `=((C32-L47)*C31)*(3^(1/2))*0.8`. Unidad escrita `vatios`. Cache 118691.13717775559. No divide entre 1000. No es la misma escala que L45.

**EQ-XLSM-Prueba-P47** `=N47/745.69`. Unidad escrita hp. Cache 159.16954388251898. 745.69 significado no definido. Distinto del 0.746 de J45. PENDIENTE.

**EQ-XLSM-Prueba-J47** `=J45-P47`. `Perdida del cable=`, hp. Cache 1.3581322906052264.

**EQ-XLSM-Prueba-P49** `=P47*C33`. hp. Cache 119.37715791188924. C33 Eff Motor = 0.75.

**EQ-XLSM-Prueba-J49** `=P47-P49`. Rótulo `Perdida Motor=`, hp. Cache 39.792385970629738. El dibujo dice `Perdida motor=perdida cable*eff motor`, que es la estructura de **P49**, no la de J49. PENDIENTE: el rótulo «pérdida» y el producto por eficiencia no nombran la misma celda.

**EQ-XLSM-Prueba-P51** `=P49-(4*C34)`. hp. Cache 111.37715791188924. El 4 no tiene unidad declarada. C34 = 2 sellos.

**EQ-XLSM-Prueba-J51** `=P49-P51`. `Perdida Sello=`, hp. Cache 8, que es 4×2. Dibujo: `Perdida Sello=perdida motor−(4*#sellos)`. Encaja con J51 si «perdida motor» del dibujo es P49.

**EQ-XLSM-Prueba-P53** `=P51*C35`. hp. Cache 69.053837905371324. C35 = 0.62.

**EQ-XLSM-Prueba-J53** `=P51-P53`. `Perdida Bomba=`, hp. Cache 42.323320006517918. Dibujo: `Perdida en la bomba=perdida sello*eff bomba`, que es la estructura de **P53**, no la de J53. Misma ambigüedad que en el motor.

**EQ-XLSM-Prueba-J55** `=J45-(J47+J49+J51+J53)`. `Potencia Real=`, hp. Cache 69.053837905371324, igual a P53. Dibujo: `Potencia Real=Potencia Variador−ΣPerdidas`. Si las pérdidas son J47+J49+J51+J53, la celda cumple esa frase y el resultado es P53.

**EQ-XLSM-Prueba-L55** `=P53*136000/J12`. Sin rótulo. Cache 2029.2398347300132. 136000 significado no definido en la celda. Unidad no declarada.

**EQ-XLSM-Prueba-M55** `=L55*0.433`. Sin rótulo. Cache 878.66084843809574. Usa el literal 0.433, no C6 ni J9. Unidad no declarada.

**EQ-XLSM-Prueba-N55** `=84/63`. Sin rótulo. Cache 1.3333333333333333. 84 y 63 significado no definido. PENDIENTE.

**EQ-XLSM-Prueba-J58** `=+(L41-L55)*0.433`. `PIP inferido=`, psi. Cache 670.78075548892048. Sustituyendo celdas: `(J41/J9 − P53*136000/J12)*0.433`. El 0.433 no es J9 (J9 cache 0.42167584308327594).

Dibujo 5, texto recuperado del XML: `〖PIP〗_i=(TDH−(((Potencia Real*136000*Gradiente del fluido)/Caudal actual))`. Lleva 136000 y el gradiente **dentro** del término restado, y no muestra un `*0.433` fuera. Evaluar esa forma con los `<v>` de la hoja no reproduce J58:

- Sobre L41 (ft): 2722.705...
- Sobre J41 (psi): 653.237...
- J58 cacheado: 670.780...

**EQ-XLSM-Prueba-N58** `=J41-(((J55*13600*J9)/J12))`. Sin rótulo. Cache 1423.351245356323. Usa **13600**, no 136000, y el gradiente J9. No coincide con J58 ni con el dibujo.

PENDIENTE bloqueante: hay tres expresiones de «PIP» asociadas a la potencia (dibujo, J58, N58) y además el PIP J23 que parte de un Pwf escrito. No se elige una.

**EQ-XLSM-Prueba-J60** `=((J58-1)/J9)`. `Sumergencia inferida=`, ft. Cache 1588.3782921770237. El 1 es literal. C30 presión de casing es 0.1 y no se cita. El dibujo de la sumergencia inferida dice `((PIP_i−Presion Casing))/Gradiente del fluido`. PENDIENTE.

**EQ-XLSM-Prueba-J62** `=C13-J60`. `Nivel de fluido dinamico inferido=`, ft. Cache 1031.2017078229762.

**EQ-XLSM-Prueba-J64** `=J58+((C11-C29)*J9)`. `Pwf inferido=`, psi. Cache 757.22430332099202. Signo **más**. El dibujo dice `Pwf_i=PIP_i−(PMP−P_Sensor)*Gradiente del fluido`, signo **menos**. J23, el PIP no inferido, sí usa el signo menos. PENDIENTE el signo de Pwf inferido. El paper no trae esta ecuación.

El bloque D69–D82 repite la cadena TDH/HP de Metodo Ordenado sobre los datos de esta hoja. No alimenta J58. Queda como cálculo paralelo, no como entrada del PIP inferido.

---

## 5. Comparación DOCX vs XLSM

No son el mismo modelo. No se propone una fórmula fusionada.

| Pieza | DOCX | XLSM Prueba Sesnorless | Relación |
|---|---|---|---|
| Incógnita | Q, raíz de `P_in − P_in,pred(Q,N) = 0` | Q prueba es dato. Q actual = Q prueba × Hz/60 | Distintas |
| Curva de bomba | H₀(Q), η₀(Q), afinidad con λ² y Q/λ | No hay curva H(Q). Hay HEAD, etapas o HP/etapa escritos en otras hojas | El DOCX no se puede calcular con lo que hay en el XLSM |
| Potencia | Hidráulica ρ·g·Q·H dividida por η_p·η_em, más P_loss(N) | V·I·√3·0.8/1000, luego /0.746, menos una cadena de cable, motor, sello y bomba | Distintas. El XLSM no usa ρ·g·Q·H como potencia de entrada |
| Fricción | `k_f·Q²` en Pa, con k_f en Pa·s²/m⁶ | Darcy con `f=64/Re` y g escrito como 32.2, resultado en psi/pie | Distintas. k_f no aparece |
| Gas | k_g entre 0 y 0.4, corrige H y η | No aparece k_g | El XLSM no aplica esa corrección |
| PIP | `THP + ρ·g·Δz + ΔP_tub − ΔP_pump` | J58 = (L41 − L55)×0.433, con L55 = P53×136000/Q_actual | No son la misma expresión. THP no entra en J58 |
| THP | Ancla de superficie del balance | Entra en D71 `Altura Dinamica`, no en J58 | Uso distinto |
| Densidad y g | ρ en kg/m³ y g = 9.80665 m/s² | Gravedad específica API, 62.4 lb/pie³, gradiente 0.433, 32.2 en la fricción | Sistemas de unidades distintos, los dos escritos |
| Observador | EKF/UKF/MHE, estado con k_f, k_g, η_shift | No está | Solo DOCX |
| Ejemplo | No hay | Hay un caso cacheado 232HST / GN4000, con cifras que cambian entre hojas | El cache no es un ejemplo del DOCX |

Coincidencias de tema, no de ecuación: ambas fuentes hablan de PIP, THP, caudal, fricción en tubing, potencia eléctrica de superficie y eficiencia. El PDF y el XLSM comparten además la palabra TDH y un esquema de pérdidas de cable; el DOCX no usa la palabra TDH ni calcula caída de voltaje en el cable.

La hoja Hoja1 / METODO calcula PIP como sumergencia × gradiente, y el caudal como IP×(Pr−Pwf). Eso tampoco es EQ-DOCX-15.

Cadena de Prueba Sesnorless, en orden de dependencia, solo con rótulos de la hoja:

1. Entradas de fluido y de prueba: API, µo, gradiente del agua, Py, Q prueba, Pwf prueba, Hz, geometría usada (C20, C13, C11, C29), THP, voltaje, corriente, eficiencias, sellos, Pwf escrito en J21, presión de casing.
2. Intermediarios de fluido: SG, densidad, gradiente, viscosidad convertida, caudal actual, Qmax, velocidad desde Q prueba, Reynolds, f, gradientes, TDH en psi y en ft.
3. Intermediarios eléctricos: potencia de variador, caída de cable con 2400, potencia tras cable, tras motor, tras sellos, tras bomba, «potencia real» igual a esa última.
4. Salidas inferidas: PIP J58, sumergencia J60, nivel J62, Pwf J64.
5. Salidas paralelas, no inferidas: PIP J23, sumergencia J25, nivel J27, y el bloque TDH de las filas 69–82.

Para codificar el DOCX faltan, como mínimo: polinomio o tabla H₀(Q) y η₀(Q), N₀, ρ, Δz, k_f, k_g, β, η_shift, η_em, a0, a1, a2, Q_min, Q_max, y la convención de unidades kW→W y psia/kPa→Pa. La fuente no los numera.

Para codificar el XLSM como está, las fórmulas alcanzan, porque los literales ya están dentro. Eso no documenta qué son 136000, 13600, 0.433 frente a J9, 2400, 4, 0.8, 32.2 ni el signo de J64. Esas fórmulas quedan **PENDIENTE** de significado aunque sean ejecutables como aritmética.

---

## 6. Contexto PDF y paper

Esto es contexto. No son resultados de este proyecto. No se copia el artículo.

### 6.1 `004-ESPdesign.pdf`

Título visible: «ESP. Diseño básico y selección». Autor en el PDF: Marcelo Hirschfeldt, oilproduction.net. Seis páginas. El texto dice que el ejemplo es un pozo de la Cuenca del Golfo San Jorge, Patagonia Argentina. No es un pozo de las hojas XLSM.

Recorrido que el PDF enumera: datos del pozo, caudal máximo, TDH, selección de bomba, número de etapas, motor, cable, voltaje y potencia en superficie.

Datos del ejemplo, página 1, como están escritos: caudal bruto 80 m³/d; agua 95 %; ρ fluido (agua) 1.01 gr/cm³; nivel dinámico 700 mbbdp; nivel estático 440 mbbdp; presión de boca 10 kg/cm²; punzados 1750–1755 mbbdp; casing 5 ½" 15.5 #; tubing 2 7/8" 6.5 #. Define mbbdp como metros bajo boca de pozo. Supuesto escrito: fluido monofásico, y un nivel dinámico 200 m sobre el punzado. Caudal teórico declarado: 340 m³/d a ND = 1550 mbbdp. La página nombra el índice de productividad y no escribe una fórmula algebraica de IP en el texto extraído.

Página 2, ecuación corta recuperable: `TDH = Pbdp + Pcf + Nd [m o ft]`. Definiciones de la misma página: Pcf pérdida de carga por fricción en los tubings; Pbdp presión de boca de pozo; P.Nivel presión por la columna a elevar. Resultado declarado en prosa: Pcf ≅ 70 m, Pbdp = 100 m, P.Nivel = 1550 m, TDH = 70 m + 100 m + 1550 m = 1720 m.

La pérdida de fricción se atribuye a la ecuación de Hazen-Williams, «aplicable para agua a 20ºC». La composición es tipográfica. PyMuPDF no devuelve una línea única fiable: los tokens quedan en coordenadas separadas (entre ellos fragmentos de 2.083, 1.85, 4.8655, 100, C, Q, ID). Lo que sí está en prosa: F = pérdida de carga en ft/1000 ft; Q = caudal en bpd; C = 120; tubing 2 7/8" con ID = 2.441 pulg; 340 m³/d ≅ 2140 bpd; resultado 40.5 ft por cada 1000 ft, o 4.047 m por 100 m de tubing. **No se transcribe una fórmula lineal de Hazen-Williams** porque el orden no queda unívoco. PENDIENTE si el coordinador quiere una transcripción visual de esa página.

Página 3: la bomba se elige para que el caudal caiga en los límites de trabajo y cerca de la máxima eficiencia. No usa la sigla BEP. Modelo del ejemplo: DX-3000, serie 400, OD 4", 3000 BPD a 50 Hz, para casing 5 ½". El gráfico de Hazen-Williams rotula tres tubing: 2 3/8" OD (ID 1.995), 2 7/8" (ID 2.441), 3 ½" (ID 2.992). El 2.992 pulgadas es el mismo número que el DI escrito en el XLSM; el PDF no dice que sea el mismo pozo. PENDIENTE cualquier identificación.

Página 4: una etapa tiene tres curvas: BHP, head capacity y eficiencia. Para 340 m³/d el texto da elevación por etapa 4.4 m/etapa y 0.36 Hp/etapa, «ver gráfico».

Página 5: número de etapas = TDH / epe. Usa **1700 m**, no los 1720 m de la página 2. 1700/4.4 ≅ 386 etapas. Catálogo citado en el texto: 4 cuerpos de 96 etapas = 384. Potencia = 384 × 0.36 ≅ 138 Hp. Motores del ejemplo: dos serie 456, 50 Hz, 73 Hp, 1042 V, 44.5 A cada uno (UT y CT). Cable: caída inferior a aproximadamente 10 volt/100 m; para 44.5 A el texto elige cable #4. El «aproximadamente» es de la fuente.

Página 6: para 45 A, 21 volt/1000 ft, dicho también como 7 volt/100 m. A 1700 m: 1700 × 7 / 100 = 119 V. Voltaje total = 2×1042 + 119 = 2203 V. Ecuación corta: `KVA = (Volts x Amp x 1.732)/1000`, con el ejemplo (2203 × 45 × 1.732)/1000 = 171 KVA, y la sugerencia de un transformador de 180 KVA. Referencias nombradas: REDA, Centrilift, un catálogo ESP y el Petroleum Engineering Handbook de Bradley.

Conceptos que sí sirven de contexto para leer el XLSM, sin copiar el ejemplo como dato de pozo: TDH como suma de columna, fricción y presión de boca; etapas = TDH / elevación por etapa; potencia de motor = potencia por etapa × etapas; caída de voltaje en el cable; potencia trifásica con el factor 1.732. El PDF no define PIP, PWF ni un PIP sin sensor.

### 6.2 `paper_sensorless - v2.docx`

Título: SensorLess, implementación y validación de un algoritmo de aprendizaje automático para estimación virtual de presión de fondo en Caño Sur, Colombia. Autores y campaña son los del artículo. El plan `trabajo.md` dice que este proyecto no busca recrear ese algoritmo. Estas notas no lo recrean.

Única ecuación corta del paper, sección «Metodología de Validación»:

`ε (%) = |PIPSL − PIPref| / PIPref × 100`

ε está en la nomenclatura como desviación relativa absoluta, en %. PIPSL es la estimación SensorLess y PIPref la referencia, según la frase que introduce la fórmula. No es una ecuación de cálculo de PIP. No se adopta como métrica de este proyecto.

Arquitectura descrita, sección «Descripción de la tecnología», en cuatro pasos, parafraseada: entradas eléctricas en tiempo real (corriente, voltaje, frecuencia, potencia) más completación (profundidad de bomba, diámetros, geometría) y PVT (gravedad específica, viscosidad, GOR); paso físico con curvas de motor, curva H-Q-η y corrección de cable; luego un modelo supervisado por pozo, entrenado con DHS y Echometer, con actualización en línea; salidas PIP, PWF, DFL y sumergencia. Eso es un esquema híbrido. El DOCX algebraico no describe entrenamiento ni DHS. El XLSM no describe aprendizaje.

El artículo cita solicitudes de patente con los números que él mismo escribe (EE. UU. 63/827,610 para ESP y 19/253,095 para PCP). Es una cita del paper, no una verificación jurídica.

El paper reporta una campaña en Caño Sur y comparaciones contra sensor de fondo y prueba acústica. Esas cifras pertenecen al artículo. **No se copian aquí como resultados del proyecto VESP/ESP.** El coordinador no debe heredarlas en `docs/trazabilidad_ecuaciones.md` como exactitud del modelo determinístico.

Nomenclatura del paper, tabla final: PIP presión de entrada de la bomba, psi; PWF presión de fondo fluyente, psi; DFL nivel de fluido dinámico, ft; DHS sensor de fondo permanente; ECH prueba acústica Echometer; SL estimación SensorLess; VSD/VFD variador de velocidad / de frecuencia; ESP bomba electrosumergible; PCP bomba de cavidad progresiva; MIP/PMM motor de imanes permanentes; GOR relación gas-petróleo, pc/STB; ε desviación relativa absoluta, %; H-Q-η curva caudal-altura-eficiencia. La conclusión menciona «pozos BES» y no desarrolla BES.

Diferencia de fondo: el paper infiere con un modelo entrenado por pozo; el DOCX propone balance algebraico y, aparte, un observador; el XLSM es una cadena de celdas con constantes fijas y un caso numérico. Ninguno de los tres entrega la curva de la bomba GN4000.

---

## 7. Glosario preliminar

Solo definiciones halladas. Si la sigla no se desarrolla, se dice.

| Término | Qué dice la fuente | Dónde |
|---|---|---|
| PIP | Presión de admisión de bomba. También «pump intake pressure». Unidad de la tabla del DOCX: Pa. | DOCX, título, sección 2 y tabla de la sección 3 |
| PIP | Presión de entrada de la bomba. Unidad: psi. | Paper, nomenclatura |
| PIP | Rótulo de celda, unidad psi en la columna contigua. Sin frase de definición. | XLSM, varias hojas |
| PIP inferido | Rótulo de J58. Sin definición adicional. | XLSM, Prueba Sesnorless |
| PIP sensorless | No hay una entrada de glosario con esas dos palabras. El DOCX se titula «Modelo SensorLess para inferir PIP en pozos ESP». El paper habla de estimación virtual de PIP. | DOCX portada; paper resumen |
| PWF | Presión de fondo fluyente, psi. | Paper, nomenclatura |
| Pwf | Rótulo `Pwf=` en psi. La sigla no se desarrolla en el XLSM. | XLSM |
| PMP | Aparece en los dibujos dentro de la fórmula de Pwf. Significado no definido en la fuente. | Dibujos del XLSM |
| THP | Presión de cabeza de tubing, Pa en la tabla. En la sección 2.1, tubing head pressure, psia o kPa. | DOCX |
| THP | Rótulo de celda en psi (`Pwh     THP` en Hoja1; `THP` en las demás). Pwh no se define. | XLSM |
| CHP | Casing head pressure, alternativa a THP en la sección 2.1. No entra en la ecuación 4.7. | DOCX |
| Q | Caudal, m³/s, «estado a resolver». | DOCX, tabla |
| Q | `Caudal  Q=`, unidad BPD o bbl/dia según la hoja. | XLSM |
| H | Head efectivo, m, «incluye correcciones». | DOCX, tabla |
| Head | Rótulo en pies, o `HEAD` sin unidad en J13 de Metodo Ordenado. | XLSM |
| η, η_p | Eficiencia hidráulica de la bomba, unidad escrita `-`, depende de Q y N. | DOCX, tabla |
| η_em | Eficiencia eléctrica total, motor + drive. | DOCX, tabla y sección 2.3 |
| ηo, η₀ | Curva de eficiencia del fabricante a la velocidad de referencia. | DOCX, secciones 2.2 y 4.2 |
| η_shift | Símbolo en la ecuación 4.3 y en el estado del observador. Significado no definido en la fuente. | DOCX |
| H-Q-η | Curva característica caudal-altura-eficiencia de la bomba. | Paper, nomenclatura |
| Eff Bomba | Rótulo. En Prueba, C35 = 0.62 sin unidad. En Hoja1, J40 = 62 %. En Ordenado, D32 cachea un número del orden de 1960 con ese rótulo. | XLSM |
| BEP | No aparece en DOCX, XLSM, PDF ni paper. El PDF dice «cerca de la máxima eficiencia» sin la sigla. `trabajo.md` sección 2 lo define como Best Efficiency Point y remite a Hydraulic Institute; esa definición es del plan, no de las fuentes de ecuaciones. | trabajo.md; ausencia en el resto |
| VESP | No aparece desarrollado en DOCX, XLSM, PDF ni paper. El plan lo usa en el título junto a ESP y no lo expande. | trabajo.md; ausencia en las fuentes técnicas |
| ESP | Electric Submersible Pump. También «bombeo electrosumergible (ESP)» en las reivindicaciones. | DOCX |
| ESP | Bomba electrosumergible. | Paper, nomenclatura |
| ESP | Bombeo electrosumergible (ESP), en el título y la introducción del PDF. | PDF, página 1 |
| BES | La hoja Prueba Sesnorless titula `ECUACIONES DE LA BES`. El paper dice «pozos BES» sin desarrollarlo. Significado no definido en esas fuentes. | XLSM; paper, conclusión 7 |
| VFD | Variable Frequency Drive. El DOCX toma de él P_in, N o f, y de forma opcional I, V y PF. | DOCX, sección 2.1 |
| VSD/VFD | Variador de velocidad / variador de frecuencia. | Paper, nomenclatura |
| PCP | Bomba de cavidad progresiva. | Paper, nomenclatura |
| DFL | Nivel de fluido dinámico, ft. | Paper, nomenclatura |
| Nivel de fluido | Rótulos `Nivel de Fluido Dimanico` y `Nivel de fluido dinamico inferido`, en pies o ft. | XLSM |
| Sumergencia | Rótulo de entrada en pies, y de resultado en pies o ft. El paper la nombra como salida y no da fórmula. | XLSM; paper, sección de arquitectura |
| IP | Rótulo, unidad BPD/psi. El dibujo escribe `IP=Q/(Pr−Pwf)`. El XLSM no dice «índice de productividad». | XLSM |
| IP | «Indice de productividad (IP)», nombrado para el caudal máximo. Sin ecuación algebraica en el texto extraído. | PDF, página 1 |
| Pr | `Presion del Reservorio Pr`, psi. | XLSM Hoja1, METODO, Metodo Ordenado |
| Py | `Presion del Reservorio Py`, psi. Misma magnitud de rótulo, otra letra, en la hoja sensorless y en su dibujo de Qmax. | XLSM Prueba Sesnorless |
| BSW | Rótulo con unidad %. No entra en las fórmulas leídas. | XLSM |
| GOR | Relación gas-petróleo, pc/STB. | Paper, nomenclatura. No está en el DOCX ni en el XLSM |
| TDH | En el PDF: Pbdp + Pcf + Nd, en m o ft, diferencia de presión de la bomba expresada como altura de columna. | PDF, página 2 |
| TDH | En Prueba, J41 es gradiente total × profundidad, unidad escrita psi. D77 es otra suma, sin unidad. | XLSM |
| k_f | Coeficiente de fricción lumped. Unidad Pa·s²/m⁶. | DOCX, tabla |
| k_g | Interferencia de gas, rango escrito 0–0.4, adimensional en la tabla. | DOCX |
| Δz | Elevación entre bomba y superficie, m, positivo hacia arriba. | DOCX |
| p | Letra en `N = 120·f / p`. Significado no definido en la fuente. | DOCX |
| β | En `C_η = 1 − β·k_g`, con `β ≈ 1`. Significado no definido. | DOCX, sección 4.3 |
| SensorLess / Sensorless | Nombre del método en el DOCX y en el paper. La hoja del XLSM escribe `Sesnorless`. No se unifican. | Las tres fuentes |
| DHS | Sensor de fondo permanente (manómetro de completación). | Paper, nomenclatura |
| ECH | Prueba de nivel acústico Echometer. | Paper, nomenclatura |
| SL | Estimación del algoritmo SensorLess. | Paper, nomenclatura |
| GLM | Nombre que el plan da al modelo de lenguaje posterior. No es una variable física y no está en las fuentes de ecuaciones. | trabajo.md |

---

## 8. Pendientes y preguntas bloqueantes

Prioridad para no cerrar un núcleo de cálculo.

1. **¿Cuál es el PIP de trabajo en Prueba Sesnorless?** J23 (desde un Pwf escrito), J58 (rótulo «PIP inferido»), N58 (sin rótulo, constante 13600) y el dibujo (constante 136000 y gradiente dentro del paréntesis) no dan el mismo número con los datos cacheados de la propia hoja.
2. **¿El signo de `Pwf inferido` es el de J64 (más) o el del dibujo (menos)?** J23 usa el signo del dibujo; J64 no.
3. **¿136000, 13600, 0.433, 0.746, 745.69, 2400, 4, 0.8, 32.2, 2.31, 0.434, 0.803, 1.91, 63, 64, 84, 1360, 2895, 950, 4268, 0.04, 0.96 y 1.8 qué son y en qué unidad?** La fuente no los define celda por celda.
4. **¿La fricción es siempre `f = 64/Re`?** El libro escribe tres regímenes y calcula una rugosidad que ninguna fórmula de `f` usa. Hoja1 cachea Re ≈ 10342 y aun así divide 64/Re.
5. **¿Qué diámetro entra en velocidad y Reynolds?** La fórmula usa C20 = 0.25 pies. En METODO, Ordenado y Prueba el DI escrito es 2.992 pulgadas, que no equivale a 0.25 pies.
6. **¿El caudal de la fricción es el de prueba o el escalado por Hz?** J29 usa C23; L55 usa J12.
7. **¿Etapas y head/etapa de GN4000 son 52 y 63, o 63 y 52?** METODO y Metodo Ordenado traen los rótulos al revés. El producto 3276 coincide; el reparto no queda escrito de una sola forma.
8. **¿Pr y Py son el mismo símbolo?** El rótulo cambia en Prueba Sesnorless.
9. **¿El caso 232HST es uno solo?** Perforados, Q prueba, Pwf prueba, sumergencia e IP no coinciden entre METODO, Metodo Ordenado y Prueba Sesnorless.
10. **DOCX sin números de calibración ni curva.** Faltan H₀(Q), η₀(Q), N₀, ρ, Δz, k_f, k_g, β, η_shift, η_em, a0, a1, a2, Q_min, Q_max, y la fórmula del score de confianza. Sin eso el MVP no se puede evaluar.
11. **Unidades cruzadas dentro del DOCX.** Sección 2.1: P_in en kW y THP en psia o kPa. Tabla: P_in en W y THP en Pa. Hay que dejar escrita la conversión antes de implementar; la fuente no da un ejemplo de conversión.
12. **p, β, η_shift, a0, a1, a2, P_hyd, FFT, CHP frente a THP.** Usados o nombrados sin fila completa de definición.
13. **Reivindicaciones frente a la sección 4.** Las reivindicaciones quitan η_shift, escriben `Darcy-Weisback` junto a P_loss, y la sección 8 reserva Darcy–Weisbach para la fricción del tubing. No se sabe cuál texto manda.
14. **Eficiencia del XLSM.** C35 = 0.62, J40 = 62 %, D32 cachea ≈ 1960 con rótulo `Eff Bomba=`. No está declarado si son la misma magnitud.
15. **TDH.** PDF: altura en m o ft, y además 1720 m en la página 2 frente a 1700 m en la página 5. XLSM: J41 en psi y D77 sin unidad, sumando un término dividido entre 1000. No unificarlos sin una decisión.
16. **Hazen-Williams.** Hace falta lectura visual de la página 2 del PDF si se quiere la expresión lineal. El texto sí fija C = 120, el resultado 40.5 ft/1000 ft y el supuesto agua a 20 ºC, fluido del ejemplo.
17. **VBA y ActiveX.** Están en el archivo. No se ejecutaron. No se sabe si una macro pisa algún valor al abrir el libro. Los `<v>` son el cache guardado, no una sesión de Excel de este agente.
18. **Datos de pozo.** Este encargo no leyó los Excel de mediciones. No se puede decir qué columnas alimentarían estas ecuaciones.
19. **BEP, VESP, BES, Pwh, PMP.** Sin definición utilizable en las fuentes de ecuaciones, o sin desarrollo de la sigla.
20. **Paper.** Sus desviaciones son de Caño Sur y de un algoritmo con aprendizaje. No son un banco de prueba del DOCX ni del XLSM.

---

## 9. Qué no se puede afirmar

- No se puede afirmar que alguna ecuación esté aprobada, validada o lista para producción.
- No se puede afirmar que el DOCX y el XLSM calculen el mismo PIP. Las expresiones y los sistemas de unidades son distintos.
- No se puede afirmar que el dibujo de Prueba Sesnorless y la celda J58 sean la misma fórmula. Con los valores cacheados de esa hoja, no dan el mismo número.
- No se puede afirmar que los `<v>` cacheados sean físicamente correctos. Solo se comprobó, en la cadena sensorless revisada, que coinciden con la aritmética de la fórmula guardada.
- No se puede afirmar un régimen de flujo turbulento o laminar como regla del libro: la única fórmula de `f` es `64/Re`.
- No se puede afirmar el significado de las constantes sin nombre listadas en la sección 8.
- No se puede afirmar que 62.4, 0.433, 5.615, 144 o 0.00067197 estén «bien» más allá de que la fuente los escribe. Donde el rótulo de unidad contradice el de la celda vecina (psi/pie³ frente a psi/pie; `vatio` frente a una división entre 1000), la contradicción queda abierta.
- No se puede afirmar que el ejemplo del PDF (Golfo San Jorge, 2002, DX-3000, 50 Hz) sea un pozo de este proyecto, ni que el ID 2.992 pulgadas identifique el tubing del XLSM con el de ese PDF.
- No se puede afirmar la forma lineal completa de Hazen-Williams a partir de la extracción de texto.
- No se puede afirmar que las métricas del paper (Caño Sur, DHS, Echometer, aprendizaje en línea) midan el modelo de estas notas.
- No se puede afirmar que este inventario reproduzca el algoritmo patentado o comercial SensorLess. El paper lo describe como modelo híbrido con entrenamiento; el DOCX es un set algebraico; el XLSM es una planilla.
- No se puede afirmar qué hace el VBA.
- No se puede afirmar que los Excel de mediciones del proyecto contengan P_in, curvas, k_f, ρ o Δz. No se leyeron en este encargo.
- No se puede afirmar un BEP numérico ni un rango de operación alrededor del BEP. Ninguna fuente de ecuaciones lo fija.
- No se puede afirmar que VESP, BES o PMP signifiquen una expansión concreta: las fuentes técnicas leídas no la escriben.
