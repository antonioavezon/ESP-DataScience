# Auditoría de la consolidación · BES-jun

Fecha: 2026-10-20. Solo problemas comprobados en el código o en los documentos, no huecos rellenados para justificar trabajo.

| Elemento | Situación observada | Problema | Impacto | Acción |
|---|---|---|---|---|
| Informe `escribir_informe.py` | La tabla ya llamaba a `comparar_caudal_con_limites` (escalado) y mostraba RC-BES-03. El párrafo decía que QF-084 superaba el máximo y que RC-BES-01 se activaba solo ahí. | Inconsistencia documental confirmada: el texto no salía de la misma función que la tabla. | Un lector del PDF tomaba por alerta vigente una comparación entre 63 Hz y 60 Hz. | El párrafo se genera ahora con la función. Prueba: `test_el_informe_no_recupera_la_clasificacion_vieja_de_qf084`. |
| `docs/reglas_candidatas.md` | Describía la evidencia de RC-BES-01 como el caso real de QF-084 (10301 contra 10000). | El mismo desfase, en la ficha de la regla. | La regla candidata quedaba documentada al revés que el código. | El Markdown se regenera desde `reglas.catalogo`. |
| Figura de caudal | `graficos._caudal` ya dibuja el máximo escalado y, aparte, el máximo a 60 Hz. | La leyenda del informe no lo decía. | Se leía el círculo hueco como una violación. | Leyenda reescrita. No se cambió el cálculo de la figura. |
| `exportar_pdf.py` | Convertía cuadernos a un HTML resumido y reescribía el PDF del informe. | Podía destruir los PDF íntegros ya verificados. | Pérdida del documento completo. | `exportar()` lanza un error y señala el pipeline vigente. |
| Cuadernos | Doce cuadernos con objetivo propio, ya reescritos. No enlazaban de forma explícita el parámetro que entregan al motor. | Cobertura faltante, no un error de cálculo. | La aplicación no sabía qué cuaderno respalda cada entrada. | Sección «Relación con el sistema de reglas» en los doce, también en el generador (`base.guardar`). |
| Reglas en código | `comparar_caudal_con_limites` ya devolvía RC-BES-03 en las cinco hojas. Las pruebas de escalamiento ya existían. | No había un defecto de cálculo que corregir. | — | Se conservó la función. Se añadió el evaluador y la prueba de que QF-084 no autoriza una orden de operación. |
| Signo del PIP, Hazen-Williams, BS&W, Cluster/Pozo, fechas `TODAY()` | Siguen en CT-01…CT-10. | Ambigüedades abiertas, no errores de transcripción: el código reproduce la hoja. | No se puede aprobar una regla de seguridad. | Se dejaron abiertas. Ver `docs/discrepancias_cientificas.md`. |
| `caudal_y_limites.png` y `head_tabulado.png` | No los produce `guardar_figuras`. | Versiones anteriores sin productor vigente. | El informe podía citarlas por error. | Inventariadas en `docs/linaje_artefactos.md`. No se borraron. El informe usa las seis figuras vigentes. |
