# Notas del agente de datos — BES_jun

Perfilado local. No es una predicción.

- Hash SHA-256 verificado en `data/entrada/BES_jun_dataset_trabajo.xlsx` y en `Copia de FINAL BES-jun.xlsx`: `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`.
- Hojas: 5 (QF-554H, QF-545H, QF-500H, QF-378HST, QF-549HST), todas visibles.
- Hay fórmulas: sí. Celdas con fórmula: 1270. Todas tienen valor cacheado. `fullCalcOnLoad=True`.
- Llave de pozo: no se pudo determinar. Cada hoja coincide con el texto junto a `Cluster:` (`QF-554H`, `QF-545H`, `QF-500H`, `QF-378HST`, `QF-549HST`). Junto a `Pozo:` hay otro texto distinto (`QF-084`, `QF-301`, `QF-147`, `QF-005`, `QF-306`). El libro no define cuál es la llave. No se agrupó por suposición.
- Errores de Excel leídos: 13 celdas `#DIV/0!` en la caché de `QF-549HST`. Cero en las otras hojas y cero en el texto de las fórmulas.
- `QF-554H` está desplazada una fila respecto del formulario de las otras cuatro, desde el título mecánico.
- B6 es `=TODAY()` cacheado como 2026-10-17 en cuatro hojas. En `QF-549HST` B6 es la constante 2017-09-06.
- El diseño es un formulario con celdas combinadas, seis gráficos de dispersión y una imagen por hoja. No hay nombres definidos ni tablas.

## Rutas escritas

- `data/perfiles/BES_jun/perfil_hojas.md`
- `data/perfiles/BES_jun/resumen_columnas.csv`
- `data/perfiles/BES_jun/formulas_muestra.md`
- `data/perfiles/BES_jun/calidad.md`
- `logs/notas_agente_datos.md`

## Bloqueos

- No hay bloqueo de hash ni de lectura del xlsx.
- No se pudo leer el título de los gráficos (`AttributeError` en la estructura de título de openpyxl).
- No se recalcularon IF, INDEX, MATCH, AVERAGE, SQRT ni TODAY. La comparación fórmula/caché de esas celdas es la pareja leída, no una verificación algebraica.
- No hay definición de columnas dentro del libro. El CSV por columna de Excel mezcla textos y números; eso limita el uso de min/max como si fueran una variable.

## Qué no se puede afirmar

- Cuál de los dos identificadores (`Cluster` o `Pozo`) es el pozo, ni que el nombre de la hoja lo sea.
- El significado operativo de las etiquetas, más allá del texto y de la unidad escrita al lado.
- Que un cero, un `#DIV/0!` o un paso de profundidad irregular sea una falla.
- Que la caché siga siendo válida si Excel recalcula `TODAY()` en otra fecha.
- Resultados de un modelo, de una imputación o de una predicción: no se hicieron.

## Hechos de apoyo

- Aritmética simple recomprobada en local: 714 coincidencias con la caché, 0 desacuerdos.
- Referencias de una sola celda no coherentes: 0.
- Celdas combinadas por hoja: QF-554H=82, QF-545H=80, QF-500H=80, QF-378HST=79, QF-549HST=79.
- Filas del bloque Measured (A numérico): QF-554H=56, QF-545H=68, QF-500H=71, QF-378HST=59, QF-549HST=67.

