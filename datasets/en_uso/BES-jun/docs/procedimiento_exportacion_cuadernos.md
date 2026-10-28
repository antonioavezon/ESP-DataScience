# Procedimiento: cuaderno → HTML → PDF, con verificación

Entorno de referencia: Fedora Linux 43, Python 3.14.8 (`/home/antonio/projects/HUC/.venv`), pandoc (`/usr/bin/pandoc`),
Google Chrome 155 (`/usr/bin/google-chrome`, modo headless). No se asume que otra distribución (CentOS, Yocto) tenga las
mismas rutas, fuentes o versión de Chrome: en ellas hay que comprobarlo antes.

Flujo obligatorio: **cuaderno completo → HTML íntegro (nbconvert) → PDF íntegro (Chrome desde ese HTML)**. Ningún PDF se arma
con fragmentos ni con un resumen aparte.

## Comandos (desde la raíz del expediente `datasets/en_uso/BES-jun/`)

Solo exportar y verificar los cuadernos tal como están (no los modifica ni los ejecuta):

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -u -m informes.pipeline_cuadernos

Un subconjunto:

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -u -m informes.pipeline_cuadernos --solo 05 06

Con ejecución previa de los cuadernos (kernel `huc-vesp`; el de trazabilidad va al final):

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -u -m informes.pipeline_cuadernos --ejecutar

> **Advertencia (destructivo).** `--construir` **regenera los 12 `.ipynb` desde `src/informes/cuadernos/` y descarta sus
> salidas**. Los originales previos a la auditoría están en `logs/respaldo_previo_a_auditoria/`, pero cualquier edición hecha
> a mano en un cuaderno se perdería. Úselo solo si se quiere reconstruir desde los módulos (normalmente con `--ejecutar`).

`informes.exportar_pdf.exportar()` ahora se niega a correr: reescribía los PDF de los cuadernos con un resumen.
El informe, la ficha y la guía salen de su Markdown con:

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -c "from pathlib import Path; from informes.exportar_documento import exportar; r=Path('.'); exportar(r/'reports/informe_analisis_BES-jun.md', r/'reports/informe_analisis_BES-jun.html', r/'pdf/informes/informe_analisis_BES-jun.pdf')"

Pruebas: `PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m pytest -q` (39 pruebas).

## Qué hace el orquestador

1. Descubre los `.ipynb` de `notebooks/` y valida que sean nbformat válidos.
2. (Opcional) reconstruye y/o ejecuta.
3. Exporta a `logs/exportacion_staging/` (HTML con nbconvert, PDF con Chrome). `pdf/notebooks/` no se toca todavía.
4. Verifica cada par HTML/PDF contra el cuaderno (abajo).
5. **Promueve a `pdf/notebooks/` solo los cuadernos que pasan todas las verificaciones.** Si uno falla, se conserva el HTML/PDF
   anterior; no se marca éxito ni se borra un documento válido previo.
6. Escribe `logs/verificacion_exportacion.json` y `.md` y compara la huella SHA-256 del informe PDF antes y después.

El código de salida es 0 solo si todos los cuadernos procesados pasan. Los errores se separan en **contenido**, **ejecución**,
**exportación** (HTML) y **paginación** (PDF).

## Qué verifica

- **Contenido:** portada con las secciones requeridas, más de 600 palabras explicativas, Limitaciones, Referencias, conclusión
  técnica, ningún marcador `@@` sin rellenar, nbformat válido.
- **Ejecución:** todas las celdas de código ejecutadas, sin salidas de error.
- **HTML:** todo el Markdown, código, salidas de texto, tablas, imágenes incrustadas y ecuaciones presentes y en orden; sin recursos remotos.
- **PDF (Letter vertical):** el mismo contenido, comparado en **orden visual**; sin recortes fuera de los márgenes, sin páginas en
  blanco, con todas las imágenes, numeración consecutiva y más páginas que el mínimo.
  Las tablas anchas pasan a página apaisada solo si sus cabeceras no caben en vertical o tienen muchas columnas y mucho texto por fila; no se elimina ninguna fila ni columna.

El verificador se probó con controles negativos (texto, código, tabla, salida y celda no exportada alterados: los cinco se
detectaron) y positivo (0 errores). Ver `docs/revision_notebooks_auditoria.md` §5.

## Límites conocidos

- Chrome escribe el texto de las tablas en el flujo del PDF después de los bloques siguientes, y entrelaza las líneas de celdas
  vecinas cuando una celda ocupa varias líneas. Por eso las celdas de tabla se aceptan contiguas o, si no, palabra por palabra
  dentro de la ventana de su tabla. Es menos estricto que el texto corrido.
- No valida el significado técnico del contenido ni la estética fina (huecos en párrafos justificados con tokens largos).
- No se regeneran salidas faltantes ni se inventan: si una celda no se ejecuta, el cuaderno falla en «ejecución».
