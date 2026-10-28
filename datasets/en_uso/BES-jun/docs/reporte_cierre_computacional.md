# Reporte de cierre computacional · BES-jun

**Documento histórico.** Registra el cierre del 2026-10-20 anterior al contrato 1.2.0. No describe la versión vigente. El cierre técnico actual está en `docs/informe_cierre_tecnico_BES-jun.md`.

Fecha: 2026-10-20. El expediente sigue en `datasets/en_uso/`. No se movió a `procesadas`. No se abrieron RB-1521 ni RB-IA-2191. Ninguna regla quedó aprobada.

## 1. Diagnóstico

Los doce cuadernos, los modelos y las reglas ya clasificaban las cinco hojas como RC-BES-03 cuando el límite se lleva a la frecuencia de operación. El informe consolidado y `docs/reglas_candidatas.md` todavía decían que QF-084 activaba RC-BES-01 por comparar 10301 BFPD a 63 Hz con 10000 BFPD a 60 Hz. El cálculo `10000 × 63 / 60 = 10500` ya estaba en el código. Faltaban el evaluador, los contratos y la ficha única. `asesor-esp/` es el esqueleto de la aplicación y no se le copiaron fórmulas (DEC-004).

## 2. Archivos que cambiaron de verdad

- Corregidos en su fuente: `src/informes/escribir_informe.py`, `src/reglas/catalogo.py` (y el Markdown que genera), `src/informes/exportar_pdf.py` (ahora se niega a correr).
- Nuevos: `src/evaluacion/`, `src/catalogo/variables_bes_jun.py`, `src/integracion/construir_paquete.py`, `src/ciclo/promocion.py`, `src/informes/ficha_maestra.py`, `src/informes/exportar_documento.py`, `tests/test_evaluacion_integracion.py`.
- Generados: `integracion/`, `docs/ficha_maestra_BES-jun.md`, `docs/catalogo_variables_BES-jun.md`, `docs/linaje_artefactos.md`, el informe Markdown/HTML/PDF, los PDF de la ficha, de la guía y de la capa de lenguaje, y la sección de reglas en los doce cuadernos.
- En la raíz del proyecto: `docs/guia_procesamiento_datasets.md`, `docs/arquitectura_funcional.md`, `docs/estado_proyecto.md`, `docs/hoja_de_ruta.md` y DEC-004 en `docs/decisiones.md`.

## 3. Corregido

La clasificación de QF-084 es RC-BES-03 en el código, en las pruebas, en el informe, en la ficha y en el JSON de ejemplo. La frase vieja del informe quedó retirada y el PDF la cita como versión anterior. `exportar_pdf` ya no puede pisar los PDF de los cuadernos.

## 4. Pendiente

CT-01 a CT-10, P-14, identidad Cluster/Pozo, aprobación de reglas, curva de fabricante para RC-BES-04, y el aviso de extrapolación dentro del modelo (el evaluador avisa; la ecuación no). Dos figuras huérfanas, sin borrar. Ver `docs/discrepancias_cientificas.md`.

## 5. Modelos

`M-BES-FLUIDO`, `M-BES-BALANCE`, `M-BES-INTERSECCION`, versión `transcripcion-1`.

## 6. Reglas candidatas

RC-BES-01, RC-BES-02 y RC-BES-03, estado `pendiente_validacion`. RC-BES-04, estado `no_evaluable`.

## 7. Reglas aprobadas

Ninguna. `manifiesto.json` trae `reglas_aprobadas: []`.

## 8. Integración

`integracion/`: README, capa lingüística, manifiesto, pozos, variables, modelos, reglas, esquemas de entrada y salida, ejemplo de QF-084.

## 9. Pruebas

`pytest -q`: 53 passed. Incluyen QF-084 → RC-BES-03, el máximo exacto de 10500, un caudal por encima que avisa sin ordenar, caudal ausente, unidad incompatible, dataset y pozo desconocidos, versión incompatible, 80 Hz fuera del dominio observado, RC-BES-04 no evaluable, y el rechazo de una recomendación operacional no autorizada.

## 10. Validación

Reproducción de la caché de la hoja. No es validación independiente ni aprobación operacional.

## 11. HTML y PDF

Doce HTML y doce PDF en `pdf/notebooks/`, verificación del pipeline en éxito (0 errores). Informe: `reports/informe_analisis_BES-jun.html` y `pdf/informes/informe_analisis_BES-jun.pdf` (SHA-256 `f17219a6d67f2f153e0d9045fd96c08aea85bdc8108fdad9bbb8a9ef841cc903`). El PDF anterior sigue en `logs/respaldo_previo_a_auditoria/`. Ficha, guía de integración y capa de lenguaje en `pdf/informes/`.

## 12. Estado del dataset

`validacion_pendiente`, en `en_uso`.

## 13. Para moverlo a procesadas

Hace falta revisión humana, respuesta de las consultas que afectan a las reglas, una aprobación con responsable y fecha, y una autorización explícita de mover la carpeta. `ciclo.promocion.promover` no la mueve.

## 14. Reutilizable

La guía `docs/guia_procesamiento_datasets.md`: estados, integridad, ficha, reglas con estado, contratos y promoción manual. No los doce cuadernos ni las ecuaciones de esta hoja.

## 15. Riesgos

Leer RC-BES-03 como «el pozo está bien». Usar la fecha `TODAY()` como fecha de medición. Tratar el rango de 56–67 Hz como límite autorizado. Conectar un modelo de lenguaje que reescriba los números.

## 16. Siguiente

Revisión humana de este cierre. No abrir los datasets en espera hasta que se pida. No instalar un modelo de lenguaje en esta etapa.

## Comandos

Desde `datasets/en_uso/BES-jun/`, con el Python del entorno en la raíz del proyecto. Fedora Linux 43.

Pruebas:

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m pytest -q

Evaluar QF-084:

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m evaluacion.motor --dataset BES-jun --pozo QF-084

Regenerar el paquete, la ficha y el catálogo de reglas:

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m integracion.construir_paquete

Regenerar el informe (también reescribe las figuras vigentes):

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -m informes.escribir_informe

PDF del informe, a partir de ese Markdown:

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -c "from pathlib import Path; from informes.exportar_documento import exportar; r=Path('.'); exportar(r/'reports/informe_analisis_BES-jun.md', r/'reports/informe_analisis_BES-jun.html', r/'pdf/informes/informe_analisis_BES-jun.pdf')"

Cuadernos, sin reconstruirlos:

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -u -m informes.pipeline_cuadernos

Reconstruir los `.ipynb` desde los módulos borra las salidas guardadas. Solo si se busca eso, y sabiéndolo:

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -u -m informes.pipeline_cuadernos --construir --ejecutar

Comprobar el cierre sin mover la carpeta:

    PYTHONPATH=src /home/antonio/projects/HUC/.venv/bin/python -c "from ciclo.promocion import comprobar; import json; print(json.dumps(comprobar(), ensure_ascii=False, indent=2))"
