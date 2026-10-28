# Bitácora

## 2026-10-17 · Inventario y copia de BES-jun

- Sistema: Fedora Linux 43. Python 3.14.8 en `.venv`.
- SHA-256 de `Copia de FINAL BES-jun.xlsx`: `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`.
- MD5: `ba89f317f505f321c496e44ab5046104`.
- La copia `fuentes/originales/` y `data/entrada/BES_jun_dataset_trabajo.xlsx` coinciden con ese hash. El original de la raíz no se reescribió.
- Los MD5 de D1, D2, E1, X1, A1 y R1 coinciden con `asesor-esp/data/raw/README.md`.
- Los cuatro DOCX de ecuaciones son el mismo SHA-256.
- `trabajo2.md` y `asesor-esp/trabajo.md` son el mismo MD5.
- No se ejecutó VBA. No se instaló un GLM. No se inicializó un repositorio ni se hizo commit.
- Dependencias: `requirements.txt` y `logs/pip_freeze.txt`. `xlrd==1.2.0` porque la serie 2 no lee `.xls`. `scikit-learn==1.9.1` quedó instalado y no entra en el cálculo.
- Kernel Jupyter local: `huc-vesp`.

## 2026-10-17 · Lectura y pruebas

- Agentes de lectura lanzados al inicio: uno sobre documentos y otro sobre el Excel. Al integrar, sus notas aún no estaban en `logs/`. El coordinador leyó los extractos locales en `logs/extractos_coordinador/` y el libro con openpyxl.
- Pruebas: `.venv/bin/python -m pytest -q` → 8 passed.
- Esas pruebas comparan la transcripción con el cache de Excel. No son una validación contra otra medición.
- Evidencia de cifras: `data/perfiles/BES_jun/resumen_pozos.csv`, `reports/BES_jun/`.
- Cuadernos `notebooks/00` a `06` ejecutados con el kernel `huc-vesp`. Ninguna celda terminó en error.

## 2026-10-17 · Integración de las lecturas independientes

- [Inspección BES-jun](2d5d0f54-3e81-465a-82d1-d2ffb21a4735) escribió `data/perfiles/BES_jun/calidad.md`, `formulas_muestra.md`, `resumen_columnas.csv` y `logs/notas_agente_datos.md`. El perfil largo de hojas se había sustituido por un resumen corto; se regeneró `perfil_hojas.md` (1177 líneas) con el mismo script de esa lectura.
- Comprobado de nuevo en la caché: 13 `#DIV/0!` en la columna D de `QF-549HST`. El informe preliminar y el diccionario decían que no había ese error. Quedó corregido. Esas celdas no entran en el balance de PIP y THD.
- La misma lectura concluye que el libro no define la llave entre Cluster y Pozo. El informe deja de llamar llave a la pareja hoja + Pozo. Las hojas siguen evaluadas por separado.
- [Ecuaciones y fuentes](731c493b-cfa7-4628-be37-8155d2b8a000) escribió `logs/notas_agente_dominio.md`. El pendiente del signo de `J64` frente al dibujo del XLSM quedó citado en `docs/trazabilidad_ecuaciones.md`. Ninguna ecuación pasa a aprobada.

## 2026-10-17 · Decisiones

- DEC-001: BES-jun es el archivo leído en esta iteración. No entra al tablero de asesor-esp.
- P-12 del plan queda en parcial. P-14 pregunta si el tablero de asesor-esp cambia el orden.
- `docs/decision_modelo_base.md` sigue en borrador. Ninguna etapa de `trabajo.md` se marcó Completa.

## 2026-10-17 · Bloqueo P-14 y puerta de fórmulas

- P-14 quedó en `docs/decisiones_pendientes.md`. Respuesta vacía. Fecha de respuesta vacía. Responsable: el del alcance (en el plan, Remitente), sin contestación.
- Efecto mientras no haya respuesta: el orden del tablero sigue D1 (`RB-1521-PY-121120.xls`) y después D2. BES-jun no sustituye a D1 ni se añade al tablero.
- El motor determinístico general queda bloqueado también hasta la puerta de fórmulas. Etapas 4, 5 y 6 de `trabajo.md` pasan a Bloqueada para implementación, evaluación del motor y aprobación de reglas.
- Sigue permitido inventario, lectura, perfilado, entorno y cuadernos exploratorios. No se amplía un motor común.

## 2026-10-17 · Expediente por dataset

- BES-jun es el único expediente en `datasets/en_uso/BES-jun/`. Estado: Listo para revisión. No pasa a `datasets/procesadas/` hasta aprobación del usuario.
- Copia de trabajo: `datasets/en_uso/BES-jun/entrada/BES_jun.xlsx`. SHA-256 igual al original `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`. El original de la raíz y el de `fuentes/originales/` no se modificaron.
- RB-1521 y RB-IA-2191 quedaron en `datasets/en_espera/`, sin copia de trabajo y sin leer filas. El orden oficial D1 → D2 no cambia. P-14 sigue sin respuesta.
- El código, los cuadernos, las pruebas, el perfil y el informe de BES-jun están dentro del expediente. El catálogo común sigue en `docs/trazabilidad_ecuaciones.md`. No hay motor general. No se instaló un GLM.

## 2026-10-17 · Cierre del análisis de BES-jun

- Sistema: Fedora Linux 43. Python 3.14.8 del `.venv`. Google Chrome 155.0.8059.84. Pandoc en `/usr/bin/pandoc`. No hay TeX Live; el PDF sale de Chrome headless.
- Comandos, desde `datasets/en_uso/BES-jun/`: `PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m pytest -q` → 12 passed. `jupyter nbconvert --execute --inplace` sobre los siete cuadernos `00_inventario_y_fuentes` a `06_hallazgos_y_reglas_candidatas`. `PYTHONPATH=src python -m informes.escribir_informe` y `python -m informes.exportar_pdf`.
- Los PDF están en tamaño carta (612 × 792). La primera página de cada cuaderno trae título, objetivo y descripción, sin código. Se abrieron con PyMuPDF.
- Se reescribieron `05_evaluacion_por_pozo.ipynb` y `06_hallazgos_y_reglas_candidatas.ipynb` porque el cierre usa esos nombres. Los cuadernos 00 a 04 de la pasada anterior siguen con sus nombres previos.
- No se procesaron los Excel de `datasets/en_espera/`. El original de BES-jun conserva el SHA-256 `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`.
- Estado del expediente: Listo para revisión. No se movió a `datasets/procesadas/`. P-14 sigue sin respuesta. No hay predicción validada. Las reglas siguen candidatas.

## 2026-10-17 · Revisión editorial de los doce cuadernos

- Se reescribieron las 20 celdas de texto que había y se añadieron 4 cierres. Quedan 24 celdas Markdown. Ningún cuaderno quedó sin ejecutar.
- El control de integridad imprime ruta, bytes, SHA-256 completo y MD5 de la copia de trabajo, de `fuentes/originales/` y del archivo de la raíz. `coincidencia_binaria=si`. Ese control no valida mediciones.
- Se dejó de afirmar que la hoja es la llave del pozo. El caso con dato faltante usa QF-554H y BS&W vacío, no los literales 65 y 8.345.
- El cuaderno 05 calcula la diferencia de PIP contra la caché. En las cinco hojas es 0 ft. No es una predicción.
- Comando, desde `datasets/en_uso/BES-jun/`: `.venv` de la raíz, `python -m pytest -q` → 13 passed. `jupyter nbconvert --execute --inplace notebooks/*.ipynb`, sin celdas en error. Luego `PYTHONPATH=src python -m informes.escribir_informe` y `python -m informes.exportar_pdf`.
- PDF: 12 cuadernos más el informe. Carta. La tabla de pozos del informe va en página apaisada. Chrome parte las líneas largas de código; no recorta el hash.
- Auditoría: `datasets/en_uso/BES-jun/docs/revision_notebooks_auditoria.md`. Consultas: `datasets/en_uso/BES-jun/docs/consultas_tecnicas_pendientes.md`.
- El expediente sigue Listo para revisión. No está Completo. No se movió a `procesadas/`.

## 2026-10-20 · Auditoría integral de los 12 cuadernos y exportación HTML/PDF verificada
- Respaldo previo: `datasets/en_uso/BES-jun/logs/respaldo_previo_a_auditoria/` (12 `.ipynb`, 12 PDF, PDF del informe, manifiesto SHA-256).
- Los 12 cuadernos se reescribieron con estructura completa (portada, objetivos con criterios ejecutables, desarrollo, Limitaciones, Referencias) y se ejecutaron sin error. Cuadernos 05 y 06 nuevos; consulta CT-10 añadida.
- Exportación: cuaderno → HTML (nbconvert) → PDF (Chrome). `PYTHONPATH=src python -m informes.pipeline_cuadernos`. Solo se promueve lo que pasa todas las verificaciones.
- Resultado: 12 de 12 verificados (contenido, ejecución, HTML, PDF). `pytest`: 39 passed. Controles negativos: 5 de 5 detectados.
- Verificación: se compara en orden visual (Chrome escribe las tablas después en el flujo del PDF). Defecto real corregido: cabeceras partidas a mitad de palabra.
- `pdf/informes/informe_analisis_BES-jun.pdf` sin cambios (SHA-256 `431e7fe7…d9c19`, igual al respaldo).
- No ejecutar `informes/exportar_pdf.py` (regenera el PDF del informe).
- Informe: `docs/revision_notebooks_auditoria.md`. Procedimiento: `docs/procedimiento_exportacion_cuadernos.md`.
- Sigue Listo para revisión (no Completo): CT-01…CT-10 y P-14 abiertas; sin advertencia de dominio observado en el código.

## 2026-10-20 · Cierre computacional de BES-jun, sin aprobación operacional
- El informe y `docs/reglas_candidatas.md` decían que QF-084 activaba RC-BES-01. El código ya daba RC-BES-03 con el límite escalado (10500 BFPD a 63 Hz). Se corrigió la fuente del informe. Prueba de regresión añadida.
- Evaluador `evaluacion.motor.evaluar` y paquete `datasets/en_uso/BES-jun/integracion/`. Ninguna regla aprobada. `promover()` no mueve la carpeta.
- Informe PDF regenerado a propósito (SHA-256 `f17219a6…cc903`). El anterior sigue en el respaldo de la auditoría de cuadernos.
- `exportar_pdf.exportar()` ahora se niega a correr.
- pytest: 53 passed. BES-jun sigue en `en_uso`. No se abrieron RB-1521 ni RB-IA-2191.
- Reporte: `datasets/en_uso/BES-jun/docs/reporte_cierre_computacional.md`.

## 2026-10-20 · Validación estricta, CT-06 y AutoTest de BES-jun
- Línea base, antes de corregir: 53 passed en 10.11 s (`logs/respaldo_previo_a_autotest/`).
- El motor 0.2.0 valida el contrato 1.1.0 antes de calcular. Una frecuencia textual ya no produce TypeError: la respuesta es `entrada_invalida`.
- RC-BES-04 cita CT-06. CT-09 queda en la tolerancia entre Q* y el caudal medido.
- El informe consolidado incluye la elasticidad de las diez entradas y las derivadas de las tres TVD. PDF: SHA-256 `9e46c9cfe8e91ec6fca20486ba09f5dd0e8142152bc4452cba9a7bcedcc5b836`.
- AutoTest: 76/76, 0 fallos, 11.835 s. El primer intento del ejecutor falló por el nombre del argumento del gancho de pytest (`reporte` en vez de `report`); se corrigió el ejecutor, no las reglas.
- SHA-256 de `entrada/BES_jun.xlsx` sin cambios: `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`.
- BES-jun sigue en `en_uso`. Ninguna regla aprobada. No se abrieron RB-1521 ni RB-IA-2191.
- Informe: `datasets/en_uso/BES-jun/docs/informe_correcciones_autotest_BES-jun.md`.

## 2026-10-20 · Cierre técnico del software de BES-jun
- Línea base de esta pasada: 76 passed en 11.59 s (`logs/respaldo_previo_a_cierre/`).
- Contrato 1.2.0 y motor 0.3.0. Una variable repetida y una clave JSON repetida se rechazan. Los límites, la curva y las etapas no se sustituyen en modo operacional. La salida de un dataset ajeno cumple el esquema y deja `dataset_evaluado` en nulo.
- AutoTest: 85/85, 0 fallos, 11.805 s. Reporte: `datasets/en_uso/BES-jun/logs/autotest_reporte.md`.
- Informe PDF SHA-256 `159353755253caae48f1e1784c6689115c71ed6671d45f399f36d341ce812266`. Doce HTML y doce PDF regenerados, 0 errores.
- Excel sin cambios: `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`.
- No se eliminaron archivos. Tres documentos quedaron marcados como históricos. BES-jun sigue en `en_uso`. Ninguna regla aprobada.
- Informe: `datasets/en_uso/BES-jun/docs/informe_cierre_tecnico_BES-jun.md`.

## 2026-10-20 · Robustez del motor y comprobación físico-matemática
- Línea base: 85 passed en 11.85 s (`logs/respaldo_previo_a_robustez/`).
- Un nombre de variable enviado como lista producía `TypeError`. Una fecha o un escenario numéricos se copiaban a campos de texto. Contrato 1.3.0 y motor 0.4.0: esos casos salen como `entrada_invalida` y cumplen el esquema.
- La excepción imprevista queda en `logs/incidentes.jsonl`. La respuesta no lleva la traza.
- La celda de PIP y la hipótesis hidrostática simple tienen signos opuestos. No se cambió la fórmula. CT-03 sigue abierta.
- AutoTest: 123/123, 0 fallos, 12.847 s. Informe PDF SHA-256 `25cbc343c28df4705fd5dc36796f1f5fc0972c6e0240582de3484a557a2fabbb`.
- Excel sin cambios. BES-jun sigue en `en_uso`. Ninguna regla aprobada.
- Informe: `datasets/en_uso/BES-jun/docs/informe_robustez_y_validacion_fisica_BES-jun.md`.

## 2026-10-20 · Validación integral de BES-jun
- Línea base: 123 passed en 12.36 s (`logs/respaldo_previo_a_validacion_integral/`). Excel `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`.
- Motor 0.4.1, contrato 1.3.0. Una curva `[123]`, un campo extra en un parámetro de escenario, un identificador vacío y una fecha no ISO quedan en `entrada_invalida` y no ejecutan fórmulas.
- E-05: la celda y la hidrostática simple difieren 51.3, 38.6, 51.1, 41.2 y 41.1 ft en los cinco pozos. La fórmula no se cambió. CT-03 sigue abierta.
- AutoTest: 151/151, 0 fallos, 13.198 s. Informe PDF SHA-256 `7457125b457fbf8ed446f7ca1af97ece98faa089ace9dfea959e4bcf98c9afbe`.
- Los doce cuadernos no se regeneraron. BES-jun sigue en `en_uso`. Ninguna regla aprobada. No se abrieron RB-1521 ni RB-IA-2191.
- Informe: `datasets/en_uso/BES-jun/docs/informe_validacion_integral_BES-jun.md`.

## 2026-10-20 · Cierre de curvas y catastro de BES-jun
- Línea base: 151 passed en 13.54 s (`logs/respaldo_previo_a_cierre_curvas/`). La curva 0, 200, 100 BFPD llegaba a los tres modelos y salía `no_evaluable`.
- Motor 0.4.2, contrato 1.3.0. Ese retroceso de caudal queda en `entrada_invalida` y no calcula. Las cinco curvas de la hoja no se reordenaron. QF-084 sigue en RC-BES-03 con máximo 10500 BFPD a 63 Hz.
- Catastro: 20 fórmulas únicas, 14 utilizadas en resultados, 15 con consistencia matemática, 0 con validación externa, 2 con discrepancia (E-05 y E-07). PDF de 18 páginas.
- AutoTest: 172/172, 0 fallos, 17.977 s. Excel sin cambios: `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`.
- BES-jun sigue en `en_uso`. Ninguna regla aprobada. No se abrieron RB-1521 ni RB-IA-2191.
- Informe: `datasets/en_uso/BES-jun/docs/informe_cierre_curvas_y_catastro_BES-jun.md`.

## 2026-10-21 · Auditoría de PIP en BES-jun
- Se leyó `Copia de FINAL BES-jun.xlsx` sin guardarlo. La huella sigue `ccb5a738baea13321993e8b6eccefd6cac90ecda86b1c4b9181f897fcfa83f85`. `pip_en_ft` no se modificó.
- En las cinco hojas el sensor está más profundo que el intake y la celda suma esa columna. El rótulo del gradiente dice `psi*ft`; la aritmética es psi/ft. La procedencia de la presión queda en «No confirmado».
- Diez pruebas en `tests/test_auditoria_pip.py`. Informe: `datasets/en_uso/BES-jun/docs/informe_auditoria_pip_BES-jun.md`.
- No se cambió el signo. BES-jun sigue en `en_uso`. Ninguna regla aprobada.
