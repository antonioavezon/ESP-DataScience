# Catastro maestro de fórmulas · BES-jun

Las cantidades salen de `src/catalogo/catastro_formulas_bes_jun.py`. No se copiaron de un informe anterior. Una fila puede cumplir más de un indicador. Sumar indicadores no da el total.

## Resumen

| Indicador | Cantidad |
|---|---:|
| Total de fórmulas únicas inventariadas | 20 |
| Fórmulas principales E-01 a E-10 | 10 |
| Fórmulas auxiliares adicionales | 4 |
| Fórmulas realmente utilizadas | 14 |
| Fórmulas implementadas, pero no utilizadas en resultados | 1 |
| Fórmulas solamente documentadas | 4 |
| Fórmulas matemáticamente verificadas | 15 |
| Fórmulas con consistencia física condicionada | 5 |
| Fórmulas con validación física externa suficiente | 0 |
| Fórmulas pendientes de validación experimental | 12 |
| Fórmulas con discrepancias identificadas | 2 |
| Hipótesis alternativas no activas | 2 |

No hay conversión de unidades en el motor: una unidad distinta se rechaza. El bloque eléctrico de la hoja es un solo ítem documentado, no un conjunto de ecuaciones transcritas. HYP-CT03 está implementada y el informe la usa para cuantificar la diferencia; no produce PIP, THD ni Q*. HYP-PUNTO-FIJO vive en el cuaderno 04b y no es una función del motor.

Discrepancias identificadas: E-05, signo de PIP frente a la hidrostática simple; E-07, exponente 4.8566 de la celda frente a 4.8655 del PDF y longitud igual a la TVD de descarga. El factor 0.052 frente a 0.051948 queda en la ficha de E-04 como redondeo de la celda, no como discrepancia que cambie la fórmula.

## Matriz de dependencias

Variable de operador o de ficha, ecuación, modelo, resultado, regla y pozos. Una regla no hereda el estado «verificada» de la ecuación que escala su umbral.

| Variable | Ecuación | Modelo | Resultado | Regla | Pozos |
|---|---|---|---|---|---|
| api_deg, temperatura_c, bsw_numero, densidad del agua | E-01, E-02, E-03, E-04 | M-BES-FLUIDO | gradiente psi/ft | ninguna de forma directa | las cinco hojas |
| presion_sensor_psi, TVD intake y sensor, gradiente | E-05 | M-BES-BALANCE | PIP ft | ninguna como umbral; CT-03 abierta | las cinco hojas |
| thp_psi, gradiente | E-06 | M-BES-BALANCE | THP ft | ninguna | las cinco hojas |
| caudal medido, ID, TVD de descarga | E-07 | M-BES-BALANCE | fricción ft | ninguna como umbral; CT-05 abierta | las cinco hojas |
| TVD de descarga, fricción, THP ft, PIP ft | E-08 | M-BES-BALANCE | THD ft | ninguna | las cinco hojas |
| curva, frecuencia, etapas, límites a 60 Hz | E-09 | M-BES-INTERSECCION y la comparación de reglas | curva escalada y límites a la frecuencia | RC-BES-01, RC-BES-02, RC-BES-03, pendientes | las cinco hojas |
| THD y curva escalada | E-10 | M-BES-INTERSECCION | Q* | ninguna como umbral; CT-06 y CT-09 | las cinco hojas |
| cono de eficiencia y columna EFF | no hay ecuación activa | ninguno | no evaluable | RC-BES-04 | ninguno |

RC-BES-01, RC-BES-02 y RC-BES-03 comparan el caudal medido con límites escalados por E-09. Siguen en `pendiente_validacion` aunque E-09 tenga la álgebra comprobada. RC-BES-04 no depende de una ecuación activa y sigue `no_evaluable`.

## Resultados de las cinco hojas

Medido, calculado y caché. La diferencia de PIP es celda menos hipótesis y no está redondeada en el JSON.

| Pozo | Q medido | Hz | PIP celda ft | Δ PIP ft | THD ft | Q* | Regla | Máximo a f BFPD |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| QF-084 | 10301 | 63 | 1714.496 | 51.291 | 2083.217 | 10535.167 | RC-BES-03 | 10500 |
| QF-301 | 8767 | 57 | 1558.042 | 38.627 | 1971.955 | 8280.859 | RC-BES-03 | 9500 |
| QF-147 | 7728 | 56 | 1920.729 | 51.060 | 1517.209 | 7360.156 | RC-BES-03 | 9333 |
| QF-005 | 7116 | 67 | 1891.210 | 41.247 | 1592.463 | 7802.608 | RC-BES-03 | 8933 |
| QF-306 | 5419 | 62 | 1422.325 | 41.078 | 1814.511 | 5503.034 | RC-BES-03 | 8267 |

Q* se compara con la caché de Excel en el JSON (`diferencia_q_estrella_menos_cache_bfpd`). Esa diferencia mide la transcripción, no la validez física. El caudal medido es otro número.

## Fichas

### E-01 · Gravedad específica desde °API

- **fenomeno.** Gravedad específica del petróleo a 60 °F
- **expresion.** sg = 141.5 / (131.5 + API)
- **variables.** api_deg
- **unidades.** entrada °API; salida adimensional
- **origen.** Celda de gravedad del petróleo a 60 °F, por ejemplo QF-554H!B96
- **fuente_cientifica.** Definición API usada por la celda. No hay densidad medida de este crudo en el expediente.
- **modulo.** src/modelo_deterministico/fluidos_bes_jun.py
- **funcion.** modelo_deterministico.fluidos_bes_jun.gravedad_especifica_api
- **notebooks.** 02 y 04
- **dataset.** BES-jun
- **parametros.** ninguno además del °API
- **hipotesis.** El número de la celda es °API y la definición API aplica.
- **dominio.** API > -131.5 para que el denominador sea positivo
- **verificacion_analitica.** A 10 °API el cociente es 1. La salida es adimensional.
- **oraculo.** tests/test_verificacion_ecuaciones.py::_sg_api
- **verificacion_fisica.** Al subir °API, sg baja. No hay ensayo de densidad.
- **resultados.** En las cinco hojas el °API escrito es 12. La cadena reproduce la caché del gradiente, que depende de esta sg.
- **diferencias.** Ninguna frente a la definición. No hay un valor de laboratorio para restar.
- **tolerancia.** pytest.approx, relativa 1e-6
- **estado_matematico.** consistencia matemática comprobada
- **estado_fisico.** fundamentada bajo la definición API; no mide este crudo
- **estado_experimental.** pendiente de validación externa
- **consecuencia_de_error.** Arrastra densidad, gradiente, PIP, THD y Q*.
- **reglas_dependientes.** Ninguna compara sg. RC-BES-01 a 03 solo corren si la cadena es calculable.
- **recomendacion_posterior.** Medir densidad del fluido a 60 °F.
- **prueba.** test_e01_definicion_oraculo_y_monotonia
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** ninguna

### E-02 · Corrección térmica de la gravedad

- **fenomeno.** Gravedad específica a la temperatura de fondo
- **expresion.** sg_T = sg_60 - 0.00066*(T-15.556) + 0.0000003*(T-15.556)^2
- **variables.** sg_60, temperatura_c
- **unidades.** T en °C; sg adimensional
- **origen.** Celda B98 de cada hoja
- **fuente_cientifica.** Solo la celda. Los coeficientes 0.00066, 0.0000003 y 15.556 no tienen otra fuente en los documentos leídos.
- **modulo.** src/modelo_deterministico/fluidos_bes_jun.py
- **funcion.** modelo_deterministico.fluidos_bes_jun.gravedad_oil_a_temperatura
- **notebooks.** 02 y 04
- **dataset.** BES-jun
- **parametros.** 0.00066, 0.0000003, 15.556
- **hipotesis.** T está en °C y los coeficientes de la celda se transcriben sin reinterpretarlos.
- **dominio.** Alrededor de la temperatura escrita. Fuera de ese entorno el polinomio no está justificado.
- **verificacion_analitica.** En T = 15.556 el resultado es sg_60. La pendiente central de ±1 °C es -0.00066.
- **oraculo.** tests/test_verificacion_ecuaciones.py::_sg_temperatura
- **verificacion_fisica.** No hay ensayo. Reproducir la celda no valida los coeficientes.
- **resultados.** Entra en la densidad de las cinco hojas. La caché del fluido coincide con la transcripción.
- **diferencias.** Ninguna frente a la celda. CT-04 pide el origen de las constantes.
- **tolerancia.** identidad en 15.556; pendiente con absoluta 1e-6
- **estado_matematico.** consistencia matemática comprobada
- **estado_fisico.** dependiente de parámetros empíricos no validados
- **estado_experimental.** pendiente de validación externa
- **consecuencia_de_error.** Cambia la densidad y, con ella, el gradiente y todo el balance.
- **reglas_dependientes.** Indirecta: si el fluido no es calculable, no hay clasificación de caudal.
- **recomendacion_posterior.** Identificar la correlación de donde salieron los tres números.
- **prueba.** test_e02_coeficientes_de_la_celda_sin_origen_experimental
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** CT-04

### E-03 · Densidad de mezcla

- **fenomeno.** Densidad del fluido como mezcla de agua y petróleo
- **expresion.** rho = BSW*rho_agua + (1-BSW)*8.33*sg_T
- **variables.** bsw_numero, densidad_agua_lb_gal, sg_T
- **unidades.** lb/gal. El rótulo de BS&W dice % y la fórmula no divide por 100.
- **origen.** Celda B100
- **fuente_cientifica.** Aritmética de la celda. No hay un análisis de fluido independiente.
- **modulo.** src/modelo_deterministico/fluidos_bes_jun.py
- **funcion.** modelo_deterministico.fluidos_bes_jun.densidad_lb_por_galon
- **notebooks.** 02
- **dataset.** BES-jun
- **parametros.** 8.33, escrito en la celda
- **hipotesis.** El número de BS&W ya es fracción. Mezcla lineal de las dos densidades.
- **dominio.** La función calcula también fuera de 0 a 1 y deja la advertencia al llamador.
- **verificacion_analitica.** BSW = 0 devuelve 8.33*sg. BSW = 1 devuelve la densidad del agua.
- **oraculo.** tests/test_verificacion_ecuaciones.py::_densidad
- **verificacion_fisica.** Con componentes positivos y BSW = 0.4 el resultado queda entre ellos. No se convirtió el rótulo.
- **resultados.** Densidad de las cinco hojas, usada por el gradiente.
- **diferencias.** CT-02: unidad del rótulo frente al uso aritmético.
- **tolerancia.** pytest.approx
- **estado_matematico.** consistencia matemática comprobada
- **estado_fisico.** consistente bajo la hipótesis de mezcla lineal y de BS&W como fracción
- **estado_experimental.** pendiente de validación externa
- **consecuencia_de_error.** Un factor 100 en BS&W cambiaría el gradiente de forma grande.
- **reglas_dependientes.** Indirecta, por la cadena de fluido.
- **recomendacion_posterior.** Confirmar si el número escrito es fracción o porcentaje.
- **prueba.** test_e03_mezcla_lineal_sin_convertir_el_rotulo_porcentual
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** CT-02

### E-04 · Gradiente de presión

- **fenomeno.** Gradiente hidrostático a partir de la densidad
- **expresion.** grad = rho_lb/gal * 0.052
- **variables.** densidad_lb_gal
- **unidades.** psi/ft. 8.34 * 0.052 = 0.43368
- **origen.** Celda B102. El factor 0.052 está escrito. No se usa 0.433/8.34.
- **fuente_cientifica.** Factor de campo de la celda. El contraste SI del test usa 1 lb = 0.45359237 kg, 1 galón US = 3.785411784 L, g = 9.80665, 1 ft = 0.3048 m y 1 psi = 6894.757293168 Pa, y obtiene 0.051948.
- **modulo.** src/modelo_deterministico/fluidos_bes_jun.py
- **funcion.** modelo_deterministico.fluidos_bes_jun.gradiente_psi_por_ft
- **notebooks.** 02
- **dataset.** BES-jun
- **parametros.** 0.052
- **hipotesis.** Se conserva el factor de la celda. El factor SI no lo reemplaza.
- **dominio.** Densidad positiva. El rango de las cinco hojas no es un límite operacional.
- **verificacion_analitica.** Producto escrito 8.34 * 0.052.
- **oraculo.** 8.34 * 0.052 en tests/test_verificacion_ecuaciones.py
- **verificacion_fisica.** El factor SI 0.051948 difiere en menos de 0.0001. La función sigue devolviendo rho*0.052.
- **resultados.** Gradiente de las cinco hojas, cerca de 0.433 psi/ft.
- **diferencias.** 0.052 frente a 0.051948. Registrado como redondeo de la celda, no sustituido.
- **tolerancia.** el factor SI con absoluta 1e-5; la función no se compara contra ese factor para aprobarla
- **estado_matematico.** consistencia matemática comprobada
- **estado_fisico.** consistente bajo el factor de campo 0.052
- **estado_experimental.** pendiente de validación externa
- **consecuencia_de_error.** Escala PIP, THP en pies, THD y Q*.
- **reglas_dependientes.** Indirecta, por el balance.
- **recomendacion_posterior.** Decidir si un modelo futuro en SI debe dejar de usar el redondeo 0.052.
- **prueba.** test_e04_factor_0_052_y_contraste_con_el_sistema_internacional
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** ninguna

### E-05 · PIP en pies

- **fenomeno.** Presión de admisión expresada en pies de columna, con el signo de la celda
- **expresion.** PIP = (P_sensor - (TVD_intake - TVD_sensor)*grad) / grad
- **variables.** presion_sensor_psi, tvd_intake_ft, tvd_sensor_ft, gradiente_psi_ft
- **unidades.** ft
- **origen.** Celda G96, «PIP en (ft)»
- **fuente_cientifica.** La celda. La hipótesis de comparación, no usada por el motor, es P/grad - (TVD_sensor - TVD_intake).
- **modulo.** src/modelo_deterministico/balance_bes_jun.py
- **funcion.** modelo_deterministico.balance_bes_jun.pip_en_ft
- **notebooks.** 02, 04 y 05
- **dataset.** BES-jun
- **parametros.** ninguno oculto
- **hipotesis.** Se transcribe el signo de la celda. No se decide que ese signo sea el hidrostático.
- **dominio.** Gradiente distinto de cero. En las cinco hojas el sensor está más profundo que el intake.
- **verificacion_analitica.** La transcripción independiente _pip_celda coincide con pip_en_ft. La caché coincide dentro de 1e-6 relativo.
- **oraculo.** tests/test_verificacion_ecuaciones.py::_pip_celda y la caché de la hoja
- **verificacion_fisica.** Con el sensor 100 ft más profundo la diferencia algebraica es 200 ft. En los cinco pozos la diferencia es 2*(TVD_sensor-TVD_intake).
- **resultados.** QF-084 51.3 ft, QF-301 38.6 ft, QF-147 51.1 ft, QF-005 41.2 ft, QF-306 41.1 ft de diferencia celda menos hidrostática.
- **diferencias.** Esas cinco diferencias. La caché coincide con la celda, no con la hipótesis.
- **tolerancia.** la diferencia algebraica es exacta dentro de pytest.approx; la caché, relativa 1e-6
- **estado_matematico.** reproducción numérica comprobada y consistencia algebraica de la celda
- **estado_fisico.** discrepancia física confirmada bajo la hipótesis hidrostática simple
- **estado_experimental.** pendiente de validación externa
- **consecuencia_de_error.** El signo mueve la THD en la misma magnitud y Q* en decenas o cientos de BFPD, según el cuaderno 05.
- **reglas_dependientes.** No entra en el umbral de RC-BES-01 a 03. Si el balance no calcula, la regla no se clasifica.
- **recomendacion_posterior.** Cerrar CT-03 con la convención de profundidades. No cambiar el signo en el código antes de eso.
- **prueba.** test_e05_reproduccion_hidrostatica_y_cinco_pozos
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** CT-03

### E-06 · THP en altura

- **fenomeno.** Presión en cabeza de pozo expresada en pies de columna
- **expresion.** THP_ft = THP_psi / gradiente
- **variables.** thp_psi, gradiente_psi_ft
- **unidades.** ft
- **origen.** Celda G98
- **fuente_cientifica.** Equivalencia de la celda. No hay una columna medida aparte.
- **modulo.** src/modelo_deterministico/balance_bes_jun.py
- **funcion.** modelo_deterministico.balance_bes_jun.thp_en_ft
- **notebooks.** 02 y 04
- **dataset.** BES-jun
- **parametros.** el gradiente de E-04
- **hipotesis.** El mismo gradiente de la mezcla convierte psi en ft.
- **dominio.** Gradiente distinto de cero
- **verificacion_analitica.** psi / (psi/ft) = ft.
- **oraculo.** 100/0.4 = 250 en tests/test_verificacion_ecuaciones.py
- **verificacion_fisica.** Duplicar la presión duplica la altura. Duplicar el gradiente la reduce a la mitad.
- **resultados.** THP en pies de las cinco hojas, dentro de la THD.
- **diferencias.** Ninguna frente a la identidad. Hereda la reserva del gradiente.
- **tolerancia.** pytest.approx
- **estado_matematico.** consistencia matemática comprobada
- **estado_fisico.** consistente bajo el gradiente de E-04
- **estado_experimental.** pendiente de validación externa
- **consecuencia_de_error.** Suma directa en la THD.
- **reglas_dependientes.** Indirecta, por la cadena.
- **recomendacion_posterior.** No usar esta altura como medición independiente de la presión.
- **prueba.** test_e06_presion_y_altura_son_inversas_del_gradiente
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** ninguna

### E-07 · Fricción de Hazen-Williams

- **fenomeno.** Pérdida de carga en el tubing, como la escribe la hoja
- **expresion.** (2.083*(100/C)^1.85*(Q/34.3)^1.85/ID^4.8566)*(L/1000), C=120
- **variables.** caudal_bfpd, id_tubing_in, longitud_ft
- **unidades.** Q en BFPD, ID en in, L en ft, salida en ft. L es la TVD de descarga, no una longitud medida.
- **origen.** Celda G100. C = 120 está dentro de la fórmula.
- **fuente_cientifica.** La celda. El PDF 004-ESPdesign escribe el exponente 4.8655. No se unificó.
- **modulo.** src/modelo_deterministico/balance_bes_jun.py
- **funcion.** modelo_deterministico.balance_bes_jun.friccion_hazen_williams_ft
- **notebooks.** 02, 04 y 04b
- **dataset.** BES-jun
- **parametros.** 2.083, 1.85, 34.3, 4.8566, C=120
- **hipotesis.** Se transcriben los exponentes de la celda. No se afirma que Hazen-Williams describa esta mezcla.
- **dominio.** ID positivo y caudal no negativo, como exige evaluar_balance.
- **verificacion_analitica.** Lineal en L, Q^1.85, ID^-4.8566.
- **oraculo.** tests/test_verificacion_ecuaciones.py::_hazen
- **verificacion_fisica.** El mismo caso con exponente 4.8655 no coincide. No hay pérdida medida.
- **resultados.** Fricción de las cinco hojas, con el caudal medido.
- **diferencias.** Exponente 4.8566 de la celda frente a 4.8655 del PDF. Longitud = TVD de descarga.
- **tolerancia.** los dos exponentes no pasan math.isclose con relativa 1e-6
- **estado_matematico.** consistencia matemática comprobada respecto de la celda
- **estado_fisico.** diferencia de fuente identificada; aplicabilidad al fluido sin evidencia suficiente
- **estado_experimental.** pendiente de validación externa
- **consecuencia_de_error.** Entra en la THD y por eso en Q*. El cuaderno 05 la ordena detrás de CT-03.
- **reglas_dependientes.** Indirecta. El caudal que clasifican las reglas es el medido, no esta pérdida.
- **recomendacion_posterior.** No cambiar el exponente ni sustituir la TVD por otra longitud sin la fuente del fluido.
- **prueba.** test_e07_exponentes_de_la_hoja_no_el_pdf
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** CT-05

### E-08 · THD total

- **fenomeno.** Balance de altura que la hoja llama THD TOTAL
- **expresion.** THD = TVD_descarga + friccion + THP_ft - PIP_ft
- **variables.** tvd_descarga_ft, friccion_ft, thp_ft, pip_ft
- **unidades.** ft en los cuatro términos
- **origen.** Celda G102
- **fuente_cientifica.** Suma de la celda. No se afirma que sea el TDH del PDF.
- **modulo.** src/modelo_deterministico/balance_bes_jun.py
- **funcion.** modelo_deterministico.balance_bes_jun.thd_total_ft
- **notebooks.** 02 y 04
- **dataset.** BES-jun
- **parametros.** ninguno
- **hipotesis.** Los cuatro términos ya están en ft y con el signo de la hoja.
- **dominio.** El de los términos. La identidad no los justifica.
- **verificacion_analitica.** thd_total_ft(1000, 10, 20, 30) = 1000.
- **oraculo.** la suma escrita en tests/test_verificacion_ecuaciones.py
- **verificacion_fisica.** Un pie más de TVD, fricción o THP suma un pie. Un pie más de PIP resta un pie. Eso es el signo algebraico.
- **resultados.** THD de las cinco hojas, coincidente con la caché por la transcripción de los términos.
- **diferencias.** Ninguna en la suma. Hereda CT-03 y CT-05.
- **tolerancia.** pytest.approx
- **estado_matematico.** consistencia matemática comprobada
- **estado_fisico.** identidad algebraica; la física queda en los términos
- **estado_experimental.** pendiente de validación externa
- **consecuencia_de_error.** Q* se interpola contra esta THD.
- **reglas_dependientes.** Indirecta, por la calculabilidad de la cadena.
- **recomendacion_posterior.** No presentar la THD como un TDH de fabricante.
- **prueba.** test_e08_el_balance_tiene_los_signos_escritos
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** CT-03, CT-05

### E-09 · Leyes de afinidad de la hoja

- **fenomeno.** Escalar caudal y head de la curva, y los límites de 60 Hz, con la frecuencia
- **expresion.** Q = Q60*(f/f_curva); H = H60*(f/f_curva)^2*etapas. Los límites usan Q(f) = Q(60)*(f/f_base).
- **variables.** caudal y head tabulados, frecuencia_hz, frecuencia_curva_hz, etapas; para límites, limite_minimo_bfpd y limite_maximo_bfpd
- **unidades.** BFPD, ft, Hz, etapas adimensionales
- **origen.** Filas de curva a la velocidad actual y celdas de límites a 60 Hz, por ejemplo J85 = J88*(I85/I88)
- **fuente_cientifica.** La hoja. No hay curva de banco. CT-08.
- **modulo.** src/modelo_deterministico/interseccion_bes_jun.py y src/reglas/candidatas_bes_jun.py
- **funcion.** modelo_deterministico.interseccion_bes_jun.curva_a_velocidad
- **notebooks.** 03, 04 y 05
- **dataset.** BES-jun
- **parametros.** exponentes 1 y 2; f_base 60 Hz cuando la hoja no trae otra
- **hipotesis.** Se transcriben los exponentes. No se afirma que valgan para estas bombas ni para sus límites.
- **dominio.** Frecuencias y etapas positivas. El rango 56–67 Hz es observado, no autorizado.
- **verificacion_analitica.** Razón 1.5, ajena al dataset: caudal por 1.5 y head por 2.25 por etapas. La transformación inversa recupera el punto.
- **oraculo.** el producto escrito en test_e09_afinidad_con_una_razon_que_no_sale_del_dataset
- **verificacion_fisica.** No hay ensayo. La misma relación escala los límites que usan RC-BES-01 a 03.
- **resultados.** Curva a la frecuencia de cada hoja y límites escalados. En QF-084, 10000 BFPD a 60 Hz pasan a 10500 BFPD a 63 Hz.
- **diferencias.** Ninguna frente a la álgebra. La aplicabilidad sigue en CT-08.
- **tolerancia.** pytest.approx
- **estado_matematico.** consistencia matemática comprobada
- **estado_fisico.** formulación de la hoja; no representa por sí sola los límites reales de la bomba
- **estado_experimental.** pendiente de validación externa
- **consecuencia_de_error.** Cambia la curva contra la que se interpola Q* y la clasificación de las tres reglas de caudal.
- **reglas_dependientes.** RC-BES-01, RC-BES-02 y RC-BES-03, por el escalamiento de los límites.
- **recomendacion_posterior.** Curva de fabricante a más de una frecuencia antes de aprobar el escalamiento.
- **prueba.** test_e09_afinidad_con_una_razon_que_no_sale_del_dataset
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** CT-08

### E-10 · Intersección bomba-sistema

- **fenomeno.** Caudal en el que el head de la curva iguala la THD
- **expresion.** MATCH descendente y Q = Qk + (THD-Hk)/(Hk+1-Hk)*(Qk+1-Qk)
- **variables.** thd_total_ft, curva, frecuencia_hz, frecuencia_curva_hz, etapas
- **unidades.** ft y BFPD
- **origen.** Bloque Descarga, «Caudal a producir»
- **fuente_cientifica.** Interpolación de la tabla de seis puntos. No es una curva de fabricante (CT-06) ni una predicción independiente (CT-09).
- **modulo.** src/modelo_deterministico/interseccion_bes_jun.py
- **funcion.** modelo_deterministico.interseccion_bes_jun.caudal_a_producir
- **notebooks.** 04, 04b y 05
- **dataset.** BES-jun
- **parametros.** sin extrapolación
- **hipotesis.** Head estrictamente descendente y caudal estrictamente creciente en la representación admitida. La fricción de la THD usa el caudal medido.
- **dominio.** THD estrictamente entre el primer y el último head de la curva ya escalada. Fuera, no_calculable.
- **verificacion_analitica.** Tramo (0 BFPD, 100 ft) a (100 BFPD, 0 ft), THD = 50 ft, resultado 50 BFPD.
- **oraculo.** tests/test_verificacion_ecuaciones.py::_interpolar
- **verificacion_fisica.** friccion(1000) y friccion(2000) difieren, así que la intersección no es un punto fijo. El cuaderno 04b explora ese punto fijo y no está en el motor.
- **resultados.** Q* de las cinco hojas, comparado con la caché por la transcripción, no con una medición independiente.
- **diferencias.** Q* menos caudal medido no es un error del algoritmo. CT-09 no fija una tolerancia.
- **tolerancia.** el caso analítico con pytest.approx; fuera de tabla, estado no_calculable
- **estado_matematico.** consistencia matemática comprobada
- **estado_fisico.** interpolación de la tabla; no es predicción del caudal del pozo
- **estado_experimental.** pendiente de validación externa
- **consecuencia_de_error.** Publicar Q* como caudal futuro. Las reglas de caudal no usan Q* como umbral.
- **reglas_dependientes.** Ninguna lo usa como umbral. La cadena tiene que ser calculable para clasificar.
- **recomendacion_posterior.** No sustituir el algoritmo por el punto fijo del cuaderno 04b.
- **prueba.** test_e10_interpolacion_analitica_sin_extrapolacion
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** CT-06, CT-09

### AUX-ELAST · Elasticidad relativa por diferencia central

- **fenomeno.** Peso local de una entrada sobre Q*
- **expresion.** epsilon = (Q(x*(1+d)) - Q(x*(1-d))) / (2*d*Q(x)), d = 0.01
- **variables.** una entrada de ENTRADAS_RELATIVAS y la cadena completa
- **unidades.** adimensional; también BFPD por 1 %
- **origen.** src/analisis/sensibilidad_local.py
- **fuente_cientifica.** Definición numérica. No es una ley de la bomba ni una incertidumbre.
- **modulo.** src/analisis/sensibilidad_local.py
- **funcion.** analisis.sensibilidad_local.elasticidad_relativa
- **notebooks.** 04 y 04b
- **dataset.** BES-jun
- **parametros.** paso relativo 0.01
- **hipotesis.** Q* es calculable en los tres puntos. El paso no sale del tramo de la curva.
- **dominio.** Entradas distintas de cero, porque el paso es relativo.
- **verificacion_analitica.** Para una respuesta lineal Q = k*x la elasticidad es 1.
- **oraculo.** tests/test_catastro_formulas.py, expresión (qp-qm)/(2*d*q0)
- **verificacion_fisica.** No aplica como ley. El signo observado en las hojas no se toma como causalidad.
- **resultados.** El informe publica la elasticidad de diez entradas. La mayor en magnitud media es la frecuencia.
- **diferencias.** No es una discrepancia física.
- **tolerancia.** pytest.approx contra el oráculo que llama a q_estrella y combina aparte
- **estado_matematico.** consistencia matemática comprobada
- **estado_fisico.** indicador numérico, no una ley física
- **estado_experimental.** no aplica
- **consecuencia_de_error.** Ordenar mal qué entrada pesa sobre Q*.
- **reglas_dependientes.** Ninguna.
- **recomendacion_posterior.** No usar la elasticidad como intervalo de confianza.
- **prueba.** test_aux_elasticidad_tiene_oraculo_independiente_de_la_combinacion
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** ninguna

### AUX-DERIV · Derivada de Q* por pie de TVD

- **fenomeno.** Sensibilidad de Q* a una profundidad
- **expresion.** dQ/dTVD = (Q(x+paso) - Q(x-paso)) / (2*paso), paso = 1 ft
- **variables.** tvd_descarga_ft, tvd_intake_ft o tvd_sensor_ft
- **unidades.** BFPD/ft
- **origen.** src/analisis/sensibilidad_local.py
- **fuente_cientifica.** Diferencia central. No es un límite de asentamiento.
- **modulo.** src/analisis/sensibilidad_local.py
- **funcion.** analisis.sensibilidad_local.derivada_por_pie
- **notebooks.** 04 y 04b
- **dataset.** BES-jun
- **parametros.** paso 1 ft
- **hipotesis.** La cadena sigue calculable a ±1 ft.
- **dominio.** Las tres TVD de la hoja
- **verificacion_analitica.** El cociente escrito coincide con la función.
- **oraculo.** tests/test_catastro_formulas.py
- **verificacion_fisica.** No es una ley. Un pie de descarga, de intake y de sensor no pesan igual porque entran en términos distintos.
- **resultados.** El informe publica las tres derivadas por pozo.
- **diferencias.** Ninguna frente a la definición.
- **tolerancia.** pytest.approx
- **estado_matematico.** consistencia matemática comprobada
- **estado_fisico.** indicador numérico, no una ley física
- **estado_experimental.** no aplica
- **consecuencia_de_error.** Atribuir el mismo efecto a las tres profundidades.
- **reglas_dependientes.** Ninguna.
- **recomendacion_posterior.** No convertir la derivada en una instrucción de mover el equipo.
- **prueba.** test_aux_derivada_por_pie_tiene_oraculo
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** ninguna

### AUX-MC · Curvatura mínima del survey

- **fenomeno.** TVD y dogleg a partir de MD, inclinación y azimut
- **expresion.** beta = arccos(cos(di) - sin(i1)*sin(i2)*(1-cos(da))); factor = (2/beta)*tan(beta/2); TVD suma (dMD/2)*(cos i1 + cos i2)*factor
- **variables.** md_ft, inclinacion_deg, azimut_deg
- **unidades.** ft y grados; dogleg en °/100 ft
- **origen.** src/analisis/calidad.py. Método de industria usado como control de las columnas de la hoja.
- **fuente_cientifica.** Método de curvatura mínima. En este expediente controla la columna Vertical, no diseña la BES.
- **modulo.** src/analisis/calidad.py
- **funcion.** analisis.calidad.curvatura_minima
- **notebooks.** 01
- **dataset.** BES-jun
- **parametros.** ninguno de la BES
- **hipotesis.** Las estaciones vienen ordenadas por MD y los ángulos están en grados.
- **dominio.** Survey de cada hoja. Un tramo vertical de inclinación nula da dogleg nulo.
- **verificacion_analitica.** Pozo vertical sintético: TVD = MD y dogleg = 0.
- **oraculo.** tests/test_catastro_formulas.py, TVD = MD
- **verificacion_fisica.** La columna de la hoja coincide con el recálculo dentro de la tolerancia de redondeo del test de survey. Eso es contraste con la hoja, no un ensayo nuevo.
- **resultados.** El cuaderno 01 y test_survey_geometria_y_curvatura_minima.
- **diferencias.** Las que reporte el test de survey, acotadas por su tolerancia.
- **tolerancia.** la del test de survey para la hoja; el caso vertical es igualdad aproximada
- **estado_matematico.** consistencia matemática comprobada en un caso analítico
- **estado_fisico.** método geométrico estándar, usado aquí como control de la hoja
- **estado_experimental.** no aplica a la BES
- **consecuencia_de_error.** Dudar de una TVD de equipo por un error de survey, no por la bomba.
- **reglas_dependientes.** Ninguna.
- **recomendacion_posterior.** No usar este control para corregir la TVD escrita del equipo.
- **prueba.** test_aux_curvatura_minima_en_pozo_vertical
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** ninguna

### AUX-TVD · Interpolación lineal de TVD

- **fenomeno.** TVD a una MD intermedia del survey
- **expresion.** TVD = TVD0 + (MD-MD0)/(MD1-MD0)*(TVD1-TVD0), sin extrapolar
- **variables.** md_ft y vertical_ft de las estaciones, MD del equipo
- **unidades.** ft
- **origen.** src/analisis/calidad.py, np.interp sobre el survey
- **fuente_cientifica.** Interpolación lineal. No sustituye la TVD escrita del equipo.
- **modulo.** src/analisis/calidad.py
- **funcion.** analisis.calidad.interpolar_tvd
- **notebooks.** 01
- **dataset.** BES-jun
- **parametros.** ninguno
- **hipotesis.** El survey está ordenado por MD.
- **dominio.** MD entre la primera y la última estación. Fuera, None.
- **verificacion_analitica.** Estaciones (0, 0) y (100, 50): a MD 50 la TVD es 25.
- **oraculo.** 25 escrito en tests/test_catastro_formulas.py
- **verificacion_fisica.** Sirve para comparar, no para reemplazar la TVD de descarga, intake o sensor.
- **resultados.** verificar_tvd_de_equipos en el cuaderno 01 y en los tests.
- **diferencias.** dif_ft de cada equipo, publicada por esa función, no absorbida en la ficha.
- **tolerancia.** el caso analítico con pytest.approx
- **estado_matematico.** consistencia matemática comprobada
- **estado_fisico.** herramienta de contraste, no una corrección de la ficha
- **estado_experimental.** no aplica
- **consecuencia_de_error.** Tomar la TVD interpolada como si reemplazara la de la hoja.
- **reglas_dependientes.** Ninguna.
- **recomendacion_posterior.** Mantener la TVD de la hoja como entrada del balance.
- **prueba.** test_aux_interpolacion_de_tvd
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** ninguna

### HYP-CT03 · PIP si el sensor más profundo aumenta la columna

- **fenomeno.** Comparación hidrostática, no la celda de BES-jun
- **expresion.** PIP = P/grad - (TVD_sensor - TVD_intake)
- **variables.** presion_sensor_psi, tvd_intake_ft, tvd_sensor_ft, gradiente
- **unidades.** ft
- **origen.** src/modelo_deterministico/hipotesis_ct03.py
- **fuente_cientifica.** Hipótesis de trabajo para CT-03. evaluar no la llama.
- **modulo.** src/modelo_deterministico/hipotesis_ct03.py
- **funcion.** modelo_deterministico.hipotesis_ct03.pip_ft_si_el_sensor_esta_mas_profundo
- **notebooks.** el informe consolidado la cita como comparación; los cuadernos usan el intercambio de TVD
- **dataset.** BES-jun
- **parametros.** ninguno
- **hipotesis.** La presión de la columna crece hacia abajo y el sensor está a otra TVD que el intake.
- **dominio.** Gradiente distinto de cero
- **verificacion_analitica.** Restada de la celda da 2*(sensor-intake).
- **oraculo.** tests/test_verificacion_ecuaciones.py::_pip_hidrostatica
- **verificacion_fisica.** Cuantifica la diferencia. No elige el signo.
- **resultados.** Solo comparación. No entra en Q* ni en las reglas.
- **diferencias.** Las cinco diferencias de E-05.
- **tolerancia.** pytest.approx
- **estado_matematico.** consistencia matemática comprobada como expresión aislada
- **estado_fisico.** hipótesis de comparación, no modelo activo
- **estado_experimental.** pendiente de validación externa
- **consecuencia_de_error.** Sustituir la celda por esta expresión sin cerrar CT-03.
- **reglas_dependientes.** Ninguna.
- **recomendacion_posterior.** Dejarla fuera del motor hasta una decisión externa.
- **prueba.** test_e05_reproduccion_hidrostatica_y_cinco_pozos
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** CT-03

### HYP-PUNTO-FIJO · Intersección autoconsistente

- **fenomeno.** Q* tal que la fricción se evalúa en ese mismo Q*
- **expresion.** iterar Q hasta |Q* - Q| < 0.01 BFPD, partiendo del caudal medido
- **variables.** la hoja completa, vía q_estrella
- **unidades.** BFPD
- **origen.** Función punto_fijo escrita en src/informes/cuadernos/nb04b.py. No está en el motor.
- **fuente_cientifica.** Diagnóstico del cuaderno 04b. Converge en las cinco hojas y no se adopta.
- **modulo.** src/informes/cuadernos/nb04b.py
- **funcion.** None
- **notebooks.** 04b
- **dataset.** BES-jun
- **parametros.** tolerancia 0.01 BFPD, máximo 100 iteraciones
- **hipotesis.** Que la fricción deba usar Q* y no el caudal medido. No está decidido.
- **dominio.** Las cinco hojas del cuaderno. No es el dominio del motor.
- **verificacion_analitica.** No hay oráculo independiente en la suite: el procedimiento vive en el texto del cuaderno.
- **oraculo.** no hay función importable distinta del cuaderno
- **verificacion_fisica.** El cuaderno informa que acerca Q* al caudal medido y dice que eso no valida el modelo.
- **resultados.** El cuaderno 04b publica la brecha antes y después. Esos números no alimentan las reglas.
- **diferencias.** Q* de la hoja frente al punto fijo. No se usa para corregir la hoja.
- **tolerancia.** 0.01 BFPD de parada, solo dentro del cuaderno
- **estado_matematico.** no verificada como función del motor
- **estado_fisico.** hipótesis de trabajo, no modelo activo
- **estado_experimental.** pendiente de validación externa
- **consecuencia_de_error.** Reemplazar E-10 por esta iteración.
- **reglas_dependientes.** Ninguna.
- **recomendacion_posterior.** Mantenerla en el cuaderno, separada del evaluador.
- **prueba.** None
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** CT-09

### DOC-F02 · Gradiente 0.433 del XLSM

- **fenomeno.** Gradiente de agua dulce citado en otra fuente
- **expresion.** 0.433 psi/ft por gravedad específica, no transcrito
- **variables.** no entra al motor
- **unidades.** psi/ft
- **origen.** src/analisis/catalogo_bes_jun.py, id F-02-F-03, estado fuera del alcance
- **fuente_cientifica.** Otra planilla. BES-jun usa E-04.
- **modulo.** src/analisis/catalogo_bes_jun.py
- **funcion.** None
- **notebooks.** catálogo de fórmulas
- **dataset.** BES-jun
- **parametros.** 0.433
- **hipotesis.** No se aplica a estas hojas.
- **dominio.** ninguno en el motor
- **verificacion_analitica.** No implementada.
- **oraculo.** no hay
- **verificacion_fisica.** No evaluable con el flujo de BES-jun.
- **resultados.** No produce un número del expediente.
- **diferencias.** No se igualó a 0.052.
- **tolerancia.** no aplica
- **estado_matematico.** solamente documentada
- **estado_fisico.** no evaluable con las fuentes usadas por el motor
- **estado_experimental.** no aplica
- **consecuencia_de_error.** Sustituir E-04 por este factor.
- **reglas_dependientes.** Ninguna.
- **recomendacion_posterior.** No copiarla al motor de BES-jun.
- **prueba.** None
- **pozos.** ninguno
- **consultas.** ninguna

### DOC-POTENCIA · Bloque eléctrico y de potencia

- **fenomeno.** Potencia, motor y cable de la hoja, no transcritos
- **expresion.** varias constantes de la hoja (0.746, 0.241 y otras) sin desglosar, porque no hay transcripción
- **variables.** no entran al motor
- **unidades.** no fijadas en el código
- **origen.** src/analisis/catalogo_bes_jun.py, id Potencia-motor-cable
- **fuente_cientifica.** La hoja las contiene. No se contaron como fórmulas separadas porque no están identificadas una a una en el código.
- **modulo.** src/analisis/catalogo_bes_jun.py
- **funcion.** None
- **notebooks.** no hay transcripción
- **dataset.** BES-jun
- **parametros.** no inventariados uno a uno
- **hipotesis.** Quedan fuera hasta conocer el origen de las constantes.
- **dominio.** ninguno en el motor
- **verificacion_analitica.** No implementada. Este ítem es un bloque, no una ecuación.
- **oraculo.** no hay
- **verificacion_fisica.** No evaluable.
- **resultados.** Los promedios con #DIV/0! de QF-549HST no entran en PIP ni en THD.
- **diferencias.** No transcritas.
- **tolerancia.** no aplica
- **estado_matematico.** solamente documentada
- **estado_fisico.** no evaluable con las fuentes usadas por el motor
- **estado_experimental.** no aplica
- **consecuencia_de_error.** Contar cada constante no leída como una fórmula verificada.
- **reglas_dependientes.** Ninguna.
- **recomendacion_posterior.** Inventariar el bloque solo cuando se transcriba cada expresión.
- **prueba.** None
- **pozos.** QF-084, QF-301, QF-147, QF-005, QF-306
- **consultas.** ninguna

### DOC-F36 · Método B y observador de E1

- **fenomeno.** Estimación sin sensor, no usada porque la hoja trae presión de sensor
- **expresion.** no transcrita
- **variables.** no entran
- **unidades.** no fijadas
- **origen.** src/analisis/catalogo_bes_jun.py, id F-36-F-40
- **fuente_cientifica.** Documento de ecuaciones del proyecto, fuera del alcance de esta hoja.
- **modulo.** src/analisis/catalogo_bes_jun.py
- **funcion.** None
- **notebooks.** no transcrito
- **dataset.** BES-jun
- **parametros.** faltan, según el catálogo
- **hipotesis.** No se aplica: hay presión de sensor.
- **dominio.** ninguno
- **verificacion_analitica.** No implementada.
- **oraculo.** no hay
- **verificacion_fisica.** No evaluable.
- **resultados.** Ninguno.
- **diferencias.** No sustituye a E-05.
- **tolerancia.** no aplica
- **estado_matematico.** solamente documentada
- **estado_fisico.** no evaluable con las fuentes usadas por el motor
- **estado_experimental.** no aplica
- **consecuencia_de_error.** Estimar PIP sin el sensor que la hoja sí trae.
- **reglas_dependientes.** Ninguna.
- **recomendacion_posterior.** No activarla en BES-jun.
- **prueba.** None
- **pozos.** ninguno
- **consultas.** ninguna

### DOC-F41 · Cadena del XLSM, incluido J64

- **fenomeno.** Otra planilla, con su propio signo de PIP
- **expresion.** no transcrita en BES-jun
- **variables.** no entran
- **unidades.** no fijadas aquí
- **origen.** src/analisis/catalogo_bes_jun.py, id F-41-J64
- **fuente_cientifica.** Otro libro. No es la celda G96.
- **modulo.** src/analisis/catalogo_bes_jun.py
- **funcion.** None
- **notebooks.** no transcrito
- **dataset.** BES-jun
- **parametros.** los de ese libro, no los de esta hoja
- **hipotesis.** No se mezcla con BES-jun.
- **dominio.** ninguno en este motor
- **verificacion_analitica.** No implementada.
- **oraculo.** no hay
- **verificacion_fisica.** No evaluable en este expediente.
- **resultados.** Ninguno.
- **diferencias.** No se copió el signo de J64 a G96.
- **tolerancia.** no aplica
- **estado_matematico.** solamente documentada
- **estado_fisico.** no evaluable con las fuentes usadas por el motor
- **estado_experimental.** no aplica
- **consecuencia_de_error.** Corregir G96 con el signo de otro libro.
- **reglas_dependientes.** Ninguna.
- **recomendacion_posterior.** Tratarla en su propio dataset si se abre.
- **prueba.** None
- **pozos.** ninguno
- **consultas.** CT-03

