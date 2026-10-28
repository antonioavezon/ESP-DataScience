# Matriz de ecuaciones · BES-jun

Fecha: 2026-10-20. Motor 0.4.2. Contrato 1.3.0. Las fórmulas de `src/modelo_deterministico/` no se modificaron. El recuento único está en `docs/catastro_maestro_formulas_BES-jun.md`: 20 ítems, 10 principales, 0 con validación externa suficiente, E-05 y E-07 con discrepancia identificada.

El dictamen científico no es el estado del software. Una fila puede reproducir la celda y, al mismo tiempo, quedar pendiente de medición o con una discrepancia física registrada.

| Ecuación | Verificación A | Verificación B | Verificación C | Resultado científico |
|---|---|---|---|---|
| E-01 | Conforme | Conforme | Conforme bajo hipótesis | Definición API reproducida. No hay densidad medida de este crudo. |
| E-02 | Conforme bajo hipótesis | Conforme | Pendiente de validación experimental | La celda se reproduce. Los coeficientes no tienen otra fuente. |
| E-03 | Conforme bajo hipótesis | Conforme | Pendiente de validación experimental | Mezcla lineal si BS&W es fracción. CT-02 abierta. |
| E-04 | Conforme bajo hipótesis | Conforme | Conforme bajo hipótesis | El factor 0.052 es el de la celda. El contraste SI da 0.051948 y no se sustituyó. |
| E-05 | Conforme | Conforme | Discrepancia detectada | La celda coincide con la caché. No coincide con la hidrostática simple. CT-03. |
| E-06 | Conforme | Conforme | Conforme bajo hipótesis | psi / (psi/ft) = ft. No hay otra medición de altura. |
| E-07 | Conforme bajo hipótesis | Conforme | Evidencia insuficiente | Los exponentes de la celda se cumplen. El PDF escribe 4.8655. CT-05. |
| E-08 | Conforme | Conforme | Conforme bajo hipótesis | La suma algebraica cierra. Hereda CT-03 y CT-05. |
| E-09 | Conforme bajo hipótesis | Conforme | Pendiente de validación experimental | Q ∝ f y H ∝ f²·etapas, con una razón ajena al dataset. CT-08. |
| E-10 | Conforme | Conforme | Pendiente de validación experimental | Interpolación lineal exacta en un caso analítico. La fricción usa el caudal medido. CT-06 y CT-09. |

## Comprobaciones

Tolerancia de las identidades algebraicas: `pytest.approx` (relativa 1e-6, absoluta 1e-12) salvo donde se indica. Archivo: `tests/test_verificacion_ecuaciones.py`. Las pruebas de caché siguen en `tests/test_fluidos_y_balance_bes_jun.py` y no sustituyen a estos tres métodos.

### E-01 · Gravedad específica

- Método A. Definición escrita: `141.5 / (131.5 + API)`. A 10 °API el denominador es 141.5 y el resultado es 1. Fuente de la celda: QF-554H, gravedad del petróleo a 60 °F. Dimensión: adimensional.
- Método B. Oráculo `_sg_api` en el test. `gravedad_especifica_api(12)` coincide con `141.5 / 143.5`.
- Método C. Al pasar de 12 °API a 40 °API la gravedad específica baja. No hay una densidad de laboratorio de estos pozos. Validación experimental: pendiente.
- Dictamen: conforme bajo la definición API. No es una medición del fluido.

### E-02 · Temperatura

- Método A. Celda B98: `sg_60 - 0.00066·(T-15.556) + 0.0000003·(T-15.556)²`. T en °C. Las tres constantes no aparecen definidas fuera de la celda.
- Método B. Oráculo `_sg_temperatura`. En 15.556 °C el resultado es el `sg_60` de entrada.
- Método C. La diferencia central de un grado alrededor de 15.556 °C da pendiente −0.00066, con tolerancia absoluta 1e-6. No hay ensayo que justifique los coeficientes. CT-04.
- Dictamen: conforme a la celda. Validación experimental pendiente.

### E-03 · Densidad de mezcla

- Método A. `8.33 · (BSW·ρ_agua/8.33 + (1-BSW)·sg_T)`, que es `BSW·ρ_agua + (1-BSW)·8.33·sg_T`. Unidad de salida: lb/gal. El rótulo de BS&W dice % y la fórmula no divide por 100.
- Método B. BSW = 0 da `8.33·sg`. BSW = 1 da la densidad del agua. El test no convierte un porcentaje.
- Método C. Con densidades positivas y BSW = 0.4, el resultado queda entre los dos componentes. No se declara mezcla real medida.
- Dictamen: conforme bajo la hipótesis de que el número de la celda ya es fracción. CT-02 abierta.

### E-04 · Gradiente

- Método A. `ρ_lb/gal · 0.052`. `8.34 · 0.052 = 0.43368` psi/ft. La hoja no usa `0.433/8.34`.
- Método B. `gradiente_psi_por_ft(8.34)` coincide con ese producto.
- Método C. Con 1 lb = 0.45359237 kg, 1 galón US = 3.785411784 L, g = 9.80665 m/s², 1 ft = 0.3048 m y 1 psi = 6894.757293168 Pa, el factor es 0.051948 (tolerancia absoluta 1e-5). La diferencia con 0.052 es menor que 0.0001 y no se absorbió en la fórmula. El código sigue devolviendo `ρ·0.052`, distinto del producto con el factor SI.
- Dictamen: conforme al factor de la celda. El redondeo frente al SI queda registrado. No es una validación de campo.

### E-05 · PIP

- Método A. Celda G96: `(P - (TVD_intake - TVD_sensor)·grad) / grad`. La caché de las cinco hojas coincide con `pip_en_ft` dentro de 1e-6 relativo.
- Método B. Oráculo `_pip_celda(800, 2500, 2600, 0.4)`.
- Método C. Oráculo hidrostático, aislado en el test y en `hipotesis_ct03.py`: `P/grad - (TVD_sensor - TVD_intake)`. Con el sensor 100 ft más profundo, la diferencia es 200 ft. En las cinco hojas el sensor está más profundo y la diferencia es `2·(TVD_sensor - TVD_intake)`:

| Pozo | Hoja | Diferencia celda − hidrostática |
|---|---|---:|
| QF-084 | QF-554H | 51.3 ft |
| QF-301 | QF-545H | 38.6 ft |
| QF-147 | QF-500H | 51.1 ft |
| QF-005 | QF-378HST | 41.2 ft |
| QF-306 | QF-549HST | 41.1 ft |

- El motor no llama a `hipotesis_ct03.py`. La fórmula original permanece.
- Dictamen: discrepancia detectada. CT-03. Reproducción informática: conforme.

### E-06 · THP en altura

- Método A. `THP_psi / gradiente`. Unidad: ft.
- Método B. 100 psi / 0.4 psi/ft = 250 ft.
- Método C. Duplicar la presión duplica la altura. Duplicar el gradiente la reduce a la mitad, con el gradiente fijo en el otro factor.
- Dictamen: conforme bajo la hipótesis del gradiente de E-04. Sin medición independiente de columna.

### E-07 · Fricción

- Método A. `(2.083·(100/C)^1.85·(Q/34.3)^1.85 / ID^4.8566)·(L/1000)`, C = 120, L = TVD de descarga. El PDF 004-ESPdesign escribe 4.8655. No se unificó.
- Método B. Oráculo `_hazen`. Doblar L duplica la pérdida. Doblar Q la multiplica por `2^1.85`. Doblar el diámetro la multiplica por `0.5^4.8566`.
- Método C. El mismo caso con exponente 4.8655 no coincide con la celda (`math.isclose` relativo 1e-6 falla). No hay pérdida de carga medida en estos pozos. No se cambió la longitud medida por la TVD ni al revés.
- Dictamen: conforme a la celda. Aplicabilidad al fluido: evidencia insuficiente. CT-05.

### E-08 · THD

- Método A. `TVD_descarga + fricción + THP_ft - PIP_ft`.
- Método B. `thd_total_ft(1000, 10, 20, 30) = 1000`.
- Método C. Un pie más de TVD, de fricción o de THP suma un pie. Un pie más de PIP resta un pie. Eso verifica el signo algebraico, no la física de cada término.
- Dictamen: conforme como identidad. La validez física queda condicionada a E-05, E-06 y E-07.

### E-09 · Afinidad

- Método A. `Q_i = Q60·f/f_curva` y `H_i = H60·(f/f_curva)²·etapas`.
- Método B. Razón 1.5 (90 Hz / 60 Hz), ajena a las cinco frecuencias del libro. Caudal × 1.5. Head × 2.25 × etapas. Volver con razón inversa y `1/etapas` recupera el punto.
- Método C. No hay curva de banco de estas bombas. CT-08 sigue condicionando el uso sobre los límites.
- Dictamen: conforme como álgebra de la hoja. Validación experimental pendiente.

### E-10 · Intersección

- Método A. MATCH descendente e interpolación `Q = Qk + (THD-Hk)/(Hk+1-Hk)·(Qk+1-Qk)`. Sin extrapolación.
- Método B. Puntos (0 BFPD, 100 ft) y (100 BFPD, 0 ft), 60 Hz, una etapa, THD = 50 ft. El oráculo `_interpolar` da 50 BFPD y `caudal_a_producir` también. THD = 150 ft y THD = −1 ft quedan `no_calculable`.
- Método C. `friccion(1000)` y `friccion(2000)` no son iguales: la THD de la hoja depende del caudal medido. Resolver la intersección con esa THD no es un punto fijo hidráulico. El cuaderno 04b explora un punto fijo y no está en el motor. No hay curva de fabricante (CT-06) ni tolerancia acordada entre Q* y el caudal medido (CT-09).
- Dictamen: conforme como interpolación de la tabla. No es predicción del caudal del pozo.

## Auxiliares ejecutadas

| Relación | Dónde | Qué se afirma | Qué no se afirma |
|---|---|---|---|
| Elasticidad central al 1 % | `sensibilidad_local.elasticidad_relativa` | Peso local de cada entrada sobre Q* | Incertidumbre o causalidad |
| Derivada por pie de TVD | `sensibilidad_local.derivada_por_pie` | BFPD por pie alrededor del punto de la hoja | Un límite operacional |
| Q(f) = Q(60)·f/60 | `candidatas_bes_jun.limites_a_frecuencia` | Misma relación que la hoja usa para llevar límites de 60 Hz | Que el límite sea de fabricante. CT-08 |
| Curvatura mínima del survey | `calidad.curvatura_minima` | Control de las columnas Vertical y Dogleg | Una ecuación de la BES |
| Interpolación de TVD por MD | `calidad.interpolar_tvd` | Lectura del survey | Sustituir la TVD escrita del equipo |
| Punto fijo de la intersección | `informes/cuadernos/nb04b.py` | Diferencia entre fricción con caudal medido e intersección reiterada | Algoritmo del motor |

Fuera del motor, y sin transcribir en esta pasada: potencia, motor y cable; el gradiente 0.433 del XLSM (F-02); el método B y el observador de E1.
