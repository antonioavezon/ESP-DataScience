# Incidencias científicas · BES-jun

Fecha: 2026-10-20. Ninguna fórmula de producción se reemplazó para cerrar estas filas. El motor operacional no usa `hipotesis_ct03.py`.

| ID | Ecuación | Problema | Evidencia | Estado | Acción |
|---|---|---|---|---|---|
| SCI-01 | E-05 | Con el sensor más profundo que el intake, el PIP de la celda y la hidrostática `P/grad - (TVD_sensor - TVD_intake)` difieren en `2·(TVD_sensor - TVD_intake)`. | Caso sintético: 200 ft. Pozos: QF-084 51.3 ft, QF-301 38.6 ft, QF-147 51.1 ft, QF-005 41.2 ft, QF-306 41.1 ft. La caché coincide con la celda. Prueba: `test_e05_reproduccion_hidrostatica_y_cinco_pozos`. | Abierta. CT-03. | Un especialista debe fijar la convención de profundidades. No cambiar el signo en el código mientras tanto. |
| SCI-02 | E-07 | La celda usa el exponente 4.8566. El PDF 004-ESPdesign escribe 4.8655. La longitud es la TVD de descarga, no una longitud medida de tubing. | `test_e07_exponentes_de_la_hoja_no_el_pdf` muestra que los dos exponentes no dan la misma pérdida. | Abierta. CT-05. | No unificar exponentes ni longitudes sin la fuente que corresponda al fluido. |
| SCI-03 | E-03 | El rótulo de BS&W es % y la aritmética lo usa como fracción. No se dividió por 100. | Comentario de `densidad_lb_por_galon` y `test_e03_mezcla_lineal_sin_convertir_el_rotulo_porcentual`. | Abierta. CT-02. | Confirmar la unidad del número escrito en las cinco hojas. |
| SCI-04 | E-02 | Coeficientes 0.00066, 0.0000003 y referencia 15.556 °C sin otra fuente en los documentos leídos. | `test_e02_coeficientes_de_la_celda_sin_origen_experimental`. | Abierta. CT-04. | No tratar la reproducción de la celda como ajuste experimental. |
| SCI-05 | E-09 | Las leyes de afinidad y el escalamiento de límites Q ∝ f no tienen curva de banco de estas bombas. | `test_e09_afinidad_con_una_razon_que_no_sale_del_dataset`. Razón de prueba 1.5. | Abierta. CT-08. | RC-BES-01, 02 y 03 siguen en `pendiente_validacion`. |
| SCI-06 | E-10 | La tabla EFF y el origen de la curva de seis puntos no están respaldados como curva de fabricante. | Catálogo RC-BES-04 y CT-06. | Abierta. CT-06. | RC-BES-04 permanece `no_evaluable`. |
| SCI-07 | E-10 | Q* usa una THD cuya fricción depende del caudal medido. No es una predicción independiente ni una tolerancia acordada. | `test_e10_interpolacion_analitica_sin_extrapolacion`. | Abierta. CT-09. | No usar Q* − caudal medido como validación física. |
| SCI-08 | E-04 | El factor 0.052 de la celda y el factor obtenido con constantes SI escritas en el test (0.051948) no son el mismo número. | `test_e04_factor_0_052_y_contraste_con_el_sistema_internacional`. | Registrada. No se sustituye el factor. | Decidir si el modelo de campo debe conservar el redondeo de la hoja. |

Responsable técnico pendiente: quien cierre CT-01 a CT-10. Este expediente no las cierra. P-14 sigue abierta y no cambia estos cálculos.
