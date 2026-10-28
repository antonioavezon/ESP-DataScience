# Auditoría integral de los 12 cuadernos · BES-jun

Expediente: `datasets/en_uso/BES-jun/`. Estado: **Listo para revisión** (no «Completo»: siguen abiertas CT-01…CT-10 y P-14).
Entorno: Fedora Linux 43, Python 3.14.8, nbconvert 7.17.2, pandoc, Google Chrome 155 (headless), PyMuPDF 1.28.2.
Todas las cifras de este documento salen de `logs/verificacion_exportacion.json` y de comparar con `logs/respaldo_previo_a_auditoria/`.

## 1. Estado inicial y causa raíz

| Cuaderno | Celdas (inicial) | Palabras de texto (inicial) | Páginas PDF (inicial) | Celdas (final) | Texto / código | Palabras de texto (final) | Páginas PDF (final) |
|---|---:|---:|---:|---:|---|---:|---:|
| 00_inventario_y_fuentes | 3 | 169 | 3 | 25 | 15 / 10 | 1630 | 7 |
| 00_inventario_y_trazabilidad | 3 | 120 | 3 | 23 | 14 / 9 | 1467 | 8 |
| 01_inspeccion_BES_jun | 3 | 209 | 2 | 29 | 16 / 13 | 1971 | 8 |
| 01_inspeccion_y_calidad_datos | 3 | 378 | 3 | 38 | 22 / 16 | 2218 | 11 |
| 02_ecuaciones_y_variables | 3 | 203 | 3 | 23 | 16 / 7 | 2854 | 11 |
| 02_trazabilidad_y_analisis_formulas | 3 | 226 | 2 | 32 | 19 / 13 | 2109 | 11 |
| 03_limpieza_y_mapeo | 3 | 147 | 2 | 35 | 22 / 13 | 2003 | 11 |
| 03_mapeo_y_preparacion_BES_jun | 3 | 218 | 4 | 32 | 19 / 13 | 2010 | 9 |
| 04_calculos_deterministicos | 3 | 232 | 3 | 30 | 17 / 13 | 1563 | 11 |
| 04_modelo_deterministico | 3 | 133 | 2 | 29 | 18 / 11 | 2385 | 9 |
| 05_evaluacion_por_pozo | 3 | 272 | 4 | 36 | 20 / 16 | 2264 | 11 |
| 06_hallazgos_y_reglas_candidatas | 3 | 228 | 3 | 27 | 16 / 11 | 1577 | 11 |

Las celdas y palabras iniciales provienen de `logs/respaldo_previo_a_auditoria/notebooks/`; las páginas iniciales, de los PDF de `logs/respaldo_previo_a_auditoria/pdf_notebooks/`.

**Causa raíz.** Había dos fallos independientes:

1. **Contenido.** Cada cuaderno tenía 3 celdas: una portada, una celda de código y una de cierre de pocas líneas. No había
   alcance, necesidad, fundamento, interpretación de resultados, limitaciones ni referencias. El código se ejecutaba, pero no
   respondía a ningún problema planteado.
2. **Exportación.** El exportador anterior (`exportar_pdf.py`) no convertía el cuaderno: reescribía un resumen a mano. Por eso el
   PDF «no describía nada» aunque el cuaderno existiera. Además, ese script regenera el PDF del informe, así que no debe
   ejecutarse (ver §6).

## 2. Qué se hizo

**Contenido (sin cambiar objetivos ni resultados del análisis).**
- Los 12 cuadernos se reescribieron desde módulos de `src/informes/cuadernos/` con la estructura pedida: título, contexto,
  justificación, objetivo general, dominio y alcance, fuentes y datos, objetivos específicos con criterios de aceptación,
  riesgo si el paso falla, desarrollo por pasos (qué se hace, para qué, código, salida, interpretación), conclusión técnica,
  **Limitaciones** y **Referencias** (solo las usadas: libro, PDF 004, hoja de ecuaciones, inventarios y registros del expediente).
- Las ecuaciones se presentan con fenómeno, formulación, variables, unidades, hipótesis, función de Python y limitación, y se
  clasifican como teórica documentada, relación empírica, procedimiento numérico o hipótesis de aplicación.
- Cuadernos nuevos: **05** (evaluación por pozo: ventana operativa, intersección sistema–bomba, sensibilidad local, ambigüedades
  CT-02…CT-05) y **06** (hallazgos H-01…H-13 con consultas CT-01…CT-10 y reglas candidatas).
- Criterios de aceptación **ejecutables** (`Criterios.exigir()`): si uno no se cumple, el cuaderno se detiene.
  Ejemplo real: el criterio C06-2 detuvo el cuaderno 06 cuando CT-08 no tenía hallazgo; se corrigió el contenido (H-01 pasó a CT-08).
- Módulos nuevos de cálculo: `analisis/cadena.py` y `analisis/sensibilidad_local.py` (con `tests/test_sensibilidad_local.py`,
  4 pruebas). Sin modificar la lógica del código existente.
- Correcciones de texto que contradecían el cálculo (ver §4).

**Exportación.** `informes/exportar_cuadernos.py` (cuaderno → HTML con nbconvert → PDF con Chrome), `informes/verificar_exportacion.py`
y el orquestador `informes/pipeline_cuadernos.py`. Detalle y comandos en `docs/procedimiento_exportacion_cuadernos.md`.

## 3. Matriz por cuaderno (resultado real de la última corrida)

| Cuaderno | Contenido revisado | Ejecución | HTML íntegro | PDF íntegro | Páginas | Imágenes (PDF/esperadas) | Tablas (HTML/esperadas) | Ecuaciones (HTML/esperadas) |
|---|---|---|---|---|---:|---|---|---|
| 00_inventario_y_fuentes | OK | OK | OK | OK | 7 | 0/0 | 7/7 | 0/0 |
| 00_inventario_y_trazabilidad | OK | OK | OK | OK | 8 | 0/0 | 8/8 | 0/0 |
| 01_inspeccion_BES_jun | OK | OK | OK | OK | 8 | 2/2 | 8/8 | 0/0 |
| 01_inspeccion_y_calidad_datos | OK | OK | OK | OK | 11 | 0/0 | 15/15 | 0/0 |
| 02_ecuaciones_y_variables | OK | OK | OK | OK | 11 | 0/0 | 6/6 | 37/37 |
| 02_trazabilidad_y_analisis_formulas | OK | OK | OK | OK | 11 | 0/0 | 12/12 | 0/0 |
| 03_limpieza_y_mapeo | OK | OK | OK | OK | 11 | 0/0 | 10/10 | 0/0 |
| 03_mapeo_y_preparacion_BES_jun | OK | OK | OK | OK | 9 | 1/1 | 9/9 | 0/0 |
| 04_calculos_deterministicos | OK | OK | OK | OK | 11 | 0/0 | 9/9 | 0/0 |
| 04_modelo_deterministico | OK | OK | OK | OK | 9 | 1/1 | 9/9 | 31/31 |
| 05_evaluacion_por_pozo | OK | OK | OK | OK | 11 | 3/3 | 11/11 | 0/0 |
| 06_hallazgos_y_reglas_candidatas | OK | OK | OK | OK | 11 | 0/0 | 8/8 | 0/0 |

«Contenido revisado» = el verificador exige portada con las secciones, más de 600 palabras de texto explicativo, Limitaciones,
Referencias, conclusión técnica y ningún marcador sin rellenar. «PDF íntegro» = todo el texto Markdown, el código, las salidas
de texto y las celdas de tabla del cuaderno aparecen en el PDF **en el orden visual**, sin recortes en los márgenes, sin páginas
en blanco, con las imágenes esperadas y con el número de página consecutivo.

Los 12 pares HTML/PDF están en `pdf/notebooks/` con el nombre del cuaderno original.

## 4. Problemas encontrados y cómo se resolvieron

| # | Problema | Resolución |
|---|---|---|
| 1 | Cuadernos de 3 celdas, sin desarrollo | Reescritos (§2) |
| 2 | PDF generado a mano, no del cuaderno | Cadena nbconvert → Chrome, con verificación |
| 3 | CT-08 sin hallazgo vinculado | El criterio ejecutable detuvo el cuaderno; H-01 pasó a CT-08 |
| 4 | H-11 asignado a CT-01 sin relación | Nueva consulta CT-10 (parámetros °API, yacimiento, burbuja y densidad del agua idénticos en los 5 pozos); H-12 reformulado |
| 5 | C06-5 era un `True` fijo | Calcula la condición (tablas repetidas y cono = Q de máxima eficiencia) |
| 6 | Textos que contradecían la salida («cuatro de seis requisitos», «comparable o superior», «ocho de diez», «tres hojas desplazadas») | Corregidos a seis, «del mismo orden», ocho y cuatro; mediana de inclinación 28–46° |
| 7 | `np.int64` en la evidencia de C01b-2 | Convertido a `int` |
| 8 | RC-BES-01 daba alerta por comparar límites sin escalar | Con límites escalados a la frecuencia solo se activa RC-BES-03 en las 5 hojas (la regla sin escalar queda documentada como artefacto) |

**Defectos del verificador durante el desarrollo** (registrados porque pudieron ocultar fallos reales):
- Los marcadores de lista (`1.`, `-`) no son texto del cuaderno que Chrome dibuje igual; se segmenta por línea.
- Chrome escribe el texto de las **tablas después** de los bloques que las siguen en el flujo del PDF. Comparar en el orden del
  flujo daba cientos de falsos errores. Se compara en **orden visual** (bloques ordenados por posición en la página).
- En una celda de tabla de varias líneas el PDF intercala las líneas de celdas vecinas; la celda se acepta si aparece contigua
  o, si no, si cada palabra está en la ventana de su tabla. Es menos estricto que el orden estricto del texto corrido.
- Defecto **real** de maquetación: las cabeceras de columna estrechas se partían a mitad de palabra («combinad|as»). Se corrigió
  (`overflow-wrap: break-word` solo en `th`) y la tabla ancha pasa a apaisada solo si sus cabeceras no caben en vertical.

## 5. Pruebas realizadas

- `pytest`: **39 pruebas, todas pasan** (incluye las 4 de sensibilidad local, con exponentes exactos 1.85 y −4.8566 de la fricción).
- Control **positivo**: el cuaderno sin alterar contra su HTML/PDF da 0 errores.
- Controles **negativos** (sobre `05_evaluacion_por_pozo`, contra el HTML y el PDF reales): una frase añadida al Markdown, una
  línea de código añadida, una fila de tabla inexistente, una línea extra en una salida de texto y una celda Markdown nueva
  no exportada. **Las cinco alteraciones se detectan** tanto en HTML como en PDF.
- Inspección visual de páginas renderizadas: portada del 02, página de ecuaciones del 02, figura y código del 05, tabla de 10
  columnas del 01 (portrait, cabeceras íntegras) y la página apaisada del 01 antes del ajuste. Sin recortes ni texto superpuesto.
- Huella SHA-256 de `pdf/informes/informe_analisis_BES-jun.pdf` antes y después: `431e7fe7…d9c19`, idéntica al respaldo.
  El informe PDF **no se modificó**.

## 6. Protección del original

No es un repositorio git. Se creó `logs/respaldo_previo_a_auditoria/` con los 12 `.ipynb` originales, los 12 PDF previos, el
PDF del informe y `MANIFIESTO_SHA256.txt` (24 entradas), para poder hacer diffs y restaurar. No se sobrescribió ningún dataset.
`informes/exportar_pdf.py` y `informes/escribir_informe.py` (anteriores) se conservaron sin cambios; **`exportar_pdf.py` no debe
ejecutarse**: además de los PDF de cuadernos regenera el PDF del informe.

## 7. Relación entre los 12 cuadernos (no son duplicados)

Los pares con el mismo número conservan su identidad y su objetivo:

| N.º | Cuaderno | Objetivo general (de su portada) |
|---|---|---|
| 00 | `00_inventario_y_fuentes` | Verificación reproducible de identidad e inventario de insumos y fuentes, con criterios ejecutables que detienen la ejecución |
| 00 | `00_inventario_y_trazabilidad` | Qué hay en el expediente, cómo se relacionan los 12 cuadernos entre sí y con los archivos que producen, y que los originales respaldados no se alteraron |
| 01 | `01_inspeccion_BES_jun` | Describir con evidencia la estructura y el contenido de las cinco hojas |
| 01 | `01_inspeccion_y_calidad_datos` | Dictamen de calidad por hoja: defectos que contaminan la cadena de cálculo frente a los que no |
| 02 | `02_ecuaciones_y_variables` | Documentar y verificar las diez ecuaciones y las variables, distinguiendo documentado, empírico y supuesto |
| 02 | `02_trazabilidad_y_analisis_formulas` | Clasificar cada fórmula (utilizable / con reserva / fuera de alcance) con fuente, constantes y consultas CT; cuantificar la inconsistencia hidrostática |
| 03 | `03_limpieza_y_mapeo` | Archivos de variables y unidades; prueba de ida y vuelta contra el libro (ningún valor alterado) |
| 03 | `03_mapeo_y_preparacion_BES_jun` | Tablas ordenadas del survey y de las curvas de bomba, con estadísticas y figuras, sin transformar valores |
| 04 | `04_calculos_deterministicos` | Cadena de cálculo en funciones auditables, reproducción de las celdas intermedias, casos límite y ficha de confiabilidad |
| 04 | `04_modelo_deterministico` | Modelo como sistema, dominio de validez observado y sensibilidad local de Q* |
| 05 | `05_evaluacion_por_pozo` | Evaluación por hoja, efecto de cada ambigüedad CT-02…CT-05 en el caudal y dictamen de lo que se puede afirmar |
| 06 | `06_hallazgos_y_reglas_candidatas` | Hallazgos de los cuadernos 00–05 enlazados a consultas CT y reglas, y límites de afirmación del expediente |

Cada par con el mismo número cubre una parte distinta del trabajo (objetivos distintos, tabla arriba); no son versiones duplicadas.

No se fusionó, eliminó ni renumeró ninguno.

## 8. Pendientes y límites (no resueltos, no ocultos)

- **Advertencia de dominio observado**: el código no avisa al extrapolar fuera del rango observado (por ejemplo 80 Hz da
  15 114 BFPD sin alerta). Está documentado en 04 y 05; **la lógica no se modificó** para cuadrar el texto.
- Consultas técnicas abiertas CT-01…CT-10 (`docs/consultas_tecnicas_pendientes.md`) y **P-14** (sin respuesta); el motor
  general sigue bloqueado y el orden oficial D1→D2 no se tocó.
- Hallazgo estructural: la hoja evalúa la fricción con el caudal **medido**, no con el calculado; iterar a punto fijo reduce la
  brecha calculado–medido entre 20 y 42 % (diagnóstico, no corrección).
- Archivos huérfanos sin clasificar en `reports/figuras/`: `caudal_y_limites.png` y `head_tabulado.png` (no se borraron).
- Cosmético: en párrafos justificados con tokens de código largos aparecen huecos entre palabras. No afecta al contenido.
- Una fila de ficha muestra decimales sin formato (por ejemplo 65.55555555555556) porque es la salida literal del código.
- Pendiente de actualizar (no afectan a los cuadernos): `reports/informe_analisis_BES-jun.md/.html` (el PDF no se toca),
  `docs/diccionario_datos_BES_jun.md`, `data_procesados/transformaciones.md`.
- El verificador comprueba texto, orden, recortes, páginas en blanco, imágenes y numeración. **No** valida el significado
  técnico: eso sigue siendo revisión humana.
